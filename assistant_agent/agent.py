import os
import httpx
import json
from google.adk.agents import Agent
from .database import add_task, get_tasks, add_note, get_notes
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
    MCP_TOOLSET_AVAILABLE = False
    print("Warning: MCPToolset not available - schedule_agent will use conversational logic.")

# --- TOOLS ---

def generate_visualization(concept: str) -> str:
    """Generates a high-fidelity visual representation of a concept or object."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "⚠️ Neural Visualization Layer Offline (Missing API Key)."
    try:
        with httpx.Client(timeout=10.0) as client:
            res = client.post("https://api.tavily.com/search", json={
                "api_key": api_key,
                "query": f"high fidelity cinematic 4k illustration of {concept}",
                "include_images": True,
                "max_results": 1
            })
            if res.status_code == 200:
                images = res.json().get("images", [])
                if images: return f"### [NEURAL VISUALIZATION: {concept}]\n![{concept}]({images[0]})\n\n> *Image sourced from real-time neural search.*"
    except Exception as e:
        print(f"Visualization Failed: {e}")
    return "⚠️ Gemini Pro Vision (Creative): Neural Visualization Signal Error."

def create_task_tool(title: str, description: str = None, due_date: str = None) -> str:
    """Creates a new task in the personal task manager."""
    task_id = add_task(title, description, due_date)
    return f"✅ Task created successfully! (ID: {task_id})"

def list_tasks_tool(status: str = None) -> str:
    """Lists all pending or completed tasks."""
    tasks = get_tasks(status)
    if not tasks: return "You have no tasks in your list."
    res = "📋 **Your Tasks**\n"
    for t in tasks:
        icon = "⏳" if t['status'] == 'pending' else "✅"
        res += f"- {icon} **{t['title']}** (ID: {t['id']}): {t['description'] or ''}\n"
    return res

def take_note_tool(content: str) -> str:
    """Saves a personal note for future reference."""
    note_id = add_note(content)
    return f"📄 Note saved! (ID: {note_id})"

def read_notes_tool() -> str:
    """Retrieves all saved personal notes."""
    notes = get_notes()
    if not notes: return "No notes found."
    res = "💡 **Your Notes**\n"
    for n in notes: res += f"- [{n['timestamp']}] {n['content']}\n"
    return res

def query_knowledge_base(query: str) -> str:
    """Queries the verified project knowledge base for grounded information (Hack2Skill, Codelabs, etc)."""
    if not PINECONE_READY: return f"Warning: [Retrieval Offline] Falling back to Internal Logic:\n{get_emergency_wisdom(query)}"
    try:
        msg = Message(role="user", content=query)
        resp = pinecone_assistant.chat(messages=[msg])
        return f"**[Source: Verified Project Documentation]**\n\n{resp['message']['content']}"
    except Exception as e:
        return f"Warning: [Retrieval Error] Falling back: {e}\n\n{get_emergency_wisdom(query)}"

def parse_complex_file(file_path: str, file_type: str) -> str:
    """Extracts raw content from complex file types like SQL or Excel for text-based analysis.
    
    Args:
        file_path: The absolute path to the file.
        file_type: 'sql' or 'excel'.
    """
    try:
        if file_type == 'sql':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(5000) # Preview first 5k chars
                return f"### [SQL SCHEMA/DATA PREVIEW]\n```sql\n{content}\n```"
        elif file_type == 'excel':
            import pandas as pd
            df = pd.read_excel(file_path).head(10) # Preview first 10 rows
            return f"### [EXCEL DATA PREVIEW]\n\n{df.to_markdown()}"
    except Exception as e:
        return f"⚠️ Multimodal Parsing Error: {e}"
    return "Unsupported file type for neural extraction."

def check_uptime_monitors() -> str:
    """Fetches the current status of all UptimeRobot monitors."""
    api_key = os.environ.get("UPTIMEROBOT_API_KEY")
    if not api_key: return "⚠️ Uptime Guard Offline: Missing API Key."
    try:
        with httpx.Client(timeout=10.0) as client:
            res = client.post("https://api.uptimerobot.com/v2/getMonitors", data={"api_key": api_key, "format": "json", "logs": "1"}, headers={"Content-Type": "application/x-www-form-urlencoded"})
            if res.status_code == 200:
                monitors = res.json().get("monitors", [])
                if not monitors: return "📡 No monitors configured."
                STATUS_MAP = {2: "✅ Up", 8: "🔥 Seems down", 9: "🔴 Down"}
                result = "## 📡 Uptime Guard Report\n\n"
                for m in monitors:
                    result += f"### {m['friendly_name']}\n- **Status**: {STATUS_MAP.get(m['status'], '❓ Unknown')}\n- **Uptime**: `{m.get('custom_uptime_ratio', 'N/A')}`\n\n"
                return result
    except Exception as e: return f"⚠️ Uptime Guard Error: {e}"
    return "⚠️ Uptime Guard Error: API returned failure."

# --- SUB-AGENTS ---

task_agent = Agent(
    name="task_agent",
    model=os.environ.get("MODEL", "gemini-1.5-flash"),
    description="Specialist for managing personal tasks and to-do lists.",
    instruction="Handle user tasks meticulously. You are 100% UNBIASED. Avoid '-' or ';' in chat.",
    tools=[create_task_tool, list_tasks_tool]
)

info_agent = Agent(
    name="info_agent",
    model=os.environ.get("MODEL", "gemini-1.5-flash"),
    description="Specialist for note-taking and information retrieval.",
    instruction="Help the user remember important details. Be detailed and unbiased.",
    tools=[take_note_tool, read_notes_tool]
)

career_agent = Agent(
    name="career_agent",
    model=os.environ.get("MODEL", "gemini-1.5-flash"),
    description="Specialist for career guidance and skill suggestions using grounded data.",
    instruction="Provide insightful career strategy. PRIORITIZE query_knowledge_base for project-specific info.",
    tools=[query_knowledge_base]
)

uptime_agent = Agent(
    name="uptime_agent",
    model=os.environ.get("MODEL", "gemini-1.5-flash"),
    description="Specialist for system monitoring and site health.",
    instruction="Protect the uptime. Use check_uptime_monitors for real-time status.",
    tools=[check_uptime_monitors]
)

# --- ORCHESTRATOR ---

assistant_root = Agent(
    name="assistant_root",
    model=os.environ.get("MODEL", "gemini-1.5-flash"),
    description="Personal AI Assistant orchestrator with Grounded Knowledge Retrieval.",
    sub_agents=[task_agent, info_agent, career_agent, uptime_agent],
    instruction="""
