import os
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.requests import Request
from starlette.responses import JSONResponse, FileResponse, PlainTextResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
import json
import httpx
import time

load_dotenv()

# --- IMPORT ASSISTANT AGENT ---
# We import from the package; this ensures all internal relative imports in the 
# assistant_agent package resolve correctly.
from assistant_agent import assistant_root, init_db
from assistant_agent.database import save_message, get_chat_history, get_tasks, get_notes
from assistant_agent.mcp_server import mcp, get_mcp_app  # FastMCP instance + safe app getter
from assistant_agent.deterministic_agent import run_deterministic_query

# --- INITIALISE DATABASE ---
init_db()

# --- SETUP MCP ENVIRONMENT ---
port = int(os.environ.get("PORT", 10000))
if not os.environ.get("MCP_SERVER_URL"):
    os.environ["MCP_SERVER_URL"] = f"http://localhost:{port}/mcp/sse"

# --- CHECK BACKUP APIS ---
if os.environ.get("PINECONE_API_KEY"):
    print("🌲 Pinecone Vector Memory: Key detected. (Ready for future scale)")
if os.environ.get("TOGETHER_API_KEY"):
    print("☁️ Together AI Fallback: Active (Ghost Mode Trial 4)")
if os.environ.get("OPENAI_API_KEY"):
    print("☁️ OpenAI Fallback: Active (Ghost Mode Trial 4)")

