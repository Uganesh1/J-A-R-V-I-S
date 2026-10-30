import sqlite3
import json
from datetime import datetime

class MemoryManager:
    def __init__(self, db_path="jarvis_memory.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT, content TEXT, ts TEXT
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                key TEXT PRIMARY KEY, value TEXT, ts TEXT
            )
        """)
        self.conn.commit()

    def log_conversation(self, role, content):
        self.conn.execute(
            "INSERT INTO conversations (role, content, ts) VALUES (?,?,?)",
            (role, content, datetime.now().isoformat())
        )
        self.conn.commit()

    def get_recent_context(self, limit=6):
        rows = self.conn.execute(
            "SELECT role, content FROM conversations ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [{"role": r, "content": c} for r, c in reversed(rows)]

    def remember(self, key, value):
        self.conn.execute(
            "INSERT OR REPLACE INTO memories (key, value, ts) VALUES (?,?,?)",
            (key, value, datetime.now().isoformat())
        )
        self.conn.commit()

    def recall(self, key):
        row = self.conn.execute("SELECT value FROM memories WHERE key=?", (key,)).fetchone()
        return row[0] if row else None