# memory.py — Memória persistente em SQLite
# Armazena histórico de conversas e recupera contexto para o LLM

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "memphis.db")
MAX_HISTORY = 20

class Memory:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                role      TEXT NOT NULL,
                content   TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def add_turn(self, user_text: str, assistant_text: str):
        now = datetime.now().isoformat()

        self.conn.executemany(
            "INSERT INTO conversations (role, content, timestamp) VALUES (?, ?, ?)",
            [
                ("user", user_text, now),
                ("assistant", assistant_text, now),
            ]
        )
        self.conn.commit()

    def get_history(self) -> list[dict]:
        cursor = self.conn.execute(
            """
            SELECT role, content FROM conversations
            ORDER BY id DESC LIMIT ?
            """,
            (MAX_HISTORY * 2,)
        )

        rows = cursor.fetchall()

        rows.reverse()
        return [{"role": r, "content": c} for r, c in rows]
    
    def clear(self):
        self.conn.execute("DELETE FROM conversations")
        self.conn.commit()

        print("[M] Memória limpa.")

    def stats(self):
        cursor = self.conn.execute("SELECT COUNT(*) FROM conversations")
        count = cursor.fetchone()[0]
        print(f"[M] Total de mensagens armazenadas: {count}")