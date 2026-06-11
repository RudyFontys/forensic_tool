import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText


class ForensicApp:
    """Bevat alleen het venster en de acties van de gebruiker."""

    def __init__(self, root, importer):
        self.root = root
        self.importer = importer
        self.filepath = ""

        self.root.title("Forensic Syslog Import Tool")
        self.root.geometry("700x450")

        self.create_widgets()

    def create_widgets(self):
        tk.Label(
            self.root,
            text="Syslogbestand"
        ).pack(anchor="w", padx=10, pady=(10, 0))

        file_frame = tk.Frame(self.root)
        file_frame.pack(fill="x", padx=10)

        self.file_entry = tk.Entry(file_frame)
        self.file_entry.pack(side="left", fill="x", expand=True)

        tk.Button(
            file_frame,
            text="Bladeren",
            command=self.choose_file
        ).pack(side="left", padx=(5, 0))

        tk.Label(
            self.root,
            text="Servernaam override (optioneel)"
        ).pack(anchor="w", padx=10, pady=(10, 0))

        self.server_entry = tk.Entry(self.root)
        self.server_entry.pack(fill="x", padx=10)

        tk.Button(
            self.root,
            text="Importeer syslog",
            command=self.import_logs
        ).pack(pady=10)

        tk.Label(
            self.root,
            text="Resultaat"
        ).pack(anchor="w", padx=10)

        self.output = ScrolledText(self.root, height=16)
        self.output.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def choose_file(self):
        selected_file = filedialog.askopenfilename(
            title="Kies een syslogbestand",
            filetypes=[("Logbestanden", "*.log *.txt"), ("Alle bestanden", "*.*")]
        )

        if selected_file:
            self.filepath = selected_file
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, selected_file)

    def import_logs(self):
        filepath = self.file_entry.get().strip()
        server_name = self.server_entry.get().strip()

        if not filepath:
            messagebox.showwarning(
                "Geen bestand",
                "Kies eerst een syslogbestand."
            )
            return

        try:
            imported, failed = self.importer.import_file(
                filepath,
                server_name if server_name else None
            )

            self.output.insert(
                tk.END,
                "Bestand: " + filepath + "\n"
                + "Geïmporteerde regels: " + str(imported) + "\n"
                + "Mislukte regels: " + str(failed) + "\n\n"
            )
            self.output.see(tk.END)

        except Exception as error:
            messagebox.showerror("Importfout", str(error))
