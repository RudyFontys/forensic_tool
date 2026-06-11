import re
from datetime import datetime


class SyslogParser:
    """Zet één syslogregel om naar losse velden."""

    def __init__(self):
        self.pattern = re.compile(
            r"^(?P<datetime>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))\s+"
            r"(?P<server>\S+)\s+"
            r"(?P<service>[^\[:]+)"
            r"(?:\[(?P<pid>\d+)\])?:\s*"
            r"(?P<message>.*)$"
        )

    def parse_line(self, line):
        """Geef een dictionary terug, of None bij een ongeldige regel."""
        match = self.pattern.match(line)

        if not match:
            return None

        data = match.groupdict()
        raw_datetime = data["datetime"]

        try:
            parsed_datetime = datetime.fromisoformat(
                raw_datetime.replace("Z", "+00:00")
            )
            formatted_datetime = parsed_datetime.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            formatted_datetime = raw_datetime

        return {
            "datetime": formatted_datetime,
            "server": data["server"],
            "service": data["service"].strip(),
            "message": data["message"].strip()
        }
