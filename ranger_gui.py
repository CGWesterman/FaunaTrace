#!/usr/bin/env python3
"""Simple Tkinter GUI to visualize and run data pipeline actions.

Features:
- Load CSV (default or choose file)
- Preview first N rows in a Treeview
- Drop selected columns
- Concatenate chosen columns into a new column
- Compute SHA256 hash of a column or concatenation
- Save cleaned CSV

This is intentionally lightweight and uses functions from data_pipeline.py
for reading/writing where possible.
"""
APP_TITLE = "FaunaTrace Ranger Portal"

import hashlib
import os
import traceback
from pathlib import Path
os.environ.setdefault("TK_SILENCE_DEPRECATION", "1")
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
from tkinter.scrolledtext import ScrolledText

import pandas as pd

try:
    from data_pipeline import load_data, write_clean_data, CSV_REL, OUT_REL, new_sighting
except Exception:
    # If import fails, fall back to local definitions (will log error)
    load_data = None
    write_clean_data = None
    CSV_REL = Path.cwd() / "data" / "raw" / "raw" / "animal_sightings.csv"
    OUT_REL = Path.cwd() / "data" / "clean" / "animal_sightings_clean.csv"


class DataPipelineGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1100x700")

        self.df: pd.DataFrame | None = None
        self.current_path: Path | None = None

        self._build_ui()

    def _build_ui(self):
        # Top frame with buttons
        top = ttk.Frame(self)
        top.pack(side=tk.TOP, fill=tk.X, padx=6, pady=6)

        ttk.Button(top, text="Load default CSV", command=self.load_default).pack(side=tk.LEFT)
        ttk.Button(top, text="Open CSV...", command=self.open_file).pack(side=tk.LEFT)
        ttk.Button(top, text="Preview", command=self.preview).pack(side=tk.LEFT)
        ttk.Button(top, text="Save Clean CSV", command=self.save_csv).pack(side=tk.LEFT)
        #ttk.Button(top, text="Create Sighting", command=self.new_sighting).pack(side=tk.LEFT)

        ttk.Button(top, text="Drop Selected Columns", command=self.drop_selected_columns).pack(side=tk.LEFT, padx=6)

        # Concatenate controls
        ttk.Label(top, text="Concat cols (comma sep):").pack(side=tk.LEFT, padx=(12, 2))
        self.concat_entry = ttk.Entry(top, width=30)
        self.concat_entry.pack(side=tk.LEFT)
        ttk.Button(top, text="Concat -> col", command=self.concat_columns_prompt).pack(side=tk.LEFT, padx=4)

        ttk.Label(top, text="Hash col name:").pack(side=tk.LEFT, padx=(12, 2))
        self.hash_entry = ttk.Entry(top, width=15)
        self.hash_entry.pack(side=tk.LEFT)
        ttk.Button(top, text="Hash from col", command=self.hash_from_col_prompt).pack(side=tk.LEFT, padx=4)

        # Middle: columns list and treeview
        middle = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        middle.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Left: columns listbox
        left = ttk.Frame(middle)
        middle.add(left, weight=1)
        ttk.Label(left, text="Columns").pack(anchor=tk.W)
        self.col_listbox = tk.Listbox(left, selectmode=tk.EXTENDED, exportselection=False)
        self.col_listbox.pack(fill=tk.BOTH, expand=True)

        # Right: data preview
        right = ttk.Frame(middle)
        middle.add(right, weight=3)
        ttk.Label(right, text="Preview (first 100 rows)").pack(anchor=tk.W)
        self.tree = ttk.Treeview(right, show='headings')
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bottom: log
        bottom = ttk.Frame(self)
        bottom.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Label(bottom, text="Log").pack(anchor=tk.W)
        self.log = ScrolledText(bottom, height=8)
        self.log.pack(fill=tk.BOTH)

    def log_msg(self, *parts):
        msg = " ".join(str(p) for p in parts)
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        print(msg)

    def load_default(self):
        try:
            path = CSV_REL
            self.load_path(path)
        except Exception as e:
            self.log_msg("Error loading default:", e)
            self.log_msg(traceback.format_exc())

    def open_file(self):
        p = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*")])
        if not p:
            return
        self.load_path(Path(p))

    def load_path(self, path: Path):
        self.log_msg("Loading:", path)
        try:
            if load_data:
                df = load_data(path)
            else:
                # fallback: basic pandas read
                df = pd.read_csv(path)
            self.df = df
            self.current_path = Path(path)
            self.log_msg(f"Loaded {len(df)} rows, {len(df.columns)} columns")
            self._populate_columns()
            self.preview()
        except Exception as e:
            self.log_msg("Error loading file:", e)
            self.log_msg(traceback.format_exc())

    def _populate_columns(self):
        self.col_listbox.delete(0, tk.END)
        if self.df is None:
            return
        for c in self.df.columns:
            self.col_listbox.insert(tk.END, c)

    def preview(self):
        if self.df is None:
            self.log_msg("No DataFrame loaded")
            return
        df = self.df
        self.tree.delete(*self.tree.get_children())
        cols = list(df.columns)
        # Limit columns to avoid UI blowup
        if len(cols) > 50:
            cols = cols[:50]
        self.tree.config(columns=cols)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120, anchor='w')

        for _, row in df.head(100)[cols].iterrows():
            values = [self._cell_str(row[c]) for c in cols]
            self.tree.insert('', tk.END, values=values)

    def _cell_str(self, v):
        if pd.isna(v):
            return ""
        return str(v)

    def drop_selected_columns(self):
        if self.df is None:
            self.log_msg("No data loaded")
            return
        sel = [self.col_listbox.get(i) for i in self.col_listbox.curselection()]
        if not sel:
            self.log_msg("No columns selected to drop")
            return
        self.log_msg("Dropping columns:", sel)
        try:
            self.df = self.df.drop(columns=sel, errors='ignore')
            self._populate_columns()
            self.preview()
        except Exception as e:
            self.log_msg("Error dropping columns:", e)
            self.log_msg(traceback.format_exc())

    def concat_columns_prompt(self):
        if self.df is None:
            self.log_msg("No data loaded")
            return
        cols_text = self.concat_entry.get().strip()
        if not cols_text:
            self.log_msg("Please enter columns to concatenate (comma separated)")
            return
        cols = [c.strip() for c in cols_text.split(',') if c.strip()]
        new_col = simpledialog.askstring("New column", "Name of concatenated column:", parent=self)
        if not new_col:
            return
        self.concat_columns(cols, new_col)

    def concat_columns(self, cols, new_col, sep='||'):
        self.log_msg("Concatenating columns", cols, "->", new_col)
        try:
            for c in cols:
                if c not in self.df.columns:
                    self.df[c] = ''
            self.df[new_col] = self.df[cols].fillna('').astype(str).agg(sep.join, axis=1)
            self._populate_columns()
            self.preview()
        except Exception as e:
            self.log_msg("Error concatenating:", e)
            self.log_msg(traceback.format_exc())

    def hash_from_col_prompt(self):
        if self.df is None:
            self.log_msg("No data loaded")
            return
        col = self.hash_entry.get().strip()
        if not col:
            col = simpledialog.askstring("Column to hash", "Column name to hash (or leave blank to use last concatenated):", parent=self)
            if not col:
                self.log_msg("No column provided for hashing")
                return
        new_col = simpledialog.askstring("Hash column name", "Name for hash column:", parent=self)
        if not new_col:
            return
        self.hash_column(col, new_col)

    def hash_column(self, source_col, new_col):
        self.log_msg("Hashing column", source_col, "->", new_col)
        try:
            s = self.df[source_col].fillna('').astype(str)
            self.df[new_col] = s.apply(lambda v: hashlib.sha256(v.encode('utf-8')).hexdigest())
            self._populate_columns()
            self.preview()
        except Exception as e:
            self.log_msg("Error hashing:", e)
            self.log_msg(traceback.format_exc())

    def save_csv(self):
        if self.df is None:
            self.log_msg("No data to save")
            return
        p = filedialog.asksaveasfilename(defaultextension='.csv', initialfile=OUT_REL.name)
        if not p:
            return
        out = Path(p)
        try:
            if write_clean_data:
                write_clean_data(self.df, out)
            else:
                out.parent.mkdir(parents=True, exist_ok=True)
                self.df.to_csv(out, index=False, encoding='utf-8')
                self.log_msg(f"Wrote cleaned CSV to {out} (rows={len(self.df)})")
        except Exception as e:
            self.log_msg("Error saving CSV:", e)
            self.log_msg(traceback.format_exc())


def main():
    app = DataPipelineGUI()
    app.mainloop()


if __name__ == '__main__':
    main()
