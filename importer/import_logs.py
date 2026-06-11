"""Importservice voor syslogbestanden."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from database.db import DatabaseManager
from database.models import ImportResult
from ip.ip_checker import IpChecker
from parser.syslog_parser import SyslogParser


class LogImporter:
    """Coördineert het parseren en opslaan van een syslogbestand.

    De afhankelijkheden worden via de constructor aangeleverd. Daardoor kan de
    importservice eenvoudig met een tijdelijke database en echte of vervangende
    componenten worden getest.
    """

    def __init__(
        self,
        database: DatabaseManager,
        parser: SyslogParser,
        ip_checker: IpChecker,
    ) -> None:
        self.database = database
        self.parser = parser
        self.ip_checker = ip_checker

    def import_file(
        self,
        filepath: str | Path,
        server_name: str | None = None,
    ) -> ImportResult:
        """Importeer een bestand en geef de aantallen terug.

        Een ingevulde ``server_name`` overschrijft de servernaam uit alle
        regels. Lege regels worden overgeslagen en onbekende regels worden als
        mislukt geteld.
        """
        log_path = Path(filepath)
        if not log_path.is_file():
            raise FileNotFoundError(f"Syslogbestand niet gevonden: {log_path}")

        override = server_name.strip() if server_name and server_name.strip() else None
        imported_count = 0
        failed_count = 0
        skipped_empty_count = 0
        failed_line_numbers: list[int] = []
        server_cache: dict[str, int] = {}

        with self.database.transaction() as connection:
            cursor = connection.cursor()

            with log_path.open("r", encoding="utf-8", errors="replace") as log_file:
                for line_number, line in enumerate(log_file, start=1):
                    if not line.strip():
                        skipped_empty_count += 1
                        continue

                    parsed = self.parser.parse_line(line)
                    if parsed is None:
                        failed_count += 1
                        failed_line_numbers.append(line_number)
                        continue

                    current_server = override or parsed.server
                    server_id = self._get_or_create_server(
                        cursor=cursor,
                        server_name=current_server,
                        server_cache=server_cache,
                    )
                    ip_address = self.ip_checker.extract_ip(parsed.message)

                    cursor.execute(
                        """
                        INSERT INTO logs (datetime, server_id, service, message, ip)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            parsed.datetime,
                            server_id,
                            parsed.service,
                            parsed.message,
                            ip_address,
                        ),
                    )
                    imported_count += 1

        return ImportResult(
            imported_count=imported_count,
            failed_count=failed_count,
            skipped_empty_count=skipped_empty_count,
            failed_line_numbers=tuple(failed_line_numbers),
        )

    @staticmethod
    def _get_or_create_server(
        cursor: sqlite3.Cursor,
        server_name: str,
        server_cache: dict[str, int],
    ) -> int:
        """Haal een server-id uit de cache of maak de server aan."""
        if server_name in server_cache:
            return server_cache[server_name]

        cursor.execute(
            "INSERT OR IGNORE INTO servers (name) VALUES (?)",
            (server_name,),
        )
        cursor.execute("SELECT id FROM servers WHERE name = ?", (server_name,))
        row = cursor.fetchone()

        if row is None:
            raise RuntimeError(f"Server-id kon niet worden opgehaald voor: {server_name}")

        server_id = int(row[0])
        server_cache[server_name] = server_id
        return server_id
