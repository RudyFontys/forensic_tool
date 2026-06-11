"""Tkinter-gebruikersinterface voor de eerste projectfase."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from importer.import_logs import LogImporter


class ForensicToolApp(tk.Tk):
    """GUI waarmee een onderzoeker één syslogbestand kan importeren."""

    def __init__(self, importer: LogImporter, database_path: Path) -> None:
        super().__init__()
        self.importer = importer
        self.database_path = database_path

        self.title("Forensic Syslog Tool")
        self.geometry("780x500")
        self.minsize(680, 420)

        self.file_path_var = tk.StringVar()
        self.server_name_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Kies een syslogbestand om te beginnen.")

        self._build_interface()

    def _build_interface(self) -> None:
        main_frame = ttk.Frame(self, padding=16)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)

        ttk.Label(
            main_frame,
            text="Syslog importeren",
            font=("TkDefaultFont", 15, "bold"),
        ).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 14))

        ttk.Label(main_frame, text="Logbestand:").grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        ttk.Entry(main_frame, textvariable=self.file_path_var).grid(
            row=1, column=1, sticky=tk.EW, pady=5
        )
        ttk.Button(main_frame, text="Bladeren…", command=self._select_file).grid(
            row=1, column=2, padx=(10, 0), pady=5
        )

        ttk.Label(main_frame, text="Server override:").grid(
            row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        ttk.Entry(main_frame, textvariable=self.server_name_var).grid(
            row=2, column=1, sticky=tk.EW, pady=5
        )
        ttk.Label(main_frame, text="optioneel").grid(
            row=2, column=2, sticky=tk.W, padx=(10, 0), pady=5
        )

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, sticky=tk.EW, pady=(12, 10))

        self.import_button = ttk.Button(
            button_frame,
            text="Importeren",
            command=self._import_selected_file,
        )
        self.import_button.pack(side=tk.LEFT)

        ttk.Button(
            button_frame,
            text="Uitvoer wissen",
            command=self._clear_output,
        ).pack(side=tk.LEFT, padx=(10, 0))

        self.output = ScrolledText(main_frame, wrap=tk.WORD, height=15, state=tk.DISABLED)
        self.output.grid(row=4, column=0, columnspan=3, sticky=tk.NSEW)

        ttk.Label(main_frame, textvariable=self.status_var).grid(
            row=5, column=0, columnspan=3, sticky=tk.W, pady=(10, 0)
        )

    def _select_file(self) -> None:
        selected_path = filedialog.askopenfilename(
            title="Selecteer een syslogbestand",
            filetypes=(
                ("Logbestanden", "*.log *.txt"),
                ("Alle bestanden", "*.*"),
            ),
        )
        if selected_path:
            self.file_path_var.set(selected_path)
            self.status_var.set(f"Geselecteerd: {selected_path}")

    def _import_selected_file(self) -> None:
        path_text = self.file_path_var.get().strip()
        if not path_text:
            messagebox.showwarning("Geen bestand", "Selecteer eerst een syslogbestand.")
            return

        self.import_button.configure(state=tk.DISABLED)
        self.status_var.set("Import wordt uitgevoerd…")
        self.update_idletasks()

        try:
            result = self.importer.import_file(
                filepath=path_text,
                server_name=self.server_name_var.get(),
            )
        except (OSError, ValueError, RuntimeError) as exc:
            self.status_var.set("Import mislukt.")
            messagebox.showerror("Importfout", str(exc))
            self._append_output(f"FOUT: {exc}\n")
        else:
            report_lines = [
                f"Bestand: {path_text}",
                f"Database: {self.database_path}",
                f"Geïmporteerde regels: {result.imported_count}",
                f"Mislukte regels: {result.failed_count}",
                f"Overgeslagen lege regels: {result.skipped_empty_count}",
            ]
            if result.failed_line_numbers:
                numbers = ", ".join(map(str, result.failed_line_numbers[:30]))
                suffix = " …" if len(result.failed_line_numbers) > 30 else ""
                report_lines.append(f"Niet herkende regelnummers: {numbers}{suffix}")

            self._append_output("\n".join(report_lines) + "\n" + "-" * 70 + "\n")
            self.status_var.set(
                f"Import gereed: {result.imported_count} gelukt, "
                f"{result.failed_count} mislukt."
            )
        finally:
            self.import_button.configure(state=tk.NORMAL)

    def _append_output(self, text: str) -> None:
        self.output.configure(state=tk.NORMAL)
        self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.configure(state=tk.DISABLED)

    def _clear_output(self) -> None:
        self.output.configure(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.configure(state=tk.DISABLED)
        self.status_var.set("Uitvoer gewist.")