# --- TAVILY WEB SEARCH ---
async def fetch_web_context(query: str) -> str:
    """Silently fetch web context using Tavily Search API for fallback LLMs."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return ""
    
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": api_key,
                    "query": query,
                    "search_depth": "basic",
                    "include_answer": False,
                    "max_results": 3
                },
                timeout=10.0
            )
            if res.status_code == 200:
                results = res.json().get("results", [])
                context = "\n".join([f"- {r['title']}: {r['content']}" for r in results])
                return f"### WEB CONTEXT FOR FALLBACK:\n{context}\n"
            elif res.status_code in [401, 403]:
                print("Silent Search: Unauthorized (Invalid Tavily Key). Skipping context.")
            elif res.status_code == 429:
                print("Silent Search: Rate limited. Skipping context.")
    except Exception as e:
        # Keep failures silent for production smoothness
        pass
    return ""

# ── Endpoints ───────────────────────────────────────────────────────────────

async def root(request: Request):
    """Serve the modern Cinematic React UI."""
    if os.path.exists("frontend/dist/index.html"):
        return FileResponse("frontend/dist/index.html")
    return FileResponse("index.html")

async def health_check(request: Request):
    """Robust health check for Render/Cloud Run deployments."""
    return JSONResponse({
        "status": "healthy", 
        "service": "assistant-ai-unified", 
        "mcp": "active",
        "port": port
    })

async def ping(request: Request):
    """Ultra-lightweight endpoint for Render keep-alive heartbeats."""
    return PlainTextResponse("pong")

async def chat_history(request: Request):
    """Retrieve persistent conversation history."""
    return JSONResponse({"history": get_chat_history()})

async def dashboard_data(request: Request):
    """Retrieve overview data for the side-panel."""
    return JSONResponse({
        "tasks": get_tasks(status="pending")[:5],
        "notes": get_notes()[:3],
        "system": {
            "model": os.environ.get("MODEL", "gemini-2.0-flash"),
            "mcp": "online"
        }
    })

async def query_agent(request: Request):
    """Run a query through the Personal Assistant ADK agent with Multimodal support."""
    try:
        # Starlette manual form parsing
        form = await request.form()
        text = form.get("text")
        file = form.get("file")

        if not text:
            return JSONResponse({"detail": "Missing 'text' field in form data."}, status_code=400)

        from google.adk.runners import InMemoryRunner
        from google.genai import types as genai_types
        import google.generativeai as raw_genai

        # ── Cognitive Memory Layer: Global History ──────────────────────────
        history = get_chat_history(limit=5)
        parts = [genai_types.Part(text=text)]
        
        # ── Multimodal Neural Mapping: File Upload ───────────────────────────
        if file and hasattr(file, 'filename') and file.filename:
            temp_path = f"tmp_{file.filename}"
            with open(temp_path, "wb") as buffer:
                buffer.write(await file.read())
            
            # Use raw GenAI to upload and get URI for ADK
            raw_genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
            uploaded_file = raw_genai.upload_file(temp_path)
            parts.append(genai_types.Part(file_data=genai_types.FileData(
                file_uri=uploaded_file.uri, 
                mime_type=file.content_type
            )))
            # Cleanup local temp
            os.remove(temp_path)

        runner = InMemoryRunner(agent=assistant_root, app_name="assistant_api")
        session = await runner.session_service.create_session(
            app_name="assistant_api", user_id="api_user"
        )

        for msg in history:
            try:
                role = "model" if msg['role'] == "bot" else "user"
                if msg['content']:
                    await session.add_content(
                        genai_types.Content(
                            role=role,
                            parts=[genai_types.Part(text=msg['content'])]
                        )
                    )
            except Exception as e_mem:
                print(f"Memory Sync Skip: {e_mem}")

        # Save user message immediately for persistence
        save_message("user", text)
        
        start_time = time.perf_counter()
        response_text = ""  # Must start empty so truthiness check works correctly
        agent_used = "Orchestrator" 
        tokens_used = 0
        
        new_msg = genai_types.Content(
            role="user",
            parts=parts,
        )
        
        # ── Ghost Mode: Trial 1 - Primary Gemini (ADK) ────────────────────────
        try:
            async for event in runner.run_async(
                user_id="api_user",
                session_id=session.id,
                new_message=new_msg,
            ):
                if event.agent_name:
                    agent_used = event.agent_name
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            response_text += part.text
            # Estimate tokens for ADK (approx 1 token per 4 chars)
            tokens_used = len(response_text) // 4
        except Exception as e:
            # ── Ghost Mode: Trial 2 - Secondary Gemini (Manual API) ─────────────
            response_text = ""  # Reset: partial data from failed Trial 1 is unusable
            print(f"Primary Gemini Failed ({e}). Attempting Silent Fallback...")
            # Silently fetch context if it's a knowledge query
            context = await fetch_web_context(text)
            
            # Fluid prompt engineering
            sys_prompt = "You are Assistant AI, a helpful, friendly, and highly intelligent personal assistant. Be fluid and natural in your responses (e.g. say hello back to greetings). Do not sound like a generic robot or an encyclopedia. Maintain an engaging personality while remaining unbiased."
            enriched_prompt = f"### SYSTEM: {sys_prompt}\n{context}\nUSER: {text}" if context else f"SYSTEM: {sys_prompt}\nUSER: {text}"
            
            # ── Ghost Mode: Trial 2 (Memory Aware) ───────────────────────────
            history_genai = []
            for m in history:
                role = "model" if m['role'] == "bot" else "user"
                history_genai.append({"role": role, "parts": [m['content']]})
            
            try:
                # We try a different model (pro/flash) with the same key
                base_model = os.environ.get("MODEL", "gemini-1.5-flash")
                secondary_model = "gemini-1.5-pro" if "flash" in base_model else "gemini-1.5-flash"
                
                # IMPORTANT: legacy google.generativeai requires 'models/' prefix
                legacy_model_name = f"models/{secondary_model}"
                
                import google.generativeai as genai
                genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
                model = genai.GenerativeModel(legacy_model_name)
                # Pass history as contents
                res = await model.generate_content_async([*history_genai, {"role": "user", "parts": [enriched_prompt]}])
                response_text = res.text
                if hasattr(res, 'usage_metadata'):
                    tokens_used = res.usage_metadata.total_token_count
                else:
                    tokens_used = len(response_text) // 4
            except Exception as e2:
                # ── Ghost Mode: Trial 3 - Gemini Neural Layer (Reserved) ──────────────
                advanced_logic_key = os.environ.get("GROQ_API_KEY")
                if advanced_logic_key:
                    print(f"Secondary Gemini Failed ({e2}). Attempting Neural Layer...")
                    try:
                        async with httpx.AsyncClient() as client:
                            neural_res = await client.post(
                                "https://api.groq.com/openai/v1/chat/completions",
                                headers={"Authorization": f"Bearer {advanced_logic_key}"},
                                json={
                                    "model": "llama-3.3-70b-versatile",
                                    "messages": [
                                        {"role": "system", "content": "You are Assistant AI, a helpful, friendly, and highly intelligent personal assistant. Be fluid, natural, and premium in your responses. Do not sound generic or robotic. If the user says hi, say hello back naturally. Maintain context and remain unbiased."},
                                        *[{"role": "assistant" if m['role'] == "bot" else "user", "content": m['content']} for m in history],
                                        {"role": "user", "content": enriched_prompt}
                                    ]
                                },
                                timeout=20.0
                            )
                            if neural_res.status_code == 200:
                                data = neural_res.json()
                                response_text = data['choices'][0]['message']['content']
                                tokens_used = data.get('usage', {}).get('total_tokens', len(response_text) // 4)
                    except Exception as e3:
                        print(f"Neural Layer Offline: {e3}")
                        
            # ── Ghost Mode: Trial 4 - Deep Cloud (Together AI / OpenAI) ─────────────
            if not response_text or not response_text.strip():
                together_key = os.environ.get("TOGETHER_API_KEY")
                openai_key = os.environ.get("OPENAI_API_KEY")
                
                fallback_key = together_key or openai_key
                fallback_url = "https://api.together.xyz/v1/chat/completions" if together_key else "https://api.openai.com/v1/chat/completions"
                fallback_model = "meta-llama/Llama-3.3-70B-Instruct-Turbo" if together_key else "gpt-4o-mini"
                
                if fallback_key:
                    print(f"Neural Layer Failed. Attempting Deep Cloud API ({fallback_model})...")
                    try:
                        async with httpx.AsyncClient() as client:
                            cloud_res = await client.post(
                                fallback_url,
                                headers={"Authorization": f"Bearer {fallback_key}"},
                                json={
                                    "model": fallback_model,
                                    "messages": [
                                        {"role": "system", "content": "You are Assistant AI, a helpful, friendly, and highly intelligent personal assistant. Be fluid, natural, and premium in your responses. Do not sound generic or robotic. If the user says hi, say hello back naturally. Maintain context and remain unbiased."},
                                        *[{"role": "assistant" if m['role'] == "bot" else "user", "content": m['content']} for m in history],
                                        {"role": "user", "content": enriched_prompt}
                                    ]
                                },
                                timeout=20.0
                            )
                            if cloud_res.status_code == 200:
                                data = cloud_res.json()
                                response_text = data['choices'][0]['message']['content']
                                tokens_used = data.get('usage', {}).get('total_tokens', len(response_text) // 4)
                    except Exception as e4:
                        print(f"Deep Cloud Offline: {e4}")

        # ── Ghost Mode: Final Result Preparation ──────────────────────────────
        duration = round(time.perf_counter() - start_time, 2)
        tps = round(tokens_used / duration, 1) if duration > 0 else 0
        
        # Save Bot Response only if we got real content from an LLM
        if response_text and response_text.strip() and response_text != "...":
            save_message(
                "bot", 
                response_text, 
                agent=agent_used, 
                duration=duration, 
                tokens=tokens_used, 
                tps=tps
            )
            return JSONResponse({
                "response": response_text, 
                "metadata": {
                    "agent": agent_used,
                    "duration": duration,
                    "tokens": tokens_used,
                    "tps": tps
                }
            })
        
        # ── Last Resort: High-Quality Deterministic Engine ────────────────────
        print(f"All LLMs Failed. Falling back to Overhauled Deterministic Base.")
        response_text = run_deterministic_query(text)
        duration = round(time.perf_counter() - start_time, 2)
        save_message(
            "bot", 
            response_text, 
            agent="deterministic_engine", 
            duration=duration, 
            tokens=len(response_text) // 4, 
            tps=0
        )
        return JSONResponse({
            "response": response_text, 
            "metadata": {
                "agent": "deterministic_engine",
                "duration": duration,
                "tokens": len(response_text) // 4,
                "tps": 0
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"detail": str(e)}, status_code=500)


# ── App Assembly ────────────────────────────────────────────────────────────

routes = [
    Route("/", root, methods=["GET", "HEAD"]),
    Route("/health", health_check, methods=["GET"]),
    Route("/ping", ping, methods=["GET"]),
    Route("/history", chat_history, methods=["GET"]),
    Route("/dashboard", dashboard_data, methods=["GET"]),
    Route("/query", query_agent, methods=["POST"]),
]

if os.path.exists("frontend/dist/assets"):
    routes.append(Mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets"))

_mcp_app = get_mcp_app()
if _mcp_app is not None:
    routes.append(Mount("/mcp", _mcp_app))
    print("✅ MCP SSE endpoint mounted at /mcp")
else:
    print("ℹ️ MCP SSE not mounted (FastMCP SSE API unavailable in this version)")

middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
]

app = Starlette(debug=False, routes=routes, middleware=middleware)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
