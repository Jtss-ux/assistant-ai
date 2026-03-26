import os
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP - the modern, ergonomic API for MCP servers
mcp = FastMCP("Assistant-Tools")

# --- TOOLS ---

@mcp.tool()
async def schedule_event(event_name: str, time: str) -> str:
    """Schedules a new event in the calendar.
    
    Args:
        event_name: Name/Title of the event.
        time: Time string (e.g., '2026-03-27 15:00').
    """
    # In a real app, this would save to a database or Google Calendar API
    return f"📅 Event '{event_name}' successfully scheduled for {time}."

@mcp.tool()
async def check_calendar(date: str) -> str:
    """Checks the calendar for events on a specific date.
    
    Args:
        date: Date string (e.g., '2026-03-27').
    """
    # Simulation of calendar retrieval
    return f"🔍 Calendar for {date}: \n1. Team Sync @ 10:00 AM\n2. Project Review @ 2:00 PM"

# Note: FastMCP handles SSE and HTTP transports automatically.
# We will mount its sse_app in our main FastAPI application.
