import os
from google.adk.agents import Agent
from .database import add_task, get_tasks, add_note, get_notes
import httpx
import json
from .static_knowledge import get_emergency_wisdom

# --- PINECONE GROUNDED KNOWLEDGE LAYER ---
PINECONE_READY = False
try:
    from pinecone import Pinecone
    from pinecone_plugins.assistant.models.chat import Message
    pc_api_key = os.environ.get("PINECONE_API_KEY")
    if pc_api_key:
        pc_client = Pinecone(api_key=pc_api_key)
        pinecone_assistant = pc_client.assistant.Assistant(assistant_name="jts")
        PINECONE_READY = True
except Exception as e:
    print(f"Warning: Pinecone Grounded Retrieval Offline: {e}")

# --- RESILIENT MCP TOOLSET IMPORT ---
MCP_TOOLSET_AVAILABLE = False
try:
    from google.adk.tools import MCPToolset
    try:
        from google.adk.tools.mcp_tool.mcp_toolset import StreamableHTTPConnectionParams
    except ImportError:
        try:
            from google.adk.tools.mcp_tool.mcp_toolset import SseServerParams as StreamableHTTPConnectionParams
        except ImportError:
            StreamableHTTPConnectionParams = None
    if StreamableHTTPConnectionParams:
        MCP_TOOLSET_AVAILABLE = True
except ImportError:
    MCPToolset = None
    StreamableHTTPConnectionParams = None
    print("Warning: MCPToolset not available in this ADK version - schedule_agent will use direct tools.")

# --- NEURAL TOOLS ---

def generate_visualization(concept: str) -> str:
    """Generates a high-fidelity visual representation of a concept or object.
    
    Args:
        concept: The subject or concept to visualize.
    """
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "⚠️ Neural Visualization Layer Offline (Missing API Key)."
    
    try:
        # Use Tavily to find high-quality images for the concept
        with httpx.Client(timeout=10.0) as client:
            res = client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": api_key,
                    "query": f"high fidelity cinematic 4k illustration of {concept}",
                    "include_images": True,
                    "max_results": 1
                }
            )
            if res.status_code == 200:
                images = res.json().get("images", [])
                if images:
                    img_url = images[0]
                    return f"### [NEURAL VISUALIZATION: {concept}]\n![{concept}]({img_url})\n\n> *Image sourced from real-time neural search.*"
    except Exception as e:
        print(f"Visualization Failed: {e}")
    
    return "⚠️ Neural Visualization Encountered a Signal Error. Please try again."

# --- TASK TOOLS ---

def create_task(title: str, description: str = None, due_date: str = None) -> str:
    """Creates a new task in the personal task manager.
    
    Args:
        title: The task title.
        description: Optional details.
        due_date: Optional target completion date.
    """
    task_id = add_task(title, description, due_date)
    return f"✅ Task created successfully! (ID: {task_id})"

def list_tasks(status: str = None) -> str:
    """Lists all pending or completed tasks.
    
    Args:
        status: Filter by 'pending' or 'completed'.
    """
    tasks = get_tasks(status)
    if not tasks:
        return "You have no tasks in your list."
    
    res = "📋 **Your Tasks**\n"
    for t in tasks:
        icon = "⏳" if t['status'] == 'pending' else "✅"
        res += f"- {icon} **{t['title']}** (ID: {t['id']}): {t['description'] or 'No description'}\n"
    return res

def take_note(content: str) -> str:
    """Saves a personal note for future reference.
    
    Args:
        content: The text of the note.
    """
    note_id = add_note(content)
    return f"📄 Note saved! (ID: {note_id})"

def read_notes() -> str:
    """Retrieves all saved personal notes."""
    notes = get_notes()
    if not notes:
        return "No notes found."
    
    res = "💡 **Your Notes**\n"
    for n in notes:
        res += f"- [{n['timestamp']}] {n['content']}\n"
    return res

