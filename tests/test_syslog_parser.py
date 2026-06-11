from parser.syslog_parser import SyslogParser


def test_parser_herkent_iso_syslogregel() -> None:
    parser = SyslogParser(default_year=2026)

    result = parser.parse_line(
        "2026-03-15T00:00:21+00:00 master sshd[123]: "
        "Failed password for root from 203.0.113.25 port 22"
    )

    assert result is not None
    assert result.datetime == "2026-03-15 00:00:21"
    assert result.server == "master"
    assert result.service == "sshd"
    assert "Failed password" in result.message
