import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# --- IMPORT ASSISTANT AGENT ---
# We import from the package; this ensures all internal relative imports in the 
# assistant_agent package resolve correctly.
from assistant_agent import assistant_root, init_db
from assistant_agent.mcp_server import mcp  # This is the FastMCP instance
from assistant_agent.deterministic_agent import run_deterministic_query

# --- INITIALISE DATABASE ---
# Ensure database and tables exist at startup
init_db()

# --- SETUP MCP ENVIRONMENT ---
# FastMCP provides an sse_app that can be mounted into FastAPI/Starlette
app.mount("/mcp", mcp.sse_app())

# --- QUERY API ---
class QueryRequest(BaseModel):
    text: str

class QueryResponse(BaseModel):
    response: str

@app.get("/")
async def root():
    """Serve the modern Web UI."""
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

        response_text = ""
        try:
            async for event in runner.run_async(
                user_id="api_user",
                session_id=session.id,
                new_message=new_msg,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            response_text += part.text
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                print(f"Rate limited (429). Falling back to mock response.")
                response_text = run_deterministic_query(request.text)
                response_text = f"🛡️ **Local Resilience (Rate-Limited)**\n\n{response_text}"
            else:
                print(f"General Failure: {e}. Switching to Emergency Mode.")
                response_text = run_deterministic_query(request.text)
                response_text = f"🔥 **Emergency Mode (System Failure)**\n\n{response_text}"

        return QueryResponse(response=response_text or "No response generated.")

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
