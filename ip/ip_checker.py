import re


class IpChecker:
    """Zoekt een IPv4-adres in een tekstbericht."""

    def extract_ip(self, message):
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)", message)

        if match:
            return match.group(1)

        return None
