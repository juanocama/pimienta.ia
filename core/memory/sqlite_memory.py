import sqlite3
from pathlib import Path
from core.memory.base import Memory

class SQLiteMemory(Memory):
    def __init__(self, db_path: str = None):
        root = Path(__file__).resolve().parents[2]
        db_path = root / "data" / "memory.db"

        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT,
                value TEXT
            )
        """)
        self.conn.commit()

    def save(self, key: str, value: str) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO memory (key, value) VALUES (?, ?)",
            (key, value)
        )
        self.conn.commit()

    def search(self, query: str) -> list[str]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT value FROM memory WHERE value LIKE ?",
            (f"%{query}%",)
        )
        return [row[0] for row in cursor.fetchall()]

    def get_by_key(self, key: str) -> list[str]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT value FROM memory WHERE key = ?",
            (key,)
        )
        return [row[0] for row in cursor.fetchall()]
