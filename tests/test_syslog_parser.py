from parser.syslog_parser import SyslogParser


def test_parse_line():
    # We testen een geldige regel, omdat dit de hoofdtaak van de parser is.
    parser = SyslogParser()
    line = (
        "2026-03-15T08:30:00+00:00 server1 sshd[42]: "
        "Failed password from 198.51.100.7"
    )

    result = parser.parse_line(line)

    assert result["datetime"] == "2026-03-15 08:30:00"
    assert result["server"] == "server1"
    assert result["service"] == "sshd"
    assert result["message"] == "Failed password from 198.51.100.7"

    # Een ongeldige regel mag niet als betrouwbaar logrecord worden gebruikt.
    assert parser.parse_line("dit is geen syslogregel") is None
