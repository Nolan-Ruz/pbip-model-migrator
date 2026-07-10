import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from pbip_model_migrator.core.migration import MigrationEngine
from pbip_model_migrator.gui.mapping_builder import build_mapping
from pbip_model_migrator.operations.table_mapper import TableMapper


class MigratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PBIP Model Migrator")
        self.geometry("760x640")

        self.file_path_var = tk.StringVar()

        self._build_file_section()
        self._build_table_mapping_section()
        self._build_column_mapping_section()
        self._build_output_section()
        self._build_run_section()

    # -- layout -----------------------------------------------------------

    def _build_file_section(self):
        frame = ttk.LabelFrame(self, text="PBIP File")
        frame.pack(fill="x", padx=10, pady=(10, 5))

        entry = ttk.Entry(frame, textvariable=self.file_path_var, state="readonly")
        entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)

        ttk.Button(frame, text="Browse...", command=self.browse_file).pack(
            side="left", padx=(0, 10), pady=10
        )

    def _build_table_mapping_section(self):
        frame = ttk.LabelFrame(self, text="Table Mappings (old table -> new table)")
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.table_tree = ttk.Treeview(
            frame, columns=("old", "new"), show="headings", height=5
        )
        self.table_tree.heading("old", text="Old Table")
        self.table_tree.heading("new", text="New Table")
        self.table_tree.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        entry_row = ttk.Frame(frame)
        entry_row.pack(fill="x", padx=10, pady=(0, 10))

        self.table_old_entry = ttk.Entry(entry_row)
        self.table_old_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.table_new_entry = ttk.Entry(entry_row)
        self.table_new_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        ttk.Button(entry_row, text="Add", command=self.add_table_mapping).pack(
            side="left", padx=(0, 5)
        )
        ttk.Button(
            entry_row, text="Remove Selected", command=self.remove_table_mapping
        ).pack(side="left")

    def _build_column_mapping_section(self):
        frame = ttk.LabelFrame(
            self, text="Column Mappings (table / old column -> new column)"
        )
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.column_tree = ttk.Treeview(
            frame, columns=("table", "old", "new"), show="headings", height=5
        )
        self.column_tree.heading("table", text="Table")
        self.column_tree.heading("old", text="Old Column")
        self.column_tree.heading("new", text="New Column")
        self.column_tree.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        entry_row = ttk.Frame(frame)
        entry_row.pack(fill="x", padx=10, pady=(0, 10))

        self.column_table_entry = ttk.Entry(entry_row)
        self.column_table_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.column_old_entry = ttk.Entry(entry_row)
        self.column_old_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.column_new_entry = ttk.Entry(entry_row)
        self.column_new_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        ttk.Button(entry_row, text="Add", command=self.add_column_mapping).pack(
            side="left", padx=(0, 5)
        )
        ttk.Button(
            entry_row, text="Remove Selected", command=self.remove_column_mapping
        ).pack(side="left")

    def _build_output_section(self):
        frame = ttk.LabelFrame(self, text="Output")
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.output_text = tk.Text(frame, height=10, state="disabled")
        self.output_text.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_run_section(self):
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Button(
            frame, text="Run Migration (Test)", command=self.run_migration
        ).pack(side="right")

    # -- actions ------------------------------------------------------------

    def browse_file(self):
        path = filedialog.askopenfilename(
            title="Select PBIP file",
            filetypes=[("Power BI Project", "*.pbip"), ("All files", "*.*")],
        )
        if path:
            self.file_path_var.set(path)
            self.log(f"Selected PBIP file: {path}")

    def add_table_mapping(self):
        old = self.table_old_entry.get().strip()
        new = self.table_new_entry.get().strip()
        if not old or not new:
            messagebox.showwarning(
                "Missing value", "Both old and new table names are required."
            )
            return
        self.table_tree.insert("", "end", values=(old, new))
        self.table_old_entry.delete(0, "end")
        self.table_new_entry.delete(0, "end")

    def remove_table_mapping(self):
        for item in self.table_tree.selection():
            self.table_tree.delete(item)

    def add_column_mapping(self):
        table = self.column_table_entry.get().strip()
        old = self.column_old_entry.get().strip()
        new = self.column_new_entry.get().strip()
        if not table or not old or not new:
            messagebox.showwarning(
                "Missing value",
                "Table, old column, and new column are all required.",
            )
            return
        self.column_tree.insert("", "end", values=(table, old, new))
        self.column_table_entry.delete(0, "end")
        self.column_old_entry.delete(0, "end")
        self.column_new_entry.delete(0, "end")

    def remove_column_mapping(self):
        for item in self.column_tree.selection():
            self.column_tree.delete(item)

    def gather_table_rows(self):
        return [
            tuple(self.table_tree.item(item, "values"))
            for item in self.table_tree.get_children()
        ]

    def gather_column_rows(self):
        return [
            tuple(self.column_tree.item(item, "values"))
            for item in self.column_tree.get_children()
        ]

    def run_migration(self):
        file_path = self.file_path_var.get().strip()
        if not file_path:
            messagebox.showwarning("No file selected", "Select a PBIP file first.")
            return

        mapping = build_mapping(self.gather_table_rows(), self.gather_column_rows())
        project = {"path": file_path}

        self.log("--- Run Migration (Test) ---")
        self.log(f"Project: {json.dumps(project, indent=2)}")
        self.log(f"Mapping: {json.dumps(mapping, indent=2)}")

        engine = MigrationEngine(operations=[TableMapper()])
        engine.run(project, mapping)

        self.log(
            "Migration engine run complete. Note: operations are stubs, so no "
            "PBIP files were actually modified."
        )

    def log(self, message):
        print(message)
        self.output_text.configure(state="normal")
        self.output_text.insert("end", message + "\n")
        self.output_text.see("end")
        self.output_text.configure(state="disabled")


def main():
    app = MigratorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
