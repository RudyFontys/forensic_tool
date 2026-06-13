import pytest

from analysis.queries import QueryManager
from database.db import Database


@pytest.fixture
def filled_database(tmp_path):
    # Iedere test krijgt een tijdelijke database; forensic.db blijft onaangetast.
    database = Database(str(tmp_path / "test.db"))
    database.create_tables()

    connection = database.connect()
    cursor = connection.cursor()

    server_id = database.get_or_create_server(cursor, "server1")
    cursor.execute("""
        INSERT INTO logs (datetime, server_id, service, message, ip)
        VALUES (?, ?, ?, ?, ?)
    """, (
        "2026-03-15 08:30:00",
        server_id,
        "sshd",
        "Failed password from 198.51.100.7",
        "198.51.100.7"
    ))

    connection.commit()
    connection.close()
    return database


def test_query_zoeken_opslaan_en_verwijderen(filled_database):
    # Deze test controleert de complete hoofdtaak van QueryManager:
    # zoeken, een geteste filter opslaan en die later verwijderen.
    manager = QueryManager(filled_database)
    clause = "service = 'sshd' AND message LIKE '%Failed password%'"

    rows = manager.search_logs("server1", "", "", clause)
    assert len(rows) == 1
    assert rows[0][1] == "server1"

    manager.save_query("Mislukte SSH-login", "Zoekt foutieve SSH-logins", clause)
    saved = manager.get_saved_queries()
    assert saved[0][1] == "Mislukte SSH-login"

    manager.delete_query(saved[0][0])
    assert manager.get_saved_queries() == []


def test_server_verwijderen_wist_bijbehorende_logs(filled_database):
    # Verwijderen gebeurt op een gekozen servernaam. We controleren daarom
    # zowel de serverlijst als de gekoppelde logregels na de verwijdering.
    deleted = filled_database.delete_server("server1")

    assert deleted == 1
    assert filled_database.get_server_names() == []

    connection = filled_database.connect()
    count = connection.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
    connection.close()

    assert count == 0
