import os
import subprocess

from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/zoo_guide_agent/.env"))
load_dotenv()  # fallback for local dev

from google.adk.agents import Agent
from google.adk.tools import MCPToolset
from google.adk.tools.mcp_tool.mcp_toolset import StreamableHTTPConnectionParams
import google.auth.transport.requests
import google.oauth2.id_token

# ── MCP Server connectivity ──────────────────────────────────────────────────
raw_url = os.environ.get("MCP_SERVER_URL", "")
audience = raw_url.split("/mcp")[0] if "/mcp" in raw_url else raw_url

def _get_id_token() -> str:
    """Fetch a Google ID token for authenticated MCP calls."""
    try:
        req = google.auth.transport.requests.Request()
        return google.oauth2.id_token.fetch_id_token(req, audience)
    except Exception:
        pass
    try:
        return subprocess.check_output(
            ["gcloud", "auth", "print-identity-token"]
        ).decode().strip()
    except Exception:
        return ""

id_token = _get_id_token()

params = StreamableHTTPConnectionParams(
    url=raw_url,
    timeout=60.0,
    sse_read_timeout=300.0,
    headers={"Authorization": f"Bearer {id_token}"} if id_token else {},
)

mcp_toolset = MCPToolset(connection_params=params)

# ── Root Agent ───────────────────────────────────────────────────────────────
root_agent = Agent(
    name="zoo_guide",
    model=os.environ.get("MODEL", "gemini-1.5-flash-001"),
    description=(
        "An expert Zoo Tour Guide that answers visitor questions about animals "
        "using live zoo data from the MCP server."
    ),
    instruction=(
        "You are a friendly, knowledgeable Zoo Tour Guide for Cloud Creek Zoo. "
        "Use the MCP zoo-remote tools to look up animal locations, species info, "
        "and habitat details. Always combine zoo data with broader conservation "
        "context. Be engaging and educational."
    ),
    tools=[mcp_toolset],
)