You are the **Assistant AI Orchestrator**. Your role is to coordinate specialized sub-agents while maintaining 100% UNBIASED status. 

### 🎯 Conversational Engine Protocol (Strict):
- **ALWAYS PROVIDE DIRECT, CONCISE, AND OBJECTIVE ANSWERS BY DEFAULT.**
- Only provide in-depth details or comprehensive explanations if the user explicitly requests 'depth', 'show your work', or 'in detail'.
- Avoid using '-' or ';' in your responses unless strictly necessary for code snippets or technical lists.
- You prioritize efficiency over verbosity.

### 🌟 Core Capabilities:
- **Grounded Verification Layer**: Route project queries (Hack2Skill, Codelabs) through **career_agent**.
- **Multimodal Neural Mapping**: You analyze PDFs, Videos, Images, SQL, and Excel natively.
- **Task Management**: Route to **task_agent**.
- **Information & Notes**: Route to **info_agent**.
- **System Health**: Route to **uptime_agent**.
- **Visualization**: Use **generate_visualization** for concept illustrations.

### 🗣️ Formatting Protocol:
- Use Markdown (Tables, Lists with Emojis) to enhance the "Liquid Glass" UI.
- Maintain a premium, professional, yet natural tone.
"""
    ,tools=[generate_visualization, parse_complex_file]
)
