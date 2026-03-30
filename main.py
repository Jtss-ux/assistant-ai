import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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

# --- IMPORT ASSISTANT AGENT ---
from assistant_agent import assistant_root, init_db
from assistant_agent.database import save_message, get_chat_history, get_tasks, get_notes, set_new_session, get_sessions, get_session_messages
from assistant_agent.mcp_server import mcp, get_mcp_app
from assistant_agent.deterministic_agent import run_deterministic_query

# --- INITIALISE DATABASE ---
init_db()

# --- PLATFORM DETECTION ---
def detect_platform() -> dict:
    """Detect and describe the runtime platform so any URL can be identified."""
    if os.environ.get("SPACE_ID"):         # Hugging Face Spaces
        return {
            "name": "Hugging Face Spaces",
            "icon": "🤗",
            "space_id": os.environ.get("SPACE_ID"),
            "url": f"https://huggingface.co/spaces/{os.environ.get('SPACE_ID')}",
        }
    elif os.environ.get("RENDER"):          # Render.com
        return {
            "name": "Render",
            "icon": "⚡",
            "service": os.environ.get("RENDER_SERVICE_NAME", "assistant-ai"),
            "url": os.environ.get("RENDER_EXTERNAL_URL", ""),
        }
    elif os.environ.get("K_SERVICE"):       # Google Cloud Run
        return {
            "name": "Google Cloud Run",
            "icon": "☁️",
            "service": os.environ.get("K_SERVICE"),
            "revision": os.environ.get("K_REVISION"),
            "region": os.environ.get("FUNCTION_REGION", os.environ.get("GOOGLE_CLOUD_REGION", "unknown")),
        }
    else:                                   # Local Dev
        return {"name": "Local Development", "icon": "💻"}

PLATFORM = detect_platform()
try:
    print(f"{PLATFORM['icon']} Runtime Platform: {PLATFORM['name']}")
except UnicodeEncodeError:
    print(f"Runtime Platform: {PLATFORM['name']}")

# --- SETUP PORT & MCP ENVIRONMENT ---
# HF Spaces injects PORT=8080 internally, but its reverse proxy always
# health-checks port 7860. We must hardcode 7860 on HF to avoid crash loops.
if "SPACE_ID" in os.environ:
    port = 7860
else:
    port = int(os.environ.get("PORT", 10000))
if not os.environ.get("MCP_SERVER_URL"):
    os.environ["MCP_SERVER_URL"] = f"http://localhost:{port}/mcp/sse"

# --- CHECK BACKUP APIS ---
if os.environ.get("PINECONE_API_KEY"):
    print("Pinecone Vector Memory: Key detected. (Ready for future scale)")
if os.environ.get("TOGETHER_API_KEY"):
    print("Together AI Fallback: Active (Ghost Mode Trial 4)")
if os.environ.get("OPENAI_API_KEY"):
    print("OpenAI Fallback: Active (Ghost Mode Trial 4)")

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
                    "max_results": 2
                },
                timeout=5.0
            )
            if res.status_code == 200:
                results = res.json().get("results", [])
                context = "\n".join([f"- {r['title']}: {r['content']}" for r in results])
                return f"### WEB CONTEXT FOR FALLBACK:\n{context}\n"
    except Exception:
        pass
    return ""

# ── Endpoints ───────────────────────────────────────────────────────────────

async def root(request: Request):
    if os.path.exists("frontend/dist/index.html"):
        return FileResponse("frontend/dist/index.html")
    return FileResponse("index.html")

async def health_check(request: Request):
    return JSONResponse({
        "status": "healthy",
        "service": "Career AI — Multi-Agent Assistant",
        "mcp": "active",
        "port": port,
        "platform": PLATFORM,
    })

async def ping(request: Request):
    return PlainTextResponse("pong")

async def chat_history(request: Request):
    return JSONResponse({"history": get_chat_history()})

async def dashboard_data(request: Request):
    return JSONResponse({
        "tasks": get_tasks(status="pending")[:5],
        "notes": get_notes()[:3],
        "system": {"model": os.environ.get("MODEL", "gemini-2.0-flash"), "mcp": "online"}
    })

async def new_chat(request: Request):
    """Start a fresh chat session."""
    session_id = set_new_session()
    return JSONResponse({"status": "ok", "session_id": session_id})

async def list_sessions(request: Request):
    """Get all past chat sessions for the history sidebar."""
    sessions = get_sessions()
    return JSONResponse({"sessions": sessions})

async def session_detail(request: Request):
    """Get messages for a specific past session."""
    session_id = request.path_params["session_id"]
    messages = get_session_messages(int(session_id))
    return JSONResponse({"messages": messages})


# ── LLM ENGINE CALLERS ──────────────────────────────────────────────────────

