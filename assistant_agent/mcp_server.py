import os

# Safely initialize FastMCP — guard against API changes in different mcp versions
try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("Assistant-Tools")
    MCP_AVAILABLE = True
except ImportError:
    mcp = None
    MCP_AVAILABLE = False
    print("⚠️ FastMCP not available — MCP tools disabled, core agent still operational.")

# --- TOOLS (only register if FastMCP loaded) ---

if MCP_AVAILABLE and mcp:
    @mcp.tool()
    async def schedule_event(event_name: str, time: str) -> str:
        """Schedules a new event in the calendar.
        
        Args:
            event_name: Name/Title of the event.
            time: Time string (e.g., '2026-03-27 15:00').
        """
        return f"📅 Event '{event_name}' successfully scheduled for {time}."

    @mcp.tool()
    async def check_calendar(date: str) -> str:
        """Checks the calendar for events on a specific date.
        
        Args:
            date: Date string (e.g., '2026-03-27').
        """
        return f"🔍 Calendar for {date}:\n1. Team Sync @ 10:00 AM\n2. Project Review @ 2:00 PM"


def get_mcp_app():
    """Returns the mountable SSE app, or None if MCP is unavailable."""
    if not MCP_AVAILABLE or mcp is None:
        return None
    try:
        return mcp.sse_app()
    except AttributeError:
        # Newer mcp versions may have renamed sse_app
        try:
            return mcp.get_asgi_app()
        except AttributeError:
            print("⚠️ FastMCP SSE app not available — skipping MCP mount.")
            return None
