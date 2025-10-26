import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import yaml

class NewsEntryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("News Entry → Append to YAML")
        self.root.geometry("700x600")

        # --- Fonts & Styles ---
        style = ttk.Style()
        style.configure("TLabel", font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI", 11))
        style.configure("TEntry", font=("Segoe UI", 11))

        self._build_form()

    def _build_form(self):
        frame = ttk.Frame(self.root, padding=15)
        frame.pack(fill="both", expand=True)

        # --- Date ---
        ttk.Label(frame, text="Date (MM/DD/YY):").grid(row=0, column=0, sticky="w", pady=5)
        self.date_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.date_var, width=20).grid(row=0, column=1, sticky="w")

        # --- Title ---
        ttk.Label(frame, text="Title:").grid(row=1, column=0, sticky="w", pady=5)
        self.title_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.title_var, width=70).grid(row=1, column=1, sticky="w")

        # --- Tags ---
        ttk.Label(frame, text="Tags (comma separated):").grid(row=2, column=0, sticky="w", pady=5)
        self.tags_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.tags_var, width=70).grid(row=2, column=1, sticky="w")

        # --- Content ---
        ttk.Label(frame, text="Content (optional):").grid(row=3, column=0, sticky="nw", pady=5)
        self.content_text = scrolledtext.ScrolledText(frame, width=60, height=6, wrap="word", font=("Consolas", 10))
        self.content_text.grid(row=3, column=1, sticky="w")

        # --- Buttons ---
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=1, sticky="w", pady=20)
        ttk.Button(btn_frame, text="Save News", command=self.save_news).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Clear Fields", command=self.clear_fields).grid(row=0, column=1, padx=5)

        # Add padding between rows
        for i in range(5):
            frame.grid_rowconfigure(i, pad=8)

    def clear_fields(self):
        self.date_var.set("")
        self.title_var.set("")
        self.tags_var.set("")
        self.content_text.delete("1.0", tk.END)

    def save_news(self):
        date = self.date_var.get().strip()
        title = self.title_var.get().strip()
        tags = [tag.strip() for tag in self.tags_var.get().split(",") if tag.strip()]
        content = self.content_text.get("1.0", tk.END).strip()

        if not date or not title:
            messagebox.showwarning("Missing Fields", "Date and Title are required.")
            return

        entry = {
            "date": date,
            "title": title,
            "tags": tags,
            "content": content
        }

        yaml_path = os.path.join("data", "news.yml")
        os.makedirs(os.path.dirname(yaml_path), exist_ok=True)

        # Load existing YAML
        if os.path.exists(yaml_path):
            with open(yaml_path, "r", encoding="utf-8") as f:
                try:
                    news_list = yaml.safe_load(f) or []
                except yaml.YAMLError:
                    news_list = []
        else:
            news_list = []

        news_list.append(entry)

        # Save back to YAML
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(news_list, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        messagebox.showinfo("Success", f"News entry added successfully to {yaml_path}")
        self.clear_fields()


if __name__ == "__main__":
    root = tk.Tk()
    app = NewsEntryApp(root)
    root.mainloop()
