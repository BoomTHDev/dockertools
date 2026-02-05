import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time

# ------------------ utils ------------------
def run_cmd(cmd):
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return out.decode()
    except subprocess.CalledProcessError as e:
        return e.output.decode()

# ------------------ GUI ------------------
class DockerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🐳 Docker Control Center")
        self.geometry("1100x600")

        self.create_layout()
        self.show_containers()

    def create_layout(self):
        # Sidebar
        sidebar = tk.Frame(self, width=180, bg="#222")
        sidebar.pack(side="left", fill="y")

        btns = [
            ("📦 Containers", self.show_containers),
            ("🖼 Images", self.show_images),
            ("📊 Stats", self.show_stats),
            ("🔄 Refresh", self.refresh),
        ]

        for text, cmd in btns:
            b = tk.Button(sidebar, text=text, command=cmd, fg="white",
                          bg="#333", relief="flat", height=2)
            b.pack(fill="x", pady=2, padx=5)

        # Main area
        self.main = tk.Frame(self)
        self.main.pack(side="right", fill="both", expand=True)

        self.tree = ttk.Treeview(self.main)
        self.tree.pack(fill="both", expand=True)

        # Action buttons
        action = tk.Frame(self)
        action.pack(fill="x")

        tk.Button(action, text="▶ Start", command=self.start_container).pack(side="left", padx=5)
        tk.Button(action, text="⏹ Stop", command=self.stop_container).pack(side="left", padx=5)

    # ------------------ views ------------------
    def clear_tree(self):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ()
        self.tree["show"] = "headings"

    def show_containers(self):
        self.clear_tree()
        self.tree["columns"] = ("ID", "Name", "Status", "Image")

        for c in self.tree["columns"]:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=200)

        out = run_cmd(
            'docker ps -a --format "{{.ID}}|{{.Names}}|{{.Status}}|{{.Image}}"'
        )
        for line in out.splitlines():
            self.tree.insert("", "end", values=line.split("|"))

    def show_images(self):
        self.clear_tree()
        self.tree["columns"] = ("Repository", "Tag", "ID", "Size")

        for c in self.tree["columns"]:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=220)

        out = run_cmd(
            'docker images --format "{{.Repository}}|{{.Tag}}|{{.ID}}|{{.Size}}"'
        )
        for line in out.splitlines():
            self.tree.insert("", "end", values=line.split("|"))

    def show_stats(self):
        self.clear_tree()
        self.tree["columns"] = ("Name", "CPU %", "Mem Usage", "Net IO", "Block IO")

        for c in self.tree["columns"]:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=220)

        out = run_cmd(
            'docker stats --no-stream '
            '--format "{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}|{{.NetIO}}|{{.BlockIO}}"'
        )
        for line in out.splitlines():
            self.tree.insert("", "end", values=line.split("|"))

    # ------------------ actions ------------------
    def get_selected_container(self):
        item = self.tree.focus()
        if not item:
            return None
        return self.tree.item(item)["values"][0]

    def start_container(self):
        cid = self.get_selected_container()
        if not cid:
            messagebox.showwarning("เลือกก่อน", "กรุณาเลือก container")
            return
        run_cmd(f"docker start {cid}")
        self.refresh()

    def stop_container(self):
        cid = self.get_selected_container()
        if not cid:
            messagebox.showwarning("เลือกก่อน", "กรุณาเลือก container")
            return
        run_cmd(f"docker stop {cid}")
        self.refresh()

    def refresh(self):
        # รีเฟรชตามหน้าปัจจุบัน
        cols = self.tree["columns"]
        if "CPU %" in cols:
            self.show_stats()
        elif "Status" in cols:
            self.show_containers()
        else:
            self.show_images()

# ------------------ run ------------------
if __name__ == "__main__":
    app = DockerGUI()
    app.mainloop()
