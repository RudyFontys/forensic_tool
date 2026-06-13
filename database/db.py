import sqlite3


class Database:
    """Regelt de databaseverbinding en het beheer van servers en tabellen."""

    def __init__(self, db_name="forensic.db"):
        self.db_name = db_name

    def connect(self):
        """Maak een gewone SQLite-verbinding."""
        connection = sqlite3.connect(self.db_name)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def create_tables(self):
        """Maak de benodigde tabellen aan als ze nog niet bestaan."""
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

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                where_clause TEXT NOT NULL
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

    def get_server_names(self):
        """Geef alle servernamen alfabetisch terug."""
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("SELECT name FROM servers ORDER BY name")
        rows = cursor.fetchall()

        connection.close()
        return [row[0] for row in rows]

    def delete_server(self, server_name):
        """Verwijder een server en alle logregels die bij deze server horen."""
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id FROM servers WHERE name = ?",
            (server_name,)
        )
        row = cursor.fetchone()

        if row is None:
            connection.close()
            return 0

        server_id = row[0]

        cursor.execute(
            "DELETE FROM logs WHERE server_id = ?",
            (server_id,)
        )
        deleted_logs = cursor.rowcount

        cursor.execute(
            "DELETE FROM servers WHERE id = ?",
            (server_id,)
        )

        connection.commit()
        connection.close()
        return deleted_logs
