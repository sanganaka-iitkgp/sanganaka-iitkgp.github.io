import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import sys
import os

# --- Dependency check and install ---
REQUIRED_PACKAGES = ["tkinter", "os", "re", "yaml", "pandas"]

def check_install_packages():
    missing = []
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            messagebox.showinfo("Packages Installed", f"Installed missing packages: {', '.join(missing)}")
        except Exception as e:
            messagebox.showerror("Package Installation Error", f"Error installing packages: {e}")

# --- Git commands ---
def git_add_status(output_widget):
    try:
        subprocess.run(["git", "add", "."], check=True)
        result = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, check=True)
        output_widget.config(state="normal")
        output_widget.delete("1.0", tk.END)
        if result.stdout.strip():
            output_widget.insert(tk.END, result.stdout.strip())
        else:
            output_widget.insert(tk.END, "No changes detected.")
        output_widget.config(state="disabled")
    except Exception as e:
        messagebox.showerror("Git Error", f"Error during git add/status:\n{e}")

def git_commit_push(message_entry, output_widget):
    commit_msg = message_entry.get().strip()
    if not commit_msg:
        messagebox.showwarning("Missing Commit Message", "Please enter a commit message.")
        return
    try:
        subprocess.run(["git", "commit", "-m", commit_msg], check=True, capture_output=True, text=True)
        try:
            subprocess.run(["git", "push"], check=True, capture_output=True, text=True)
            messagebox.showinfo("Success", "Changes committed and pushed successfully!")
        except subprocess.CalledProcessError as push_err:
            err_msg = push_err.stderr
            if "set upstream" in err_msg:
                # Try to set upstream and push
                try:
                    subprocess.run(["git", "push", "--set-upstream", "origin", "master"], check=True)
                    messagebox.showinfo("Success", "Changes committed and pushed successfully with upstream!")
                except Exception as e:
                    messagebox.showerror("Git Push Error", f"Push failed even after setting upstream:\n{e}")
            else:
                messagebox.showerror("Git Push Error", f"Push failed:\n{err_msg}")
    except subprocess.CalledProcessError as commit_err:
        messagebox.showwarning("Git Commit", f"No changes to commit or error:\n{commit_err.stderr}")

# --- Open editing scripts ---
def open_editor(script_name):
    script_path = os.path.join(os.getcwd(), script_name)
    if os.path.exists(script_path):
        os.system(f"{sys.executable} {script_path}")
    else:
        messagebox.showerror("File Not Found", f"{script_name} not found!")

# --- GUI ---
root = tk.Tk()
root.title("Editing Home Page")
root.geometry("800x700")

check_install_packages()  # check on launch

main_frame = ttk.Frame(root, padding=10)
main_frame.pack(fill="both", expand=True)

# --- Editor buttons ---
ttk.Label(main_frame, text="Select Editor Script:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=5)
editor_frame = ttk.Frame(main_frame)
editor_frame.pack(fill="x", pady=5)
ttk.Button(editor_frame, text="Entry Member", command=lambda: open_editor(os.path.join("Editing", "add_member.py"))).pack(side="left", padx=5)
ttk.Button(editor_frame, text="Entry News", command=lambda: open_editor(os.path.join("Editing", "add_news.py"))).pack(side="left", padx=5)
ttk.Button(editor_frame, text="Entry Publication", command=lambda: open_editor(os.path.join("Editing", "add_publication.py"))).pack(side="left", padx=5)

# --- Changes Block ---
ttk.Label(main_frame, text="Changes Block (Git Status):", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=10)
changes_text = scrolledtext.ScrolledText(main_frame, height=10, state="disabled", font=("Consolas", 10))
changes_text.pack(fill="both", expand=False, pady=5)
ttk.Button(main_frame, text="Refresh Changes", command=lambda: git_add_status(changes_text)).pack(pady=5)

# --- Commit & Push Block ---
ttk.Label(main_frame, text="Commit & Push Changes:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=10)
commit_frame = ttk.Frame(main_frame)
commit_frame.pack(fill="x", pady=5)
ttk.Label(commit_frame, text="Commit Message:").pack(side="left", padx=5)
commit_msg_entry = ttk.Entry(commit_frame, width=50)
commit_msg_entry.pack(side="left", padx=5)
ttk.Button(commit_frame, text="Commit & Push", command=lambda: git_commit_push(commit_msg_entry, changes_text)).pack(side="left", padx=5)

root.mainloop()
