import pytest

from ip.ip_checker import IpChecker
# Aanpassing vorige versie: De methode extract_ip() hoort nu bij de klasse IpChecker (feedback Peter)

# Uitleg parameterize staat in Master Piece import opzet code en pytest.docx.
# IP zoals 999.999.999.999 worden niet getest omdat het ondenkbaar is dat deze in een SYSLOG staan.
@pytest.mark.parametrize(
    "message, expected",
    [
        (
            "Failed login from 192.168.1.10",
            "192.168.1.10",
        ),
        (
            "Connection from 10.0.0.1",
            "10.0.0.1",
        ),
        (
            "No IP address found",
            None,
        ),
        (
            "",
            None,
        ),
    ],
)
def test_extract_ip(message: str, expected: str | None) -> None:
    checker = IpChecker()

    assert checker.extract_ip(message) == expected