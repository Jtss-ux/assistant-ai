import os
import sqlite3
from typing import List, Optional, Union
from pydantic import BaseModel
from datetime import datetime

# --- DATABASE CONFIGURATION ---
DB_PATH = os.environ.get("DATABASE_PATH", "/tmp/assistant.db")
USE_SUPABASE = os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SERVICE_KEY")

if USE_SUPABASE:
    from supabase import create_client, Client
    supabase: Client = create_client(
        os.environ.get("SUPABASE_URL"), 
        os.environ.get("SUPABASE_SERVICE_KEY")
    )
else:
    supabase = None

class Task(BaseModel):
    id: Optional[Union[int, str]] = None
    title: str
    description: Optional[str] = None
    status: str = "pending"
    due_date: Optional[str] = None

class Note(BaseModel):
    id: Optional[Union[int, str]] = None
    content: str
    timestamp: str

def init_db():
    """Initializes local SQLite database only."""
    db_dir = os.path.dirname(os.path.abspath(DB_PATH))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            agent TEXT,
            duration REAL,
            tokens INTEGER,
            tps REAL,
            session_id INTEGER DEFAULT 1,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Migrate: add session_id if missing
    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN session_id INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            due_date TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_task(title: str, description: str = None, due_date: str = None) -> Union[int, str]:
    if USE_SUPABASE:
        data = {"title": title, "description": description, "status": "pending", "due_date": due_date}
        res = supabase.table("tasks").insert(data).execute()
        return res.data[0]['id'] if res.data else 0
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, description, due_date) VALUES (?, ?, ?)", (title, description, due_date))
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id

def get_tasks(status: str = None) -> List[dict]:
    if USE_SUPABASE:
        query = supabase.table("tasks").select("*")
        if status:
            query = query.eq("status", status)
        res = query.execute()
        return res.data

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT * FROM tasks WHERE status = ?", (status,))
    else:
        cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_note(content: str) -> Union[int, str]:
    if USE_SUPABASE:
        data = {"content": content}
        res = supabase.table("notes").insert(data).execute()
        return res.data[0]['id'] if res.data else 0

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
    note_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return note_id

def get_notes() -> List[dict]:
    if USE_SUPABASE:
        res = supabase.table("notes").select("*").order("created_at", desc=True).execute()
        return res.data

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Global session tracker
_current_session_id = None

def get_current_session_id():
    global _current_session_id
    if _current_session_id is not None:
        return _current_session_id
        
    if USE_SUPABASE:
        res = supabase.table("messages").select("session_id").order("session_id", desc=True).limit(1).execute()
        _current_session_id = res.data[0]['session_id'] if res.data else 1
    else:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(MAX(session_id), 1) FROM messages")
        _current_session_id = cursor.fetchone()[0]
        conn.close()
    return _current_session_id

def save_message(role: str, content: str, agent: str = None, duration: float = None, tokens: int = None, tps: float = None):
    session_id = get_current_session_id()
    if USE_SUPABASE:
        data = {
            "role": role, "content": content, "agent": agent, 
            "duration": duration, "tokens": tokens, "tps": tps, 
            "session_id": session_id
        }
        supabase.table("messages").insert(data).execute()
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (role, content, agent, duration, tokens, tps, session_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (role, content, agent, duration, tokens, tps, session_id)
    )
    conn.commit()
    conn.close()

def get_chat_history(limit: int = 50) -> List[dict]:
    if USE_SUPABASE:
        # Get max session_id first
        sid = get_current_session_id()
        res = supabase.table("messages").select("*").eq("session_id", sid).order("created_at", desc=False).limit(limit).execute()
        return res.data

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE session_id = (SELECT MAX(session_id) FROM messages) ORDER BY timestamp ASC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def clear_chat() -> int:
    if USE_SUPABASE:
        res = supabase.table("messages").select("session_id").order("session_id", desc=True).limit(1).execute()
        new_session = (res.data[0]['session_id'] if res.data else 0) + 1
        return new_session

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(MAX(session_id), 0) + 1 FROM messages")
    new_session = cursor.fetchone()[0]
    conn.close()
    return new_session
