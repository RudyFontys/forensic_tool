import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText


class ImportTab:
    """Bevat alleen de GUI voor het importeren van syslogbestanden."""

    def __init__(self, parent, importer, refresh_callback):
        self.importer = importer
        self.refresh_callback = refresh_callback

        self.frame = tk.Frame(parent)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(
            self.frame,
            text="Syslogbestand"
        ).pack(anchor="w", padx=10, pady=(10, 0))

        file_frame = tk.Frame(self.frame)
        file_frame.pack(fill="x", padx=10)

        self.file_entry = tk.Entry(file_frame)
        self.file_entry.pack(side="left", fill="x", expand=True)

        tk.Button(
            file_frame,
            text="Bladeren",
            command=self.choose_file
        ).pack(side="left", padx=(5, 0))

        tk.Label(
            self.frame,
            text="Servernaam override (optioneel)"
        ).pack(anchor="w", padx=10, pady=(10, 0))

        self.server_entry = tk.Entry(self.frame)
        self.server_entry.pack(fill="x", padx=10)

        tk.Button(
            self.frame,
            text="Importeer syslog",
            command=self.import_logs
        ).pack(pady=10)

        tk.Label(
            self.frame,
            text="Importresultaat"
        ).pack(anchor="w", padx=10)

        self.output = ScrolledText(self.frame, height=20)
        self.output.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def choose_file(self):
        selected_file = filedialog.askopenfilename(
            title="Kies een syslogbestand",
            filetypes=[("Logbestanden", "*.log *.txt"), ("Alle bestanden", "*.*")]
        )

        if selected_file:
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

            # Nieuwe servers moeten direct in de keuzelijsten zichtbaar worden.
            self.refresh_callback()

        except Exception as error:
            messagebox.showerror("Importfout", str(error))
