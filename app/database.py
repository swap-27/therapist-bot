import sqlite3
from pathlib import Path

DATABASE_PATH = Path("therapy.db")

class Database:
    def __init__(self):
        self.connection = sqlite3.connect(
            DATABASE_PATH,
            check_same_thread=False
        )
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.create_tables()

    def create_tables(self):

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                username TEXT UNIQUE NOT NULL,

                password_hash TEXT NOT NULL,

                display_name TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                role TEXT NOT NULL,

                content TEXT NOT NULL,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(user_id)
                REFERENCES users(id)

            )
        """)
        self.connection.commit()

    def create_user(self, username:str, password_hash:str, display_name:str) -> int | None:
        try:
            self.cursor.execute("""
                INSERT INTO users
                (username, password_hash, display_name)
                VALUES (?, ?, ?)
            """,
            (username, password_hash, display_name))
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        

    def get_user(self, username:str):

        self.cursor.execute("""
            SELECT *
            FROM users
            WHERE username = ?
        """,
        (username,)
        )

        return self.cursor.fetchone()
    
    def save_message(self, user_id, role, content):
        self.cursor.execute("""
            INSERT INTO messages
            (user_id, role, content)
            VALUES (?, ?, ?)
        """,
        (user_id, role, content)
        )
        self.connection.commit()

    def load_messages(self, user_id):
        self.cursor.execute("""
            SELECT role, content FROM messages
            WHERE user_id = ?
            ORDER BY id ASC
        """,
        (user_id,))
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()



db = Database()