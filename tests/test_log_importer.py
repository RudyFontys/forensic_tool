from database.db import Database
from importer.import_logs import LogImporter
from ip.ip_checker import IpChecker
from parser.syslog_parser import SyslogParser


def test_import_file(tmp_path):
    # tmp_path maakt een tijdelijke map. De echte forensic.db blijft onaangetast.
    test_database = tmp_path / "test.db"
    test_log = tmp_path / "test.log"

    test_log.write_text(
        "2026-03-15T08:30:00+00:00 server1 sshd[42]: "
        "Failed password from 198.51.100.7\n"
        "ongeldige regel\n",
        encoding="utf-8"
    )

    database = Database(str(test_database))
    database.create_tables()

    importer = LogImporter(
        database,
        SyslogParser(),
        IpChecker()
    )

    imported, failed = importer.import_file(str(test_log))

    # Hiermee controleren we het zichtbare resultaat van de import.
    assert imported == 1
    assert failed == 1

    # Daarna lezen we de database terug om te controleren of de data echt is opgeslagen.
    connection = database.connect()
    row = connection.execute("""
        SELECT servers.name, logs.service, logs.ip
        FROM logs
        JOIN servers ON servers.id = logs.server_id
    """).fetchone()
    connection.close()

    assert row == ("server1", "sshd", "198.51.100.7")
