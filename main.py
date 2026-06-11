import tkinter as tk

from database.db import Database
from gui.app import ForensicApp
from importer.import_logs import LogImporter
from ip.ip_checker import IpChecker
from parser.syslog_parser import SyslogParser


def main():
    # Maak de onderdelen van de applicatie aan.
    database = Database("forensic.db")
    database.create_tables()

    parser = SyslogParser()
    ip_checker = IpChecker()
    importer = LogImporter(database, parser, ip_checker)

    # Start daarna het Tkinter-venster.
    root = tk.Tk()
    ForensicApp(root, importer)
    root.mainloop()


if __name__ == "__main__":
    main()
