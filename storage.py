import sqlite3


SCHEMA = """
CREATE TABLE IF NOT EXISTS cards (
    token TEXT PRIMARY KEY,
    encrypted_pan TEXT NOT NULL,
    masked_pan TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""


class CardStore:
    def __init__(self, path):
        self.path = path
        with self.connect() as connection:
            connection.execute(SCHEMA)

    def connect(self):
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def save(self, token, encrypted_pan, masked_pan):
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO cards(token, encrypted_pan, masked_pan) VALUES (?, ?, ?)",
                (token, encrypted_pan, masked_pan),
            )

    def get(self, token):
        with self.connect() as connection:
            return connection.execute(
                "SELECT token, encrypted_pan, masked_pan, created_at FROM cards WHERE token = ?",
                (token,),
            ).fetchone()

    def list_masked(self):
        with self.connect() as connection:
            return connection.execute(
                "SELECT token, masked_pan, created_at FROM cards ORDER BY created_at DESC"
            ).fetchall()
