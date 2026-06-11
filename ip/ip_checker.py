"""IP-adressen uit logmeldingen halen en valideren."""

from __future__ import annotations

import ipaddress
import re


class IpChecker:
    """Zoekt het eerste geldige IPv4-adres in een tekst."""

    _IPV4_CANDIDATE = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")

    def extract_ip(self, message: str) -> str | None:
        """Geef het eerste geldige IPv4-adres terug, anders ``None``."""
        for candidate in self._IPV4_CANDIDATE.findall(message):
            try:
                return str(ipaddress.IPv4Address(candidate))
            except ipaddress.AddressValueError:
                continue
        return None
