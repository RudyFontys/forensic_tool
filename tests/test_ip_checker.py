import pytest

from ip.ip_checker import IpChecker


@pytest.mark.parametrize(
    "message, expected",
    [
        ("Failed login from 192.168.1.10", "192.168.1.10"),
        ("Connection from 10.0.0.1", "10.0.0.1"),
        ("No IP address found", None),
        ("", None),
    ]
)
def test_extract_ip(message, expected):
    # We testen meerdere soorten invoer met dezelfde testcode (DRY).
    checker = IpChecker()

    assert checker.extract_ip(message) == expected
