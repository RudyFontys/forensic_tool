import re


class QueryManager:
    """Voert zoekopdrachten uit en beheert opgeslagen query's."""

    def __init__(self, database):
        self.database = database

    def validate_where_clause(self, where_clause):
        """Controleer dat alleen een veilige leesvoorwaarde is ingevuld."""
        if not where_clause:
            return

        upper_clause = where_clause.upper()
        forbidden_words = [
            "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
            "CREATE", "PRAGMA", "ATTACH", "DETACH"
        ]

        if ";" in where_clause or "--" in where_clause:
            raise ValueError("Gebruik geen puntkomma of SQL-commentaar in de query.")

        for word in forbidden_words:
            # Met woordgrenzen wordt bijvoorbeeld "deleted_file" niet onterecht geweigerd.
            if re.search(r"\b" + word + r"\b", upper_clause):
                raise ValueError(
                    "Alleen een leesfilter is toegestaan. Verboden woord: " + word
                )

    def search_logs(self, server_name="", start_time="", end_time="", where_clause=""):
        """Zoek logregels op server, tijdsperiode en een extra SQL-filter."""
        self.validate_where_clause(where_clause)

        sql = """
            SELECT
                logs.datetime,
                servers.name,
                logs.service,
                logs.message,
                logs.ip
            FROM logs
            JOIN servers ON servers.id = logs.server_id
            WHERE 1 = 1
        """
        parameters = []

        if server_name and server_name != "Alle servers":
            sql += " AND servers.name = ?"
            parameters.append(server_name)

        if start_time:
            sql += " AND logs.datetime >= ?"
            parameters.append(start_time)

        if end_time:
            sql += " AND logs.datetime <= ?"
            parameters.append(end_time)

        if where_clause:
            # De onderzoeker vult alleen het deel na WHERE in.
            sql += " AND (" + where_clause + ")"

        sql += " ORDER BY logs.datetime"

        connection = self.database.connect()
        cursor = connection.cursor()

        try:
            cursor.execute(sql, parameters)
            rows = cursor.fetchall()
            return rows
        except Exception as error:
            raise ValueError("De query bevat een fout: " + str(error))
        finally:
            connection.close()

    def save_query(self, name, description, where_clause):
        """Sla een nieuwe query op of werk een bestaande naam bij."""
        self.validate_where_clause(where_clause)

        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id FROM saved_queries WHERE name = ?",
            (name,)
        )
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE saved_queries
                SET description = ?, where_clause = ?
                WHERE name = ?
            """, (description, where_clause, name))
        else:
            cursor.execute("""
                INSERT INTO saved_queries (name, description, where_clause)
                VALUES (?, ?, ?)
            """, (name, description, where_clause))

        connection.commit()
        connection.close()

    def get_saved_queries(self):
        """Geef alle opgeslagen query's terug."""
        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, description, where_clause
            FROM saved_queries
            ORDER BY name
        """)
        rows = cursor.fetchall()

        connection.close()
        return rows

    def delete_query(self, query_id):
        """Verwijder één opgeslagen query."""
        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM saved_queries WHERE id = ?",
            (query_id,)
        )

        connection.commit()
        connection.close()
