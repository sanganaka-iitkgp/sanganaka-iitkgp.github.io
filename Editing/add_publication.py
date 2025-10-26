import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pandas as pd
import os

class PublicationEntryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Publication Entry → Append to CSV")
        self.root.geometry("700x650")

        # --- Fonts & Styles ---
        style = ttk.Style()
        style.configure("TLabel", font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI", 11))
        style.configure("TEntry", font=("Segoe UI", 11))

        self._build_form()

    def _build_form(self):
        frame = ttk.Frame(self.root, padding=15)
        frame.pack(fill="both", expand=True)

        # --- Title ---
        ttk.Label(frame, text="Title:").grid(row=0, column=0, sticky="w", pady=5)
        self.title_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.title_var, width=70).grid(row=0, column=1, sticky="w")

        # --- Abstract ---
        ttk.Label(frame, text="Abstract:").grid(row=1, column=0, sticky="nw", pady=5)
        self.abstract_text = scrolledtext.ScrolledText(frame, width=60, height=6, wrap="word", font=("Consolas", 10))
        self.abstract_text.grid(row=1, column=1, sticky="w")

        # --- Authors ---
        ttk.Label(frame, text="Authors (comma separated):").grid(row=2, column=0, sticky="w", pady=5)
        self.authors_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.authors_var, width=70).grid(row=2, column=1, sticky="w")

        # --- Issued ---
        ttk.Label(frame, text="Issued (yyyy/mm/dd):").grid(row=3, column=0, sticky="w", pady=5)
        self.issued_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.issued_var, width=30).grid(row=3, column=1, sticky="w")

        # --- Type Dropdown ---
        ttk.Label(frame, text="Type:").grid(row=4, column=0, sticky="w", pady=5)
        self.type_var = tk.StringVar(value="conference")
        type_options = ["archive", "book", "conference", "journal", "thesis", "other"]
        ttk.OptionMenu(frame, self.type_var, self.type_var.get(), *type_options).grid(row=4, column=1, sticky="w")

        # --- Type Name ---
        ttk.Label(frame, text="Type Name (e.g. ACL 2025):").grid(row=5, column=0, sticky="w", pady=5)
        self.type_name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.type_name_var, width=70).grid(row=5, column=1, sticky="w")

        # --- Link ---
        ttk.Label(frame, text="Link:").grid(row=6, column=0, sticky="w", pady=5)
        self.link_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.link_var, width=70).grid(row=6, column=1, sticky="w")

        # --- Buttons ---
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=7, column=1, sticky="w", pady=20)
        ttk.Button(btn_frame, text="Save Publication", command=self.save_publication).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Clear Fields", command=self.clear_fields).grid(row=0, column=1, padx=5)

        # Add padding between rows
        for i in range(8):
            frame.grid_rowconfigure(i, pad=8)

    def clear_fields(self):
        self.title_var.set("")
        self.abstract_text.delete("1.0", tk.END)
        self.authors_var.set("")
        self.issued_var.set("")
        self.type_var.set("conference")
        self.type_name_var.set("")
        self.link_var.set("")

    def save_publication(self):
        title = self.title_var.get().strip()
        abstract = self.abstract_text.get("1.0", tk.END).strip()
        authors = self.authors_var.get().strip()
        issued = self.issued_var.get().strip()
        type_ = self.type_var.get().strip()
        type_name = self.type_name_var.get().strip()
        link = self.link_var.get().strip()

        if not title or not authors or not issued:
            messagebox.showwarning("Missing Fields", "Title, Authors, and Issued are required.")
            return

        row = {
            "title": title,
            "abstract": abstract,
            "author": authors,
            "issued": issued,
            "type": type_,
            "type-name": type_name,
            "link": link
        }

        csv_path = os.path.join("data", "publications.csv")
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)

        # Load existing CSV or create new
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        else:
            df = pd.DataFrame([row])

        df.to_csv(csv_path, index=False, encoding="utf-8")
        messagebox.showinfo("Success", f"Publication added successfully to {csv_path}")
        self.clear_fields()


if __name__ == "__main__":
    root = tk.Tk()
    app = PublicationEntryApp(root)
    root.mainloop()
