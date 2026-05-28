import re


def extract_ip(message):
    match = re.search(r"(\d+\.\d+\.\d+\.\d+)", message)
    return match.group(1) if match else None