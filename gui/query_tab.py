import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText


class QueryTab:
    """Bevat alleen de GUI voor zoeken en opgeslagen query's."""

    def __init__(self, parent, database, query_manager):
        self.database = database
        self.query_manager = query_manager
        self.saved_query_data = {}
        self.last_tested_clause = None

        self.frame = tk.Frame(parent)
        self.create_widgets()
        self.refresh_servers()
        self.refresh_saved_queries()

    def create_widgets(self):
        filter_frame = tk.LabelFrame(self.frame, text="Selectie")
        filter_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(filter_frame, text="Server").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.server_combo = ttk.Combobox(filter_frame, state="readonly", width=30)
        self.server_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(filter_frame, text="Vanaf").grid(
            row=0, column=2, sticky="w", padx=5, pady=5
        )
        self.start_entry = tk.Entry(filter_frame, width=22)
        self.start_entry.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

        tk.Label(filter_frame, text="Tot en met").grid(
            row=0, column=4, sticky="w", padx=5, pady=5
        )
        self.end_entry = tk.Entry(filter_frame, width=22)
        self.end_entry.grid(row=0, column=5, sticky="ew", padx=5, pady=5)

        tk.Label(
            filter_frame,
            text="Tijdformaat: JJJJ-MM-DD UU:MM:SS. Leeg betekent geen tijdsgrens."
        ).grid(row=1, column=0, columnspan=6, sticky="w", padx=5, pady=(0, 5))

        filter_frame.columnconfigure(1, weight=1)
        filter_frame.columnconfigure(3, weight=1)
        filter_frame.columnconfigure(5, weight=1)

        saved_frame = tk.LabelFrame(self.frame, text="Voorgemaakte query")
        saved_frame.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(saved_frame, text="Kies query").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.saved_combo = ttk.Combobox(saved_frame, state="readonly")
        self.saved_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.saved_combo.bind("<<ComboboxSelected>>", self.load_saved_query)

        tk.Button(
            saved_frame,
            text="Verwijder gekozen query",
            command=self.delete_saved_query
        ).grid(row=0, column=2, padx=5, pady=5)

        saved_frame.columnconfigure(1, weight=1)

        query_frame = tk.LabelFrame(self.frame, text="Handmatige query")
        query_frame.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(
            query_frame,
            text="Vul alleen de SQL-voorwaarde na WHERE in. Voorbeeld: service = 'sshd' AND message LIKE '%Failed password%'"
        ).pack(anchor="w", padx=5, pady=(5, 0))

        self.query_text = ScrolledText(query_frame, height=4)
        self.query_text.pack(fill="x", padx=5, pady=5)

        details_frame = tk.Frame(query_frame)
        details_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(details_frame, text="Naam").grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(details_frame)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=(5, 10))

        tk.Label(details_frame, text="Beschrijving").grid(row=0, column=2, sticky="w")
        self.description_entry = tk.Entry(details_frame)
        self.description_entry.grid(row=0, column=3, sticky="ew", padx=(5, 0))

        details_frame.columnconfigure(1, weight=1)
        details_frame.columnconfigure(3, weight=2)

        button_frame = tk.Frame(query_frame)
        button_frame.pack(fill="x", padx=5, pady=(0, 5))

        tk.Button(
            button_frame,
            text="Query uitvoeren / testen",
            command=self.test_query
        ).pack(side="left")

        tk.Button(
            button_frame,
            text="Geteste query opslaan",
            command=self.save_query
        ).pack(side="left", padx=5)

        result_frame = tk.LabelFrame(self.frame, text="Queryresultaat")
        result_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("datetime", "server", "service", "message", "ip")
        self.result_tree = ttk.Treeview(
            result_frame,
            columns=columns,
            show="headings"
        )

        self.result_tree.heading("datetime", text="Datum en tijd")
        self.result_tree.heading("server", text="Server")
        self.result_tree.heading("service", text="Service")
        self.result_tree.heading("message", text="Melding")
        self.result_tree.heading("ip", text="IP-adres")

        self.result_tree.column("datetime", width=150)
        self.result_tree.column("server", width=120)
        self.result_tree.column("service", width=100)
        self.result_tree.column("message", width=500)
        self.result_tree.column("ip", width=120)

        vertical_scroll = ttk.Scrollbar(
            result_frame,
            orient="vertical",
            command=self.result_tree.yview
        )
        horizontal_scroll = ttk.Scrollbar(
            result_frame,
            orient="horizontal",
            command=self.result_tree.xview
        )

        self.result_tree.configure(
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set
        )

        self.result_tree.grid(row=0, column=0, sticky="nsew")
        vertical_scroll.grid(row=0, column=1, sticky="ns")
        horizontal_scroll.grid(row=1, column=0, sticky="ew")

        result_frame.rowconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)

        self.count_label = tk.Label(result_frame, text="0 resultaten")
        self.count_label.grid(row=2, column=0, sticky="w", pady=5)

    def refresh_servers(self):
        server_names = ["Alle servers"] + self.database.get_server_names()
        current = self.server_combo.get()
        self.server_combo["values"] = server_names

        if current in server_names:
            self.server_combo.set(current)
        else:
            self.server_combo.set("Alle servers")

    def refresh_saved_queries(self):
        rows = self.query_manager.get_saved_queries()
        self.saved_query_data = {}

        for query_id, name, description, where_clause in rows:
            self.saved_query_data[name] = {
                "id": query_id,
                "description": description or "",
                "where_clause": where_clause
            }

        names = list(self.saved_query_data.keys())
        self.saved_combo["values"] = names

        if self.saved_combo.get() not in names:
            self.saved_combo.set("")

    def load_saved_query(self, event=None):
        name = self.saved_combo.get()
        data = self.saved_query_data.get(name)

        if data is None:
            return

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, name)

        self.description_entry.delete(0, tk.END)
        self.description_entry.insert(0, data["description"])

        self.query_text.delete("1.0", tk.END)
        self.query_text.insert("1.0", data["where_clause"])

        # Na wijzigen of laden moet de onderzoeker de query opnieuw testen.
        self.last_tested_clause = None

    def get_current_clause(self):
        return self.query_text.get("1.0", tk.END).strip()

    def execute_query(self):
        server_name = self.server_combo.get()
        start_time = self.start_entry.get().strip()
        end_time = self.end_entry.get().strip()
        where_clause = self.get_current_clause()

        rows = self.query_manager.search_logs(
            server_name,
            start_time,
            end_time,
            where_clause
        )

        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        for row in rows:
            self.result_tree.insert("", tk.END, values=row)

        self.count_label.config(text=str(len(rows)) + " resultaten")
        return rows

    def test_query(self):
        try:
            rows = self.execute_query()
            self.last_tested_clause = self.get_current_clause()
            messagebox.showinfo(
                "Query uitgevoerd",
                "De query is geldig. Aantal resultaten: " + str(len(rows))
            )
        except Exception as error:
            self.last_tested_clause = None
            messagebox.showerror("Queryfout", str(error))

    def save_query(self):
        name = self.name_entry.get().strip()
        description = self.description_entry.get().strip()
        where_clause = self.get_current_clause()

        if not name:
            messagebox.showwarning("Naam ontbreekt", "Vul een begrijpelijke naam in.")
            return

        if not where_clause:
            messagebox.showwarning("Query ontbreekt", "Vul eerst een queryvoorwaarde in.")
            return

        if where_clause != self.last_tested_clause:
            messagebox.showwarning(
                "Eerst testen",
                "Voer deze query eerst succesvol uit voordat je hem opslaat."
            )
            return

        try:
            self.query_manager.save_query(name, description, where_clause)
            self.refresh_saved_queries()
            self.saved_combo.set(name)
            messagebox.showinfo("Opgeslagen", "De query is opgeslagen.")
        except Exception as error:
            messagebox.showerror("Opslagfout", str(error))

    def delete_saved_query(self):
        name = self.saved_combo.get()
        data = self.saved_query_data.get(name)

        if data is None:
            messagebox.showwarning("Geen query", "Kies eerst een opgeslagen query.")
            return

        confirmed = messagebox.askyesno(
            "Query verwijderen",
            "Wil je de query '" + name + "' verwijderen?"
        )

        if confirmed:
            self.query_manager.delete_query(data["id"])
            self.saved_combo.set("")
            self.refresh_saved_queries()
            messagebox.showinfo("Verwijderd", "De query is verwijderd.")
