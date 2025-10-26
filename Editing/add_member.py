import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font
import os
import re

PLACEHOLDER = "placeholder.jpg"
IMAGES_PATH_HINT = "images/teams/"

class EducationRow:
    def __init__(self, parent, remove_callback):
        self.frame = ttk.Frame(parent, padding=(0,6))
        # Institute
        ttk.Label(self.frame, text="Institute").grid(row=0, column=0, sticky="w")
        self.institute = ttk.Entry(self.frame, width=60)
        self.institute.grid(row=0, column=1, sticky="w")
        # Degree
        ttk.Label(self.frame, text="Degree").grid(row=1, column=0, sticky="w")
        self.degree = ttk.Entry(self.frame, width=60)
        self.degree.grid(row=1, column=1, sticky="w")
        # Duration
        ttk.Label(self.frame, text="Duration").grid(row=2, column=0, sticky="w")
        self.duration = ttk.Entry(self.frame, width=60)
        self.duration.grid(row=2, column=1, sticky="w")
        # Description (multi-line)
        ttk.Label(self.frame, text="Description").grid(row=3, column=0, sticky="nw")
        self.description = scrolledtext.ScrolledText(self.frame, width=44, height=4, wrap="word")
        self.description.grid(row=3, column=1, sticky="w")
        # Remove button
        self.remove_btn = ttk.Button(self.frame, text="Remove", command=self._on_remove)
        self.remove_btn.grid(row=0, column=2, sticky="ne")
        self._remove_callback = remove_callback

    def _on_remove(self):
        if messagebox.askyesno("Remove Education", "Remove this education entry?"):
            self.frame.destroy()
            self._remove_callback(self)

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def get_data(self):
        return {
            "institute": self.institute.get().strip(),
            "degree": self.degree.get().strip(),
            "duration": self.duration.get().strip(),
            "description": self.description.get("1.0", "end").strip()
        }

