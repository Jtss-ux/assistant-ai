# Deterministic Fallback Engine
# Performs basic task and career logic without an LLM.

from .database import add_task, get_tasks
from .static_knowledge import get_emergency_wisdom

def run_deterministic_query(query: str):
    query = query.lower()
    
    if "list tasks" in query or "show tasks" in query:
        tasks = get_tasks() # Returns a list of dictionaries
        if not tasks:
            return "📋 **Local Mode**: Your task list is currently empty."
        # Fixed: Use dictionary keys instead of tuple indices
        task_str = "\n".join([f"- {t['title']} (ID: {t['id']})" for t in tasks])
        return f"📋 **Local Mode**: Your Current Tasks:\n{task_str}"
        
    if "add task" in query or "create task" in query:
        # Simple extraction for demo purposes
        parts = query.split("add task")
        if len(parts) < 2:
            parts = query.split("create task")
        
        task_name = parts[-1].strip() or "New Offline Task"
        add_task(task_name) # Call correct add_task signature
        return f"✅ **Local Mode**: Task '{task_name}' added successfully to your local database."
        
    # Career Fallback
    wisdom = get_emergency_wisdom(query)
    return (
        f"⚠️ **Emergency Mode (Offline)**: I'm currently operating without cloud AI. "
        f"However, I can still help you with tasks and local knowledge.\n\n"
        f"{wisdom}\n\n"
        f"*Full AI orchestration will resume once service is restored.*"
    )
