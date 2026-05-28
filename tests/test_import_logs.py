import sqlite3
import pytest

from importer import import_logs


@pytest.fixture
def test_db():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datetime TEXT NOT NULL,
            server_id INTEGER NOT NULL,
            service TEXT NOT NULL,
            message TEXT NOT NULL,
            ip TEXT,
            FOREIGN KEY (server_id) REFERENCES servers(id)
        )
    """)

    conn.commit()
    return conn


def test_get_or_create_server_creates_new_server(test_db):
    cursor = test_db.cursor()
    server_cache = {}

    server_id = import_logs.get_or_create_server(
        cursor,
        "server01",
        server_cache
    )

    assert server_id == 1
    assert server_cache["server01"] == 1


def test_get_or_create_server_uses_cache(test_db):
    cursor = test_db.cursor()
    server_cache = {}

    first_id = import_logs.get_or_create_server(
        cursor,
        "server01",
        server_cache
    )

    second_id = import_logs.get_or_create_server(
        cursor,
        "server01",
        server_cache
    )

    assert first_id == second_id
    assert len(server_cache) == 1


def test_import_file_imports_valid_lines(tmp_path, test_db, monkeypatch):
    log_file = tmp_path / "syslog.log"

    log_file.write_text(
        "regel 1\n"
        "regel 2\n",
        encoding="utf-8"
    )

    def fake_get_connection():
        return test_db

    def fake_parse_line(line):
        return {
            "datetime": "2025-05-07 14:32:15",
            "server": "server01",
            "service": "sshd",
            "message": "Failed login from 192.168.1.10"
        }

    def fake_extract_ip(message):
        return "192.168.1.10"

    monkeypatch.setattr(import_logs, "get_connection", fake_get_connection)
    monkeypatch.setattr(import_logs, "parse_line", fake_parse_line)
    monkeypatch.setattr(import_logs, "extract_ip", fake_extract_ip)

    imported, failed = import_logs.import_file(str(log_file))

    assert imported == 2
    assert failed == 0

    cursor = test_db.cursor()

    cursor.execute("SELECT COUNT(*) FROM logs")
    assert cursor.fetchone()[0] == 2

    cursor.execute("SELECT name FROM servers")
    assert cursor.fetchone()[0] == "server01"


def test_import_file_counts_failed_parse_lines(tmp_path, test_db, monkeypatch):
    log_file = tmp_path / "syslog.log"

    log_file.write_text(
        "geldige regel\n"
        "ongeldige regel\n",
        encoding="utf-8"
    )

    def fake_get_connection():
        return test_db

    def fake_parse_line(line):
        if line == "ongeldige regel":
            return None

        return {
            "datetime": "2025-05-07 14:32:15",
            "server": "server01",
            "service": "sshd",
            "message": "Login from 10.0.0.1"
        }

    def fake_extract_ip(message):
        return "10.0.0.1"

    monkeypatch.setattr(import_logs, "get_connection", fake_get_connection)
    monkeypatch.setattr(import_logs, "parse_line", fake_parse_line)
    monkeypatch.setattr(import_logs, "extract_ip", fake_extract_ip)

    imported, failed = import_logs.import_file(str(log_file))

    assert imported == 1
    assert failed == 1


def test_import_file_uses_server_override(tmp_path, test_db, monkeypatch):
    log_file = tmp_path / "syslog.log"

    log_file.write_text(
        "regel 1\n",
        encoding="utf-8"
    )

    def fake_get_connection():
        return test_db

    def fake_parse_line(line):
        return {
            "datetime": "2025-05-07 14:32:15",
            "server": "server-uit-logregel",
            "service": "sshd",
            "message": "Login from 172.16.0.5"
        }

    def fake_extract_ip(message):
        return "172.16.0.5"

    monkeypatch.setattr(import_logs, "get_connection", fake_get_connection)
    monkeypatch.setattr(import_logs, "parse_line", fake_parse_line)
    monkeypatch.setattr(import_logs, "extract_ip", fake_extract_ip)

    imported, failed = import_logs.import_file(
        filepath=str(log_file),
        server_name="handmatige-server"
    )

    assert imported == 1
    assert failed == 0

    cursor = test_db.cursor()
    cursor.execute("SELECT name FROM servers")

    assert cursor.fetchone()[0] == "handmatige-server"