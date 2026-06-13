import os


class LogImporter:
    """Leest een bestand en slaat geldige syslogregels op."""

    def __init__(self, database, parser, ip_checker):
        self.database = database
        self.parser = parser
        self.ip_checker = ip_checker

    def import_file(self, filepath, server_name=None):
        if not os.path.exists(filepath):
            raise FileNotFoundError("Het gekozen syslogbestand bestaat niet.")

        connection = self.database.connect()
        cursor = connection.cursor()

        imported_count = 0
        failed_count = 0

        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as file:
                for line in file:
                    line = line.strip()

                    if not line:
                        continue

                    parsed = self.parser.parse_line(line)

                    if parsed is None:
                        failed_count += 1
                        continue

                    # Een ingevulde servernaam overschrijft de naam uit de logregel.
                    current_server = server_name or parsed["server"]
                    server_id = self.database.get_or_create_server(
                        cursor,
                        current_server
                    )

                    ip_address = self.ip_checker.extract_ip(parsed["message"])

                    cursor.execute("""
                        INSERT INTO logs (datetime, server_id, service, message, ip)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        parsed["datetime"],
                        server_id,
                        parsed["service"],
                        parsed["message"],
                        ip_address
                    ))

                    imported_count += 1

            connection.commit()
            return imported_count, failed_count

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()