def query_knowledge_base(query: str) -> str:
    """Queries the verified project knowledge base for grounded information.
    Use this for any questions about Hack2Skill, Codelabs, Skills Labs, or project specific roadmaps.
    
    Args:
        query: The specific question or topic to search for in the documentation.
    """
    if not PINECONE_READY:
        return f"Warning: [Grounded Retrieval Offline] Falling back to Internal Logic:\n{get_emergency_wisdom(query)}"
    
    try:
        msg = Message(role="user", content=query)
        # We use the gpt-4o model integrated within the assistant by default
        resp = pinecone_assistant.chat(messages=[msg])
        content = resp["message"]["content"]
        return f"**[Source: Verified Project Documentation]**\n\n{content}"
    except Exception as e:
        return f"Warning: [Retrieval Error] Falling back to Internal Logic: {e}\n\n{get_emergency_wisdom(query)}"

# --- SUB-AGENTS ---

task_agent = Agent(
    name="task_agent",
    model=os.environ.get("MODEL", "gemini-1.5-flash"),
    description="Specialist for managing personal tasks and to-do lists.",
    instruction=(
        "You are a meticulous, helpful, and highly capable Task Manager. Your job is to help the user stay organized. "
        "Use create_task to add items and list_tasks to review them. Always confirm "
        "when a task is added and provide clear, engaging summaries."
    ),
    tools=[create_task, list_tasks]
)

info_agent = Agent(
    name="info_agent",
    model=os.environ.get("MODEL", "gemini-1.5-flash"),
    description="Specialist for note-taking and information retrieval.",
    instruction=(
        "You are a highly intelligent Knowledge Assistant. "
        "Help the user remember important details by using take_note and read_notes. "
        "Organise information logically, highlight key points, and maintain a friendly, conversational tone."
    ),
    tools=[take_note, read_notes]
)

# --- MCP CONNECTIVITY (RESILIENT) ---

def get_resilient_mcp_toolset():
    """Attempts to connect to MCP. Returns None if unavailable."""
    if not MCP_TOOLSET_AVAILABLE:
        return None
    import httpx
    primary_url = os.environ.get("MCP_SERVER_URL", "")
    fallback_url = os.environ.get("MCP_FALLBACK_URL", "http://localhost:10000/mcp/sse")
    
    # Only check external URLs (not localhost self-references during init)
    selected_url = fallback_url
    if primary_url and "localhost" not in primary_url:
        try:
            check_url = primary_url.replace("/sse", "")
            with httpx.Client(timeout=3.0) as client:
                res = client.get(check_url)
                if res.status_code == 200:
                    selected_url = primary_url
                else:
                    print(f"Warning: Primary MCP offline ({res.status_code}). Using fallback.")
        except Exception:
            print("Warning: Primary MCP unreachable. Using fallback.")
    
    print(f"MCP URL: {selected_url}")
    try:
        params = StreamableHTTPConnectionParams(url=selected_url)
        return MCPToolset(connection_params=params)
    except Exception as e:
        print(f"Warning: MCPToolset init failed: {e}")
        return None

