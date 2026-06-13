import tkinter as tk

from analysis.queries import QueryManager
from database.db import Database
from gui.app import ForensicApp
from importer.import_logs import LogImporter
from ip.ip_checker import IpChecker
from parser.syslog_parser import SyslogParser


def main():
    # Maak de database en tabellen.
    database = Database("forensic.db")
    database.create_tables()

    # Maak de onderdelen voor importeren en onderzoeken.
    parser = SyslogParser()
    ip_checker = IpChecker()
    importer = LogImporter(database, parser, ip_checker)
    query_manager = QueryManager(database)

    # Start het hoofdvenster.
    root = tk.Tk()
    ForensicApp(root, database, importer, query_manager)
    root.mainloop()


if __name__ == "__main__":
    main()
