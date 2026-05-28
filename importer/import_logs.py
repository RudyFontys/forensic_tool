''' 
- Leest een logbestand regel voor regel.
- Parseert elke regel om de datum, servernaam, service en bericht te extraheren.
- Slaat deze gegevens op in een database, samen met een eventueel gevonden IP-adres.
- Geeft feedback over het aantal succesvol geïmporteerde en mislukte regels.
'''

from database.db import get_connection # Haalt een verbinding met de SQLite-database op (uit database/db.py).
from parser.syslog_parser import parse_line # Parseert een logregel (uit parser/syslog_parser.py).
from ip.ip_checker import extract_ip # Extraheert een IP-adres uit een logbericht (uit ip/ip_checker.py).


def get_or_create_server(cursor, server_name, server_cache):
    """
    Haal server_id op uit cache of database.
    Als de server nog niet bestaat, maak deze aan.
    """
    if server_name not in server_cache:
        cursor.execute(
            "INSERT OR IGNORE INTO servers (name) VALUES (?)",
            (server_name,)
        )
        cursor.execute(
            "SELECT id FROM servers WHERE name = ?",
            (server_name,)
        )
        result = cursor.fetchone()
        if result is None:
            raise ValueError(f"Kon server_id niet ophalen voor server: {server_name}")
        server_cache[server_name] = result[0]

    return server_cache[server_name]


def import_file(filepath, server_name=None, debug=False):
    """
    Importeer een syslogbestand in de SQLite database.

    Args:
        filepath (str): pad naar syslogbestand
        server_name (str|None): optionele servernaam override.
                                Als None, gebruik servernaam uit syslogregel.
        debug (bool): toon debugmeldingen

    Returns:
        tuple: (imported_count, failed_count)
        tuple is overigens een onverandelijke lijst van data
        elke tuple is een enkele rij uit de database tabel
    """
    conn = get_connection()
    cursor = conn.cursor()

    imported_count = 0
    failed_count = 0
    server_cache = {}

    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()

                if not line:
                    continue

                parsed = parse_line(line)

                if not parsed:
                    failed_count += 1
                    if debug:
                        print(f"[DEBUG] Regel {line_number} kon niet worden geparsed:")
                        print(f"        {line}")
                    continue

                # Gebruik handmatige server override als die is opgegeven,
                # anders pak de servernaam uit de syslogregel zelf.
                current_server = server_name if server_name else parsed["server"]

                try:
                    server_id = get_or_create_server(cursor, current_server, server_cache)
                except Exception as e:
                    failed_count += 1
                    if debug:
                        print(f"[DEBUG] Regel {line_number}: fout bij server '{current_server}': {e}")
                    continue

                ip = extract_ip(parsed["message"])

                try:
                    cursor.execute("""
                        INSERT INTO logs (datetime, server_id, service, message, ip)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        parsed["datetime"],
                        server_id,
                        parsed["service"],
                        parsed["message"],
                        ip
                    ))
                    imported_count += 1

                    if debug:
                        print(
                            f"[DEBUG] Regel {line_number} geïmporteerd | "
                            f"datetime={parsed['datetime']} | "
                            f"server={current_server} | "
                            f"service={parsed['service']} | "
                            f"ip={ip}"
                        )

                except Exception as e:
                    failed_count += 1
                    if debug:
                        print(f"[DEBUG] Regel {line_number}: database insert mislukt: {e}")

        conn.commit()
        return imported_count, failed_count

    finally:
        conn.close()


# ==========================================================
# CLI TEST MODE
# Alleen actief wanneer dit bestand direct wordt gestart.
# Later kun men dit eenvoudig verwijderen of uitcommentariëren.
# ==========================================================
if __name__ == "__main__":
    import argparse
    import os
    import sys

    cli = argparse.ArgumentParser(
        description="Importeer een syslogbestand in de SQLite database"
    )

    cli.add_argument(
        "file",
        help="Pad naar het syslogbestand"
    )

    cli.add_argument(
        "--server",
        help="Optionele servernaam override. Als deze ontbreekt, wordt de servernaam uit de syslogregel gebruikt."
    )

    cli.add_argument(
        "--debug",
        action="store_true",
        help="Toon extra debuginformatie tijdens import"
    )

    args = cli.parse_args()

    if not os.path.exists(args.file):
        print(f"[ERROR] Bestand niet gevonden: {args.file}")
        sys.exit(1)

    print("=== SYSLOG IMPORT TOOL (CLI TEST MODE) ===")
    print(f"Bestand         : {args.file}")
    print(f"Server override : {args.server if args.server else 'Nee, gebruik servernaam uit syslog'}")
    print(f"Debug           : {'Aan' if args.debug else 'Uit'}")
    print("------------------------------------------")

    try:
        imported, failed = import_file(
            filepath=args.file,
            server_name=args.server,
            debug=args.debug
        )

        print("\n=== RESULTAAT ===")
        print(f"Geïmporteerde regels : {imported}")
        print(f"Mislukte regels      : {failed}")

    except Exception as e:
        print(f"[ERROR] Er ging iets mis tijdens de import: {e}")
        sys.exit(1)