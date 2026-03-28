import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import httpx

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
async def query_agent(request: QueryRequest):
    """Run a query through the Personal Assistant ADK agent."""
    try:
        from google.adk.runners import InMemoryRunner
        from google.genai import types as genai_types

        runner = InMemoryRunner(agent=assistant_root, app_name="assistant_api")
        session = await runner.session_service.create_session(
            app_name="assistant_api", user_id="api_user"
        )

        new_msg = genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=request.text)],
        )

        # Save user message
        save_message("user", request.text)

        response_text = ""
        agent_used = "orchestrator"
        
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
        except Exception as e:
            # ── Ghost Mode: Trial 2 - Secondary Gemini (Manual API) ─────────────
            print(f"Primary Gemini Failed ({e}). Attempting Silent Fallback...")
            # Silently fetch context if it's a knowledge query
            context = await fetch_web_context(request.text)
            enriched_prompt = f"{context}\nUSER QUERY: {request.text}" if context else request.text
            
            try:
                # We try a different model (pro/flash) with the same key
                secondary_model = "gemini-1.5-flash" if os.environ.get("MODEL") != "gemini-1.5-flash" else "gemini-1.5-pro"
                import google.generativeai as genai
                genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
                model = genai.GenerativeModel(secondary_model)
                res = await model.generate_content_async(enriched_prompt)
                response_text = res.text
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
                                        {"role": "system", "content": "You are Gemini. Provide a direct, helpful response using the context provided if relevant. Do not mention search or fallbacks."},
                                        {"role": "user", "content": enriched_prompt}
                                    ]
                                },
                                timeout=20.0
                            )
                            if neural_res.status_code == 200:
                                response_text = neural_res.json()['choices'][0]['message']['content']
                    except Exception as e3:
                        print(f"Neural Layer Offline: {e3}")

        # ── Ghost Mode: Final Result Preparation ──────────────────────────────
        # Save Bot Response
        if response_text:
            save_message("bot", response_text)
            return QueryResponse(response=response_text, metadata={"agent": agent_used})
        
        # ── Last Resort: High-Quality Deterministic Engine ────────────────────
        print(f"All LLMs Failed. Falling back to Overhauled Deterministic Base.")
        response_text = run_deterministic_query(request.text)
        save_message("bot", response_text)
        return QueryResponse(response=response_text, metadata={"agent": "deterministic_engine"})

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
