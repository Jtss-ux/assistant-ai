import os
from google.adk.agents import Agent
from google.adk.tools import MCPToolset
from google.adk.tools.mcp_tool.mcp_toolset import StreamableHTTPConnectionParams
from .database import add_task, get_tasks, add_note, get_notes
from .career_tools import suggest_skills, suggest_projects, resume_feedback, career_path_guide

# --- TOOLS ---

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

# --- SUB-AGENTS ---

task_agent = Agent(
    name="task_agent",
    model=os.environ.get("MODEL", "gemini-1.5-flash"),
    description="Specialist for managing personal tasks and to-do lists.",
    instruction=(
        "You are a meticulous Task Manager. Your job is to help the user stay organized. "
        "Use create_task to add items and list_tasks to review them. Always confirm "
        "when a task is added and provide clear summaries."
    ),
    tools=[create_task, list_tasks]
)

info_agent = Agent(
    name="info_agent",
    model=os.environ.get("MODEL", "gemini-1.5-flash"),
    description="Specialist for note-taking and information retrieval.",
    instruction=(
        "You are a Knowledge Assistant. Help the user remember important details by "
        "using take_note and read_notes. Organise information logically and highlight key points."
    ),
    tools=[take_note, read_notes]
)

# --- MCP CONNECTIVITY ---

mcp_url = os.environ.get("MCP_SERVER_URL", "http://localhost:8000/mcp/")
params = StreamableHTTPConnectionParams(url=mcp_url)
mcp_toolset = MCPToolset(connection_params=params)

schedule_agent = Agent(
    name="schedule_agent",
    model=os.environ.get("MODEL", "gemini-1.5-flash"),
    description="Specialist for calendar management and event scheduling.",
    instruction=(
        "You are a highly organized Scheduling Assistant. Use the MCP calendar tools "
        "to manage the user's schedule. Always check for conflicts and confirm event details."
    ),
    tools=[mcp_toolset]
)

career_agent = Agent(
    name="career_agent",
    model=os.environ.get("MODEL", "gemini-1.5-flash"),
    description="Specialist for career guidance, resume feedback, and skill suggestions.",
    instruction=(
        "You are the Career Strategist of Assistant AI. Help the user optimize their "
        "professional path using suggest_skills, suggest_projects, resume_feedback, and career_path_guide. "
        "Provide insightful, high-level feedback and structured roadmaps."
    ),
    tools=[suggest_skills, suggest_projects, resume_feedback, career_path_guide]
)

# --- ORCHESTRATOR ---

assistant_root = Agent(
    name="assistant_root",
    model=os.environ.get("MODEL", "gemini-1.5-flash"),
    description="Personal AI Assistant orchestrator for tasks, schedules, and information.",
    sub_agents=[task_agent, info_agent, schedule_agent, career_agent],
    instruction="""
You are the **Personal Multi-Agent Assistant**. Your role is to coordinate specialist sub-agents to help the user manage their life and career.

**Routing Logic**:
- For creating/listing tasks → Route to **task_agent**.
- For taking notes or retrieving info → Route to **info_agent**.
- For scheduling events or checking calendar → Route to **schedule_agent**.
- For career advice, resumes, or skill suggestions → Route to **career_agent**.
- For hybrid requests (e.g., 'Add learning Docker to my tasks and suggest a project for it') → Orchestrate both **task_agent** and **career_agent**.

**Response Style**:
1. Be **concise** but **helpful**.
2. Use **Markdown** for beautiful formatting.
3. Use **Emojis** (📋, 📅, 💡, 🏅, 🏗️) to make the UI look premium.
4. At the end of every interaction, suggest a relevant next step.
"""
)
