import tkinter as tk
from tkinter import messagebox, ttk


class ManageTab:
    """Bevat alleen de GUI voor het verwijderen van serverlogboeken."""

    def __init__(self, parent, database, refresh_callback):
        self.database = database
        self.refresh_callback = refresh_callback

        self.frame = tk.Frame(parent)
        self.create_widgets()
        self.refresh_servers()

    def create_widgets(self):
        tk.Label(
            self.frame,
            text="Verwijder geïmporteerde loggegevens op servernaam",
            font=("TkDefaultFont", 12, "bold")
        ).pack(anchor="w", padx=10, pady=(15, 5))

        tk.Label(
            self.frame,
            text=(
                "De servernaam wordt uit de database gekozen. "
                "Hiermee worden alle logregels van die server verwijderd. "
                "Het oorspronkelijke bestand op de schijf blijft bestaan."
            ),
            justify="left",
            wraplength=700
        ).pack(anchor="w", padx=10, pady=(0, 10))

        select_frame = tk.Frame(self.frame)
        select_frame.pack(fill="x", padx=10)

        tk.Label(select_frame, text="Server").pack(side="left")

        self.server_combo = ttk.Combobox(
            select_frame,
            state="readonly",
            width=40
        )
        self.server_combo.pack(side="left", padx=10)

        tk.Button(
            select_frame,
            text="Verwijder server en logregels",
            command=self.delete_server
        ).pack(side="left")

    def refresh_servers(self):
        names = self.database.get_server_names()
        self.server_combo["values"] = names

        if self.server_combo.get() not in names:
            self.server_combo.set("")

    def delete_server(self):
        server_name = self.server_combo.get()

        if not server_name:
            messagebox.showwarning("Geen server", "Kies eerst een server.")
            return

        confirmed = messagebox.askyesno(
            "Server verwijderen",
            "Alle logregels van '" + server_name + "' worden verwijderd. Doorgaan?"
        )

        if not confirmed:
            return

        deleted_logs = self.database.delete_server(server_name)
        self.refresh_callback()

        messagebox.showinfo(
            "Verwijderd",
            str(deleted_logs) + " logregels zijn verwijderd."
        )