class TeamProfileApp:
    def __init__(self, root):
        self.root = root
        root.title("Team Profile → Markdown")
        root.geometry("950x800")

        # Fonts
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=11, family="Segoe UI")
        text_font = font.nametofont("TkTextFont")
        text_font.configure(size=11, family="Consolas")
        root.option_add("*Font", default_font)

        # Scrollable main frame
        main_canvas = tk.Canvas(root)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
        main_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        main_canvas.pack(side="left", fill="both", expand=True)

        self.main_frame = ttk.Frame(main_canvas, padding=10)
        main_canvas.create_window((0,0), window=self.main_frame, anchor="nw")
        self.main_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))

        # Bind mousewheel
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.main_frame.bind("<Enter>", lambda e: self.main_frame.bind_all("<MouseWheel>", _on_mousewheel))
        self.main_frame.bind("<Leave>", lambda e: self.main_frame.unbind_all("<MouseWheel>"))

        # Variables
        self.category = tk.StringVar(value="student")
        self.title = tk.StringVar()
        self.image = tk.StringVar()
        self.role = tk.StringVar()
        self.permalink = tk.StringVar()
        self.socials = {
            "linkedin": tk.StringVar(value="n/a"),
            "google-scholar": tk.StringVar(value="n/a"),
            "github": tk.StringVar(value="n/a"),
            "website": tk.StringVar(value="n/a"),
            "orcid": tk.StringVar(value="n/a"),
        }
        self.education_rows = []

        # Build sections
        self._build_form()
        self._build_education_area()
        self._build_bio_and_actions()
        self._build_output_area()

        # Add one education by default
        self.add_education_row()

    def _build_form(self):
        f = ttk.Frame(self.main_frame)
        f.pack(fill="x", pady=(0,8))

        # Category
        ttk.Label(f, text="Category:").grid(row=0, column=0, sticky="w", padx=2, pady=2)
        cat_cb = ttk.Combobox(f, textvariable=self.category, values=["alumni","scholar","staff","student"], width=20)
        cat_cb.grid(row=0, column=1, sticky="w", padx=2, pady=2)

        # Name
        ttk.Label(f, text="Title (Name):").grid(row=1, column=0, sticky="w", padx=2, pady=2)
        ttk.Entry(f, textvariable=self.title, width=50).grid(row=1, column=1, sticky="w", padx=2, pady=2)

        # Image
        ttk.Label(f, text="Profile Image Name:").grid(row=2, column=0, sticky="w", padx=2, pady=2)
        ttk.Entry(f, textvariable=self.image, width=50).grid(row=2, column=1, sticky="w", padx=2, pady=2)
        ttk.Label(f, text=f"⚠️ Image must be stored in {IMAGES_PATH_HINT} (default -> {PLACEHOLDER})").grid(row=3, column=1, sticky="w", padx=2, pady=(0,8))

        # Role
        ttk.Label(f, text="Role (optional):").grid(row=4, column=0, sticky="w", padx=2, pady=2)
        ttk.Entry(f, textvariable=self.role, width=50).grid(row=4, column=1, sticky="w", padx=2, pady=2)

        # Permalink
        ttk.Label(f, text="Permalink (team/your-permalink):").grid(row=5, column=0, sticky="w", padx=2, pady=2)
        ttk.Entry(f, textvariable=self.permalink, width=50).grid(row=5, column=1, sticky="w", padx=2, pady=2)

        # Social block
        soc_frame = ttk.LabelFrame(self.main_frame, text="Social (defaults: n/a)")
        soc_frame.pack(fill="x", pady=(6,8))
        r = 0
        for k, var in self.socials.items():
            ttk.Label(soc_frame, text=f"{k}:").grid(row=r, column=0, sticky="w", padx=6, pady=2)
            ttk.Entry(soc_frame, textvariable=var, width=80).grid(row=r, column=1, sticky="w", padx=6, pady=2)
            r += 1

    def _build_education_area(self):
        self.edu_container = ttk.LabelFrame(self.main_frame, text="Education (add as many as needed)")
        self.edu_container.pack(fill="both", expand=False, pady=(6,8))
        self.edu_inner = ttk.Frame(self.edu_container)
        self.edu_inner.pack(fill="both", expand=True)
        ttk.Button(self.main_frame, text="+ Add Education", command=self.add_education_row).pack(anchor="w", padx=6, pady=6)

    def add_education_row(self):
        row = EducationRow(self.edu_inner, remove_callback=self._on_remove_edu)
        row.grid(sticky="we", pady=4)
        self.education_rows.append(row)

    def _on_remove_edu(self, row):
        try: self.education_rows.remove(row)
        except ValueError: pass

    def _build_bio_and_actions(self):
        bio_frame = ttk.LabelFrame(self.main_frame, text="Bio")
        bio_frame.pack(fill="both", expand=False, pady=(6,8))
        self.bio_text = scrolledtext.ScrolledText(bio_frame, height=10, wrap="word")
        self.bio_text.pack(fill="both", expand=True, padx=6, pady=6)

        action_frame = ttk.Frame(self.main_frame)
        action_frame.pack(fill="x", pady=(6,8))
        ttk.Button(action_frame, text="Generate Markdown", command=self.generate_markdown).pack(side="left", padx=6)
        ttk.Button(action_frame, text="Save Markdown to file", command=self.save_markdown).pack(side="left", padx=6)

    def _build_output_area(self):
        out_frame = ttk.LabelFrame(self.main_frame, text="Generated Markdown")
        out_frame.pack(fill="both", expand=True, pady=(6,8))
        self.output = scrolledtext.ScrolledText(out_frame, height=18, wrap="word")
        self.output.pack(fill="both", expand=True, padx=6, pady=6)

    def _collect_data(self):
        title = self.title.get().strip()
        category = self.category.get().strip()
        image_name = self.image.get().strip() or PLACEHOLDER
        role = self.role.get().strip()
        permalink = self.permalink.get().strip()
        if permalink and not permalink.startswith("team/"): permalink = "team/"+permalink
        elif not permalink:
            safe_title = title.lower().replace(" ","")
            permalink = f"team/{safe_title}" if safe_title else "team/unknown"

        socials = {k:(v.get().strip() or "n/a") for k,v in self.socials.items()}
        bio = self.bio_text.get("1.0", "end").strip()

        edus = []
        for r in self.education_rows:
            d = r.get_data()
            if not (d["institute"] or d["degree"] or d["duration"] or d["description"]): continue
            edus.append(d)

        image_path = os.path.join(IMAGES_PATH_HINT, image_name)
        image_exists = os.path.exists(image_path)
        return {
            "title": title or "Untitled",
            "category": category or "student",
            "image_name": image_name,
            "image_exists": image_exists,
            "role": role,
            "permalink": permalink,
            "socials": socials,
            "bio": bio,
            "education": edus
        }

    def _format_education_block(self, edu):
        lines=[]
        if edu.get("degree"): lines.append(f"**{edu['degree']}**  ")
        if edu.get("institute"): lines.append(f"**{edu['institute']}**  ")
        if edu.get("duration"): lines.append(f"- {edu['duration']}  ")
        desc = edu.get("description","")
        if desc:
            for dl in [ln.strip() for ln in desc.splitlines() if ln.strip()]:
                lines.append(f"- {dl}" if not dl.startswith("- ") else dl + "  ")
        return "\n".join(lines)

    def generate_markdown(self):
        data = self._collect_data()
        if not data["image_exists"]:
            messagebox.showwarning("Image missing", f"{data['image_name']} not found at {IMAGES_PATH_HINT}")

        md_lines = ["---","layout: member",f"category: {data['category']}",f"title: {data['title']}",f"image: {data['image_name']}"]
        if data.get("role"): md_lines.append(f"role: {data['role']}")
        md_lines.append(f"permalink: '{data['permalink']}'")
        md_lines.append("social:")
        for k,v in data["socials"].items(): md_lines.append(f"    {k}: {v}")
        md_lines.append("education:")
        if data["education"]:
            for edu in data["education"]:
                md_lines.append("  - |")
                for ln in self._format_education_block(edu).splitlines():
                    md_lines.append("    " + ln)
                md_lines.append("")
        else:
            md_lines.append("  - |")
            md_lines.append("    **No formal education entered**  ")
            md_lines.append("")

        md_lines.append("---\n"+data["bio"])
        md_text="\n".join(md_lines).rstrip()+"\n"
        self.output.delete("1.0","end")
        self.output.insert("1.0",md_text)
        self.last_generated = md_text
        return md_text

    def save_markdown(self):
        md_text = getattr(self, "last_generated", None) or self.generate_markdown()
        title = self.title.get().strip() or "untitled"
        safe_title = re.sub(r'[^A-Za-z0-9_-]+', '', title.replace(" ",""))
        target_dir = os.path.join(os.path.dirname(__file__), "..", "_team")
        os.makedirs(target_dir, exist_ok=True)
        filepath = os.path.join(target_dir, f"{safe_title}.md")
        try:
            with open(filepath, "w", encoding="utf-8") as f: f.write(md_text)
            messagebox.showinfo("Saved", f"Markdown saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")

if __name__=="__main__":
    root=tk.Tk()
    app=TeamProfileApp(root)
    root.mainloop()
