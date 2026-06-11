import sqlite3


class Database:
    """Regelt alleen de verbinding en de tabellen van de database."""

    def __init__(self, db_name="forensic.db"):
        self.db_name = db_name

    def connect(self):
        """Maak een gewone SQLite-verbinding."""
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        """Maak de tabellen aan als ze nog niet bestaan."""
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS servers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                datetime TEXT NOT NULL,
                server_id INTEGER NOT NULL,
                service TEXT,
                message TEXT,
                ip TEXT,
                FOREIGN KEY (server_id) REFERENCES servers(id)
            )
        """)

        connection.commit()
        connection.close()

    def get_or_create_server(self, cursor, server_name):
        """Geef het id van een server terug en maak de server zo nodig aan."""
        cursor.execute(
            "INSERT OR IGNORE INTO servers (name) VALUES (?)",
            (server_name,)
        )

        cursor.execute(
            "SELECT id FROM servers WHERE name = ?",
            (server_name,)
        )

        result = cursor.fetchone()
        return result[0]
