from tkinter import ttk

from gui.import_tab import ImportTab
from gui.manage_tab import ManageTab
from gui.query_tab import QueryTab


class ForensicApp:
    """Maakt het hoofdvenster en koppelt de drie schermonderdelen."""

    def __init__(self, root, database, importer, query_manager):
        self.root = root
        self.database = database
        self.importer = importer
        self.query_manager = query_manager

        self.root.title("Forensic Syslog Tool")
        self.root.geometry("1150x720")

        self.create_tabs()

    def create_tabs(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        self.import_tab = ImportTab(
            notebook,
            self.importer,
            self.refresh_lists
        )

        self.query_tab = QueryTab(
            notebook,
            self.database,
            self.query_manager
        )

        self.manage_tab = ManageTab(
            notebook,
            self.database,
            self.refresh_lists
        )

        notebook.add(self.import_tab.frame, text="Importeren")
        notebook.add(self.query_tab.frame, text="Onderzoeken")
        notebook.add(self.manage_tab.frame, text="Beheren")

    def refresh_lists(self):
        """Werk alle server- en querykeuzelijsten opnieuw bij."""
        self.query_tab.refresh_servers()
        self.query_tab.refresh_saved_queries()
        self.manage_tab.refresh_servers()
