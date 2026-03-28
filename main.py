import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Form, File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import httpx
import time

load_dotenv()

# --- IMPORT ASSISTANT AGENT ---
# We import from the package; this ensures all internal relative imports in the 
# assistant_agent package resolve correctly.
from assistant_agent import assistant_root, init_db
from assistant_agent.database import save_message, get_chat_history, get_tasks, get_notes
from assistant_agent.mcp_server import mcp  # This is the FastMCP instance
from assistant_agent.deterministic_agent import run_deterministic_query

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
    except Exception as e:
        print(f"Silent Search Failed: {e}")
    return ""

# --- INITIALISE DATABASE ---
# Ensure database and tables exist at startup
init_db()

# --- SETUP MCP ENVIRONMENT ---
port = int(os.environ.get("PORT", 8080))
if not os.environ.get("MCP_SERVER_URL"):
    # With FastMCP mounted at /mcp, the SSE endpoint is /mcp/sse
    os.environ["MCP_SERVER_URL"] = f"http://localhost:{port}/mcp/sse"

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Multi-Agent Personal Assistant API",
    description="ADK-powered Assistant with Database storage and FastMCP integration.",
    version="1.2.5",
)

# --- MIDDLEWARE ---
# Enable CORS for browser-side interactions in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MOUNT FRONTEND ---
# Mount the React assets directory
if os.path.exists("frontend/dist/assets"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

# FastMCP provides an sse_app that can be mounted into FastAPI/Starlette
app.mount("/mcp", mcp.sse_app())

# --- QUERY API ---
class QueryRequest(BaseModel):
    text: str

class QueryResponse(BaseModel):
    response: str
    metadata: dict = {}

@app.get("/")
@app.head("/")
async def root():
    """Serve the modern Cinematic React UI."""
    if os.path.exists("frontend/dist/index.html"):
        return FileResponse("frontend/dist/index.html")
    return FileResponse("index.html")

@app.get("/health")
async def health_check():
    """Robust health check for Render/Cloud Run deployments."""
    return {
        "status": "healthy", 
        "service": "assistant-ai-unified", 
        "mcp": "active",
        "port": port
    }

@app.get("/ping")
async def ping():
    """Ultra-lightweight endpoint for Render keep-alive heartbeats."""
    return "pong"

@app.get("/history")
async def chat_history():
    """Retrieve persistent conversation history."""
    return {"history": get_chat_history()}

@app.get("/dashboard")
async def dashboard_data():
    """Retrieve overview data for the side-panel."""
    return {
        "tasks": get_tasks(status="pending")[:5],
        "notes": get_notes()[:3],
        "system": {
            "model": os.environ.get("MODEL", "gemini-2.0-flash"),
            "mcp": "online"
        }
    }

@app.post("/query", response_model=QueryResponse)
async def query_agent(
    text: str = Form(...),
    file: UploadFile = File(None)
):
    """Run a query through the Personal Assistant ADK agent with Multimodal support."""
    try:
        from google.adk.runners import InMemoryRunner
        from google.genai import types as genai_types
        import google.generativeai as raw_genai

        # ── Cognitive Memory Layer: Global History ──────────────────────────
        # Reduce limit for better stability on start
        history = get_chat_history(limit=5)
        parts = [genai_types.Part(text=text)]
        
        # ── Multimodal Neural Mapping: File Upload ───────────────────────────
        if file:
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
        response_text = "..." # Initial fallback text
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
            print(f"Primary Gemini Failed ({e}). Attempting Silent Fallback...")
            # Silently fetch context if it's a knowledge query
            context = await fetch_web_context(text)
            enriched_prompt = f"### SYSTEM: Provide an OBJECTIVE and UNBIASED analysis.\n{context}\nUSER QUERY: {text}" if context else f"SYSTEM: Objective analysis required.\nQUERY: {text}"
            
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
                                        {"role": "system", "content": "You are Gemini, an OBJECTIVE and UNBIASED Neural Layer. Provide a direct, fact-based response using the context provided. Do not show bias. Mainatain context from previous conversation."},
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

        # ── Ghost Mode: Final Result Preparation ──────────────────────────────
        duration = round(time.perf_counter() - start_time, 2)
        tps = round(tokens_used / duration, 1) if duration > 0 else 0
        
        # Save Bot Response
        if response_text:
            save_message(
                "bot", 
                response_text, 
                agent=agent_used, 
                duration=duration, 
                tokens=tokens_used, 
                tps=tps
            )
            return QueryResponse(
                response=response_text, 
                metadata={
                    "agent": agent_used,
                    "duration": duration,
                    "tokens": tokens_used,
                    "tps": tps
                }
            )
        
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
        return QueryResponse(
            response=response_text, 
            metadata={
                "agent": "deterministic_engine",
                "duration": duration,
                "tokens": len(response_text) // 4,
                "tps": 0
            }
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