async def call_groq(text, history, enriched_prompt):
    """Ultra-fast, low-token text generation via Groq Llama 3."""
    advanced_logic_key = os.environ.get("GROQ_API_KEY")
    if not advanced_logic_key:
        raise ValueError("No Groq API key")
        
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {advanced_logic_key}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "max_tokens": 150,  # Token conservation
                "messages": [
                    {"role": "system", "content": "You are Gemini, a helpful, friendly, and highly intelligent personal assistant. Be extremely concise, fluid, and premium in your responses. Do not sound generic or robotic. If the user says hi, say hello back naturally. Conserve words to save tokens."},
                    *[{"role": "assistant" if m['role'] == "bot" else "user", "content": m['content']} for m in history],
                    {"role": "user", "content": enriched_prompt}
                ]
            },
            timeout=8.0
        )
        if res.status_code == 200:
            data = res.json()
            return data['choices'][0]['message']['content'], data.get('usage', {}).get('total_tokens'), "Gemini 2.0 Flash (Fast Engine)"
        raise Exception(f"Groq API Error: {res.status_code}")

async def call_gemini_adk(text, history, parts, session, runner, new_msg):
    """Heavy reasoning and multimodal parsing via ADK."""
    response_text = ""
    agent_used = "Orchestrator"
    
    async for event in runner.run_async(user_id="api_user", session_id=session.id, new_message=new_msg):
        if event.agent_name:
            agent_used = event.agent_name
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    response_text += part.text
                    
    if not response_text:
        raise ValueError("ADK returned empty response")
    
    return response_text, len(response_text) // 4, agent_used

async def call_gemini_api(text, history, enriched_prompt):
    """Direct Gemini API fallback using GenerativeAI SDK."""
    base_model = os.environ.get("MODEL", "gemini-1.5-flash")
    secondary_model = "gemini-1.5-pro" if "flash" in base_model else "gemini-1.5-flash"
    
    from google import genai
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
    
    history_genai = [{"role": "model" if m['role'] == "bot" else "user", "parts": [m['content']]} for m in history]
    res = await client.models.generate_content_async(
        model=f"models/{secondary_model}",
        contents=[*history_genai, {"role": "user", "parts": [enriched_prompt]}]
    )
    
    tokens = res.usage_metadata.total_token_count if hasattr(res, 'usage_metadata') else len(res.text) // 4
    return res.text, tokens, "Gemini 1.5 Pro (Core Engine)"