def check_uptime_monitors() -> str:
    """Fetches the current status of all UptimeRobot monitors via the REST API.
    
    Returns a formatted summary of all monitors with their status, uptime ratios,
    and any recent incidents.
    """
    api_key = os.environ.get("UPTIMEROBOT_API_KEY")
    if not api_key:
        return "⚠️ Uptime Guard Offline: Missing UPTIMEROBOT_API_KEY in environment."
    
    try:
        with httpx.Client(timeout=10.0) as client:
            res = client.post(
                "https://api.uptimerobot.com/v2/getMonitors",
                data={
                    "api_key": api_key,
                    "format": "json",
                    "logs": "1",
                    "response_times": "0",
                    "custom_uptime_ratios": "7-30",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if res.status_code == 200:
                data = res.json()
                if data.get("stat") != "ok":
                    return f"⚠️ UptimeRobot API Error: {data.get('error', {}).get('message', 'Unknown error')}"
                
                monitors = data.get("monitors", [])
                if not monitors:
                    return "📡 No monitors configured in UptimeRobot."
                
                STATUS_MAP = {0: "🔇 Paused", 1: "⏳ Not checked", 2: "✅ Up", 8: "🔥 Seems down", 9: "🔴 Down"}
                result = "## 📡 Uptime Guard Report\n\n"
                for m in monitors:
                    status = STATUS_MAP.get(m.get("status", -1), "❓ Unknown")
                    ratios = m.get("custom_uptime_ratio", "N/A")
                    result += f"### {m['friendly_name']}\n"
                    result += f"- **Status**: {status}\n"
                    result += f"- **URL**: `{m.get('url', 'N/A')}`\n"
                    result += f"- **Uptime (7d / 30d)**: `{ratios}`\n\n"
                return result
            else:
                return f"⚠️ UptimeRobot API returned status {res.status_code}."
    except Exception as e:
        return f"⚠️ Uptime Guard Error: {e}"

mcp_toolset = get_resilient_mcp_toolset()

if mcp_toolset:
    schedule_agent_tools = [mcp_toolset]
else:
    # Fallback: schedule_agent uses the same calendar tools from mcp_server directly
    from .mcp_server import mcp as _mcp_instance
    schedule_agent_tools = []  # No tools — agent will respond conversationally

schedule_agent = Agent(
    name="schedule_agent",
    model=os.environ.get("MODEL", "gemini-1.5-flash"),
    description="Specialist for calendar management and event scheduling.",
    instruction=(
        "You are a highly organized Scheduling Assistant. Help the user track and plan events. "
        "If asked to schedule something, confirm the details and acknowledge the request."
    ),
    tools=schedule_agent_tools
)

career_agent = Agent(
    name="career_agent",
    model=os.environ.get("MODEL", "gemini-1.5-flash"),
    description="Specialist for career guidance, resume feedback, and skill suggestions based on verified project data.",
    instruction=(
        "You are the Career Strategist of Assistant AI. You provide highly personalized, insightful career guidance. "
        "PRIORITIZE using verified project documentation via query_knowledge_base for any questions about Hack2Skill, "
        "Google Skill Labs, Codelabs, or project timelines. If no grounded data is found or available, "
        "provide detailed, actionable critiques based on your professional logic."
    ),
    tools=[query_knowledge_base]
)

uptime_agent = Agent(
    name="uptime_agent",
    model=os.environ.get("MODEL", "gemini-1.5-flash"),
    description="Specialist for system monitoring, site health, and uptime alerts.",
    instruction=(
        "You are the Uptime Guard of Assistant AI. Use check_uptime_monitors to fetch the "
        "current status of all monitored services. Investigate downtime incidents, provide "
        "accurate uptime percentages, and give immediate troubleshooting steps for any incidents."
    ),
    tools=[check_uptime_monitors]
)

# --- ORCHESTRATOR ---

assistant_root = Agent(
    name="assistant_root",
    model=os.environ.get("MODEL", "gemini-1.5-flash"),
    description="Personal AI Assistant orchestrator with Grounded Knowledge Retrieval.",
    sub_agents=[task_agent, info_agent, schedule_agent, career_agent, uptime_agent],
    instruction="""
You are the **Assistant AI Orchestrator**. Your role is to coordinate specialized sub-agents while maintaining 100% UNBIASED and NEUTRAL status. 

### 🌟 Core Capabilities:
- **Grounded Verification Layer**: You have access to a verified project knowledge base via **career_agent**. Route any queries about competition rules, lab differences, or project roadmaps through this layer.
- **Cognitive Memory Layer**: You have a rolling 5-message context. Always reference previous conversation details when relevant.
- **Multimodal Neural Mapping**: You can analyze PDFs, Videos, and Images natively. For media queries, synthesize insights from file metadata and visual content.
- **Task Management**: Route task-specific queries to **task_agent**.
- **Information & Notes**: For knowledge and personal notes -> Route to **info_agent**.
- **Scheduling**: For event tracking -> Route to **schedule_agent**.
- **Career Growth**: For professional strategy -> Route to **career_agent**.
- **System Health (Uptime Guard)**: For monitor status or incidents -> Route to **uptime_agent**.
- **Visualization**: If the user needs an image or a visual concept illustration -> USE **generate_visualization**.

### 🗣️ Conversational Engine Protocol:
- You are a helpful, friendly, and highly intelligent personal assistant.
- Be fluid and natural in your conversations (e.g., respond warmly to greetings like 'hi').
- Do NOT sound like an encyclopedia or a generic robot. Have a premium, engaging personality.
- Provide objective, fact-based analysis for complex queries while maintaining a conversational tone.
- Avoid social, political, or personal bias.

### ✨ Response Style:
- Be **concise**, **professional**, and **premium**.
- Use **Markdown** (Images, Tables, Lists) and **Emojis**.
"""
    ,tools=[generate_visualization]
)
