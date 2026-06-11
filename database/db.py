"""Beheer van de SQLite-database en het databaseschema."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class DatabaseManager:
    """Maakt databaseverbindingen en initialiseert het schema.

    Deze klasse is alleen verantwoordelijk voor technische databasezaken.
    De importlogica staat bewust in ``LogImporter``.
    """

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)

    def connect(self) -> sqlite3.Connection:
        """Open een SQLite-verbinding met foreign keys ingeschakeld."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """Lever een verbinding en voer commit of rollback automatisch uit."""
        connection = self.connect()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        """Maak de tabellen en indexen aan wanneer deze nog niet bestaan."""
        with self.transaction() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS servers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                );

                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    datetime TEXT NOT NULL,
                    server_id INTEGER NOT NULL,
                    service TEXT,
                    message TEXT,
                    ip TEXT,
                    FOREIGN KEY (server_id) REFERENCES servers(id)
                );

                CREATE INDEX IF NOT EXISTS idx_logs_datetime
                    ON logs(datetime);

                CREATE INDEX IF NOT EXISTS idx_logs_server_id
                    ON logs(server_id);

                CREATE INDEX IF NOT EXISTS idx_logs_ip
                    ON logs(ip);
                """
            )
