"""Parser voor veelgebruikte Linux-syslogformaten."""

from __future__ import annotations

import re
from datetime import datetime

from database.models import ParsedLogEntry


class SyslogParser:
    """Zet één tekstregel om naar een ``ParsedLogEntry``.

    Ondersteund worden:
    - ISO/RFC3339-tijdstempels, zoals ``2026-03-15T00:00:21+00:00``;
    - het klassieke syslogformaat, zoals ``Mar 15 00:00:21``.
    """

    _ISO_PATTERN = re.compile(
        r"^(?P<datetime>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
        r"(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))\s+"
        r"(?P<server>\S+)\s+"
        r"(?P<service>[^\[:]+)"
        r"(?:\[(?P<pid>\d+)\])?:\s*"
        r"(?P<message>.*)$"
    )

    _CLASSIC_PATTERN = re.compile(
        r"^(?P<month>[A-Z][a-z]{2})\s+"
        r"(?P<day>\d{1,2})\s+"
        r"(?P<time>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<server>\S+)\s+"
        r"(?P<service>[^\[:]+)"
        r"(?:\[(?P<pid>\d+)\])?:\s*"
        r"(?P<message>.*)$"
    )

    def __init__(self, default_year: int | None = None) -> None:
        self.default_year = default_year or datetime.now().year

    def parse_line(self, line: str) -> ParsedLogEntry | None:
        """Parseer een regel; geef ``None`` terug bij een onbekend formaat."""
        stripped_line = line.strip()
        if not stripped_line:
            return None

        iso_match = self._ISO_PATTERN.match(stripped_line)
        if iso_match:
            return self._from_iso_match(iso_match)

        classic_match = self._CLASSIC_PATTERN.match(stripped_line)
        if classic_match:
            return self._from_classic_match(classic_match)

        return None

    @staticmethod
    def _from_iso_match(match: re.Match[str]) -> ParsedLogEntry | None:
        values = match.groupdict()
        raw_datetime = values["datetime"]

        try:
            parsed_datetime = datetime.fromisoformat(raw_datetime.replace("Z", "+00:00"))
            normalized_datetime = parsed_datetime.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None

        return ParsedLogEntry(
            datetime=normalized_datetime,
            server=values["server"],
            service=values["service"].strip(),
            message=values["message"].strip(),
        )

    def _from_classic_match(self, match: re.Match[str]) -> ParsedLogEntry | None:
        values = match.groupdict()
        raw_datetime = (
            f"{self.default_year} {values['month']} {values['day']} {values['time']}"
        )

        try:
            parsed_datetime = datetime.strptime(raw_datetime, "%Y %b %d %H:%M:%S")
        except ValueError:
            return None

        return ParsedLogEntry(
            datetime=parsed_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            server=values["server"],
            service=values["service"].strip(),
            message=values["message"].strip(),
        )
