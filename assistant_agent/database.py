import os
import sqlite3
from typing import List, Optional
from pydantic import BaseModel

# --- CONFIGURATION ---
DB_PATH = os.environ.get("DATABASE_PATH", "assistant.db")

# NOTE: On platforms like Render or Cloud Run, the local filesystem is ephemeral.
# To keep your data across restarts, you must mount a Persistent Disk
# and set DATABASE_PATH to a path on that disk (e.g., /app/data/assistant.db).

class Task(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    status: str = "pending"
    due_date: Optional[str] = None

class Note(BaseModel):
    id: Optional[int] = None
    content: str
    timestamp: str

def init_db():
    """Initializes the SQLite database. Ensures the parent directory exists."""
    db_dir = os.path.dirname(os.path.abspath(DB_PATH))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
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

def add_task(title: str, description: str = None, due_date: str = None) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description, due_date) VALUES (?, ?, ?)",
        (title, description, due_date)
    )
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id

def get_tasks(status: str = None) -> List[dict]:
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

def add_note(content: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
    note_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return note_id

def get_notes() -> List[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
