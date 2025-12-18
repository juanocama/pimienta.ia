import sqlite3
import threading
from pathlib import Path
from typing import List, Optional


class SQLiteMemory:
    def __init__(self, db_path: str = None):
        if db_path is None:
            root = Path(__file__).resolve().parents[2]
            db_path = root / "data" / "memory.db"
        
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self._local = threading.local()
        self._initialize_db()
        self._migrate_if_needed()

    def _get_connection(self):
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )
        return self._local.conn

    def _initialize_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT,
                value TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

    def _migrate_if_needed(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(memory)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'timestamp' not in columns:
            print("[SQLite] Migrando base de datos: agregando columna timestamp...")
            cursor.execute("""
                ALTER TABLE memory 
                ADD COLUMN timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            """)
            conn.commit()
            print("[SQLite] Migración completada")

    def save(self, key: str, value: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO memory (key, value) VALUES (?, ?)",
            (key, value)
        )
        conn.commit()

    def get_by_key(self, key: str) -> Optional[List[str]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT value FROM memory WHERE key = ? ORDER BY id DESC",
            (key,)
        )
        results = cursor.fetchall()
        return [row[0] for row in results] if results else None

    def search(self, query: str) -> Optional[List[str]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT value FROM memory WHERE value LIKE ? ORDER BY id DESC",
            (f"%{query}%",)
        )
        results = cursor.fetchall()
        return [row[0] for row in results] if results else None

    def delete_by_key(self, key: str) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memory WHERE key = ?", (key,))
        conn.commit()
        return cursor.rowcount

    def clear_all(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memory")
        conn.commit()
