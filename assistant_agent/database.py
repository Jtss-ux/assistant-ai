import os
import sqlite3
from typing import List, Optional
from pydantic import BaseModel

# --- CONFIGURATION ---
DB_PATH = os.environ.get("DATABASE_PATH", "/tmp/assistant.db")

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
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
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

# Global session tracker
_current_session_id = None

def get_current_session_id():
    global _current_session_id
    if _current_session_id is None:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(MAX(session_id), 1) FROM messages")
        _current_session_id = cursor.fetchone()[0]
        conn.close()
    return _current_session_id

def set_new_session():
    global _current_session_id
    _current_session_id = clear_chat()
    return _current_session_id

def save_message(role: str, content: str, agent: str = None, duration: float = None, tokens: int = None, tps: float = None):
    session_id = get_current_session_id()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (role, content, agent, duration, tokens, tps, session_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (role, content, agent, duration, tokens, tps, session_id)
    )
    conn.commit()
    conn.close()

def get_chat_history(limit: int = 50) -> List[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE session_id = (SELECT MAX(session_id) FROM messages) ORDER BY timestamp ASC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def clear_chat() -> int:
    """Start a new session by incrementing the session counter."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(MAX(session_id), 0) + 1 FROM messages")
    new_session = cursor.fetchone()[0]
    conn.close()
    return new_session

def get_sessions() -> List[dict]:
    """Get a list of all chat sessions with their first message as preview."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT session_id,
               MIN(timestamp) as started,
               COUNT(*) as message_count,
               (SELECT content FROM messages m2 WHERE m2.session_id = m1.session_id AND m2.role = 'user' ORDER BY m2.timestamp ASC LIMIT 1) as preview
        FROM messages m1
        GROUP BY session_id
        ORDER BY MIN(timestamp) DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_session_messages(session_id: int) -> List[dict]:
    """Get all messages for a specific session."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
