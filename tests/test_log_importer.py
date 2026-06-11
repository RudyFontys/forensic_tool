from database.db import DatabaseManager
from importer.import_logs import LogImporter
from ip.ip_checker import IpChecker
from parser.syslog_parser import SyslogParser


def test_importer_slaat_geldige_regel_op_en_telt_fout(tmp_path) -> None:
    database = DatabaseManager(tmp_path / "test.db")
    database.initialize()
    importer = LogImporter(database, SyslogParser(default_year=2026), IpChecker())

    log_file = tmp_path / "auth.log"
    log_file.write_text(
        "2026-03-15T08:30:00+00:00 original sshd[42]: "
        "Failed password from 198.51.100.7\n"
        "dit is geen geldige syslogregel\n"
        "\n",
        encoding="utf-8",
    )

    result = importer.import_file(log_file, server_name="onderzoek-server")

    assert result.imported_count == 1
    assert result.failed_count == 1
    assert result.skipped_empty_count == 1
    assert result.failed_line_numbers == (2,)

    connection = database.connect()
    try:
        row = connection.execute(
            """
            SELECT logs.datetime, servers.name, logs.service, logs.message, logs.ip
            FROM logs
            JOIN servers ON servers.id = logs.server_id
            """
        ).fetchone()
    finally:
        connection.close()

    assert row is not None
    assert tuple(row) == (
        "2026-03-15 08:30:00",
        "onderzoek-server",
        "sshd",
        "Failed password from 198.51.100.7",
        "198.51.100.7",
    )
