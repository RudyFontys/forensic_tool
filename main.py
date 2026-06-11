"""Startpunt van de forensic syslog-applicatie."""

from __future__ import annotations

from pathlib import Path

from database.db import DatabaseManager
from gui.app import ForensicToolApp
from importer.import_logs import LogImporter
from ip.ip_checker import IpChecker
from parser.syslog_parser import SyslogParser


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_DATABASE_PATH = PROJECT_DIR / "forensic.db"


def create_application(
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> ForensicToolApp:
    """Stel de objecten samen en geef de GUI terug.

    Alleen deze functie weet welke concrete klassen aan elkaar gekoppeld worden.
    Dit heet ook wel de *composition root* van de applicatie.
    """
    database = DatabaseManager(database_path)
    database.initialize()

    importer = LogImporter(
        database=database,
        parser=SyslogParser(),
        ip_checker=IpChecker(),
    )
    return ForensicToolApp(importer=importer, database_path=database.db_path)


def main() -> None:
    app = create_application()
    app.mainloop()


if __name__ == "__main__":
    main()