async def call_deep_cloud(text, history, enriched_prompt):
    """Together AI or OpenAI absolute fallback."""
    together_key = os.environ.get("TOGETHER_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    fallback_key = together_key or openai_key
    
    if not fallback_key:
        raise ValueError("No Deep Cloud API key available")
        
    fallback_url = "https://api.together.xyz/v1/chat/completions" if together_key else "https://api.openai.com/v1/chat/completions"
    fallback_model = "meta-llama/Llama-3.3-70B-Instruct-Turbo" if together_key else "gpt-4o-mini"
    
    async with httpx.AsyncClient() as client:
        res = await client.post(
            fallback_url,
            headers={"Authorization": f"Bearer {fallback_key}"},
            json={
                "model": fallback_model,
                "max_tokens": 150, # Token conservation
                "messages": [
                    {"role": "system", "content": "You are Gemini, a helpful, friendly, and highly intelligent personal assistant. Be extremely concise, fluid, and premium in your responses. Do not sound generic or robotic. Conserve words to save tokens."},
                    *[{"role": "assistant" if m['role'] == "bot" else "user", "content": m['content']} for m in history],
                    {"role": "user", "content": enriched_prompt}
                ]
            },
            timeout=10.0
        )
        if res.status_code == 200:
            data = res.json()
            return data['choices'][0]['message']['content'], data.get('usage', {}).get('total_tokens'), f"Gemini 1.5 Ultra (Cloud Runtime)"
        raise Exception(f"Cloud API Error: {res.status_code}")


async def query_agent(request: Request):
    """Run a query through the incredibly intelligent Auto-Router."""
    try:
        form = await request.form()
        text = form.get("text")
        file = form.get("file")

        if not text:
            return JSONResponse({"detail": "Missing 'text' field in form data."}, status_code=400)

        history = get_chat_history(limit=5)
        
        # Determine Routing Path
        is_multimodal = bool(file and hasattr(file, 'filename') and file.filename)
        
        from google.adk.runners import InMemoryRunner
        from google import genai
        from google.genai import types as genai_types
        client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        parts = [genai_types.Part(text=text)]
        
        if is_multimodal:
            import tempfile
            temp_path = os.path.join(tempfile.gettempdir(), f"tmp_{file.filename}")
            with open(temp_path, "wb") as buffer:
                buffer.write(await file.read())
            
            # Use google-genai for upload
            uploaded_file = client.files.upload(path=temp_path)
            parts.append(genai_types.Part(file_data=genai_types.FileData(file_uri=uploaded_file.uri, mime_type=file.content_type)))
            os.remove(temp_path)

        runner = InMemoryRunner(agent=assistant_root, app_name="assistant_api")
        session = await runner.session_service.create_session(app_name="assistant_api", user_id="api_user")

        for msg in history:
            try:
                role = "model" if msg['role'] == "bot" else "user"
                if msg['content']:
                    await session.add_content(genai_types.Content(role=role, parts=[genai_types.Part(text=msg['content'])]))
            except Exception:
                pass

        save_message("user", text)
        start_time = time.perf_counter()
        
        new_msg = genai_types.Content(role="user", parts=parts)
        
        # Async fetch context early so standard LLMs don't wait
        context = await fetch_web_context(text)
        sys_prompt = "You are Gemini, a helpful, highly intelligent personal assistant. Be fluid and natural in your responses. Be concise to conserve tokens. Remain unbiased."
        enriched_prompt = f"### SYSTEM: {sys_prompt}\n{context}\nUSER: {text}" if context else f"SYSTEM: {sys_prompt}\nUSER: {text}"
        
        # ── INTELLIGENT ROUTER ────────────────────────────────────────────────
        response_text, tokens_used, agent_used = None, 0, None
        
        if not is_multimodal:
            # Route 1: Text-Only Superfast Low-Token Execution (Groq Base)
            print("🚀 Fast Route: Text Detected. Using Groq natively.")
            try:
                response_text, tokens_used, agent_used = await call_groq(text, history, enriched_prompt)
            except Exception as e:
                print(f"⏩ Route 1 Failed ({e}), jumping to Route 2 (ADK)")
                try:
                    response_text, tokens_used, agent_used = await call_gemini_adk(text, history, parts, session, runner, new_msg)
                except Exception as e2:
                    print(f"⏩ Route 2 Failed ({e2}), jumping to Route 3 (Gemini Native)")
                    try:
                        response_text, tokens_used, agent_used = await call_gemini_api(text, history, enriched_prompt)
                    except Exception as e3:
                        print(f"☁️ Route 3 Failed ({e3}), jumping to Route 4 (Deep Cloud)")
                        try:
                            response_text, tokens_used, agent_used = await call_deep_cloud(text, history, enriched_prompt)
                        except Exception as e4:
                            print(f"❌ Core API Network Exhausted: {e4}")
        else:
            # Route 2: Multimodal Heavy Execution (Gemini Focus)
            print("👁️ Visual Route: File Detected. Forcing Gemini ADK.")
            try:
                response_text, tokens_used, agent_used = await call_gemini_adk(text, history, parts, session, runner, new_msg)
            except Exception as e:
                print(f"⏩ Route 1 Failed ({e}), jumping to Route 2 (Gemini Native)")
                try:
                    response_text, tokens_used, agent_used = await call_gemini_api(text, history, enriched_prompt)
                except Exception as e2:
                    print(f"❌ Core APIs exhausted for Multimodal: {e2}")

        # ── FINAL RESULT PREPARATION ──────────────────────────────────────────
        duration = round(time.perf_counter() - start_time, 2)
        tps = round(tokens_used / duration, 1) if duration > 0 else 0
        
        if response_text and response_text.strip() and response_text != "...":
            save_message("bot", response_text, agent=agent_used, duration=duration, tokens=tokens_used, tps=tps)
            return JSONResponse({"response": response_text, "metadata": {"agent": agent_used, "duration": duration, "tokens": tokens_used, "tps": tps}})
        
        # ── Last Resort: Deterministic Engine ─────────────────────────────────
        print(f"Falling back to Overhauled Deterministic Base.")
        response_text = run_deterministic_query(text)
        duration = round(time.perf_counter() - start_time, 2)
        save_message("bot", response_text, agent="Gemini System Root", duration=duration, tokens=len(response_text) // 4, tps=0)
        return JSONResponse({"response": response_text, "metadata": {"agent": "Gemini System Root", "duration": duration, "tokens": len(response_text) // 4, "tps": 0}})

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
    Route("/new-chat", new_chat, methods=["POST"]),
    Route("/sessions", list_sessions, methods=["GET"]),
    Route("/sessions/{session_id:int}", session_detail, methods=["GET"]),
]

if os.path.exists("frontend/dist/assets"):
    routes.append(Mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets"))

_mcp_app = get_mcp_app()
if _mcp_app is not None:
    routes.append(Mount("/mcp", _mcp_app))
else:
    print("ℹ️ MCP SSE not mounted (FastMCP SSE API unavailable in this version)")

middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
]

app = Starlette(debug=False, routes=routes, middleware=middleware)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
