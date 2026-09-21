import json
import os
import uuid
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from dataclasses import dataclass, asdict, field

DATA_FILE = os.path.join(os.path.expanduser("~"), ".todo_app_data.json")

PRIORITIES = ["Low", "Medium", "High"]
PRIORITY_COLORS = {"Low": "#2e7d32", "Medium": "#e65100", "High": "#c62828"}

@dataclass
class Task:
    id: str
    title: str
    description: str = ""
    priority: str = "Medium"
    due_date: str = ""
    completed: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(d):
        known = {"id", "title", "description", "priority", "due_date",
                 "completed", "created_at"}
        return Task(**{k: v for k, v in d.items() if k in known})


class TaskStore:
    """Handles loading and saving tasks to a local JSON file."""

    def __init__(self, path=DATA_FILE):
        self.path = path
        self.tasks = []
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                self.tasks = [Task.from_dict(t) for t in raw]
            except (json.JSONDecodeError, TypeError, KeyError):
                self.tasks = []
        else:
            self.tasks = []

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in self.tasks], f, indent=2)

    def add(self, task: Task):
        self.tasks.append(task)
        self.save()

    def update(self, task_id, **kwargs):
        for t in self.tasks:
            if t.id == task_id:
                for k, v in kwargs.items():
                    setattr(t, k, v)
                self.save()
                return t
        return None

    def delete(self, task_id):
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self.save()

    def get(self, task_id):
        for t in self.tasks:
            if t.id == task_id:
                return t
        return None

class TaskDialog(tk.Toplevel):
    """Modal dialog used for both adding a new task and editing one."""

    def __init__(self, parent, title="Add Task", task=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        self.transient(parent)
        self.grab_set()

        pad = {"padx": 10, "pady": 6}

        ttk.Label(self, text="Title:").grid(row=0, column=0, sticky="w", **pad)
        self.title_var = tk.StringVar(value=task.title if task else "")
        title_entry = ttk.Entry(self, textvariable=self.title_var, width=40)
        title_entry.grid(row=0, column=1, **pad)

        ttk.Label(self, text="Description:").grid(row=1, column=0, sticky="nw", **pad)
        self.desc_text = tk.Text(self, width=30, height=4)
        self.desc_text.grid(row=1, column=1, **pad)
        if task:
            self.desc_text.insert("1.0", task.description)

        ttk.Label(self, text="Priority:").grid(row=2, column=0, sticky="w", **pad)
        self.priority_var = tk.StringVar(value=task.priority if task else "Medium")
        ttk.Combobox(self, textvariable=self.priority_var, values=PRIORITIES,
                     state="readonly", width=15).grid(row=2, column=1, sticky="w", **pad)

        ttk.Label(self, text="Due date (YYYY-MM-DD):").grid(row=3, column=0, sticky="w", **pad)
        self.due_var = tk.StringVar(value=task.due_date if task else "")
        ttk.Entry(self, textvariable=self.due_var, width=15).grid(row=3, column=1, sticky="w", **pad)

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Save", command=self.on_save).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)

        self.bind("<Return>", lambda e: self.on_save())
        self.bind("<Escape>", lambda e: self.destroy())
        self.after(50, title_entry.focus_force)

    def on_save(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Missing title", "Please enter a task title.", parent=self)
            return

        due = self.due_var.get().strip()
        if due:
            try:
                datetime.strptime(due, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning(
                    "Invalid date", "Due date must be in YYYY-MM-DD format.", parent=self
                )
                return

        self.result = {
            "title": title,
            "description": self.desc_text.get("1.0", "end").strip(),
            "priority": self.priority_var.get(),
            "due_date": due,
        }
        self.destroy()

class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("To-Do List")
        self.geometry("800x540")
        self.minsize(640, 420)

        self.store = TaskStore()
        self.filter_var = tk.StringVar(value="All")
        self.search_var = tk.StringVar()
        self.sort_var = tk.StringVar(value="Created")

        self._build_style()
        self._build_ui()
        self.refresh_list()

    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def _build_ui(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        ttk.Button(top, text="+ Add Task", command=self.add_task).pack(side="left")
        ttk.Button(top, text="Edit", command=self.edit_task).pack(side="left", padx=5)
        ttk.Button(top, text="Delete", command=self.delete_task).pack(side="left")
        ttk.Button(top, text="Toggle Complete", command=self.toggle_complete).pack(
            side="left", padx=5
        )

        ttk.Label(top, text="Filter:").pack(side="left", padx=(20, 4))
        filter_box = ttk.Combobox(
            top, textvariable=self.filter_var, values=["All", "Pending", "Completed"],
            state="readonly", width=10,
        )
        filter_box.pack(side="left")
        filter_box.bind("<<ComboboxSelected>>", lambda e: self.refresh_list())

        ttk.Label(top, text="Sort by:").pack(side="left", padx=(20, 4))
        sort_box = ttk.Combobox(
            top, textvariable=self.sort_var,
            values=["Created", "Priority", "Due Date", "Title"],
            state="readonly", width=10,
        )
        sort_box.pack(side="left")
        sort_box.bind("<<ComboboxSelected>>", lambda e: self.refresh_list())

        search_frame = ttk.Frame(self, padding=(10, 0))
        search_frame.pack(fill="x")
        ttk.Label(search_frame, text="Search:").pack(side="left")
        ttk.Entry(search_frame, textvariable=self.search_var).pack(
            side="left", fill="x", expand=True, padx=6
        )
        self.search_var.trace_add("write", lambda *a: self.refresh_list())

        columns = ("status", "title", "priority", "due", "created")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("status", text="Done")
        self.tree.heading("title", text="Title")
        self.tree.heading("priority", text="Priority")
        self.tree.heading("due", text="Due Date")
        self.tree.heading("created", text="Created")

        self.tree.column("status", width=60, anchor="center")
        self.tree.column("title", width=320, anchor="w")
        self.tree.column("priority", width=90, anchor="center")
        self.tree.column("due", width=100, anchor="center")
        self.tree.column("created", width=140, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", lambda e: self.edit_task())

        for p, color in PRIORITY_COLORS.items():
            self.tree.tag_configure(f"priority_{p}", foreground=color)
        self.tree.tag_configure("completed", foreground="#888888")

        self.status_bar = ttk.Label(self, text="", anchor="w", padding=(10, 4))
        self.status_bar.pack(fill="x", side="bottom")

    def _filtered_sorted_tasks(self):
        tasks = self.store.tasks

        f = self.filter_var.get()
        if f == "Pending":
            tasks = [t for t in tasks if not t.completed]
        elif f == "Completed":
            tasks = [t for t in tasks if t.completed]

        q = self.search_var.get().strip().lower()
        if q:
            tasks = [
                t for t in tasks
                if q in t.title.lower() or q in t.description.lower()
            ]

        sort = self.sort_var.get()
        if sort == "Priority":
            order = {"High": 0, "Medium": 1, "Low": 2}
            tasks = sorted(tasks, key=lambda t: order.get(t.priority, 1))
        elif sort == "Due Date":
            tasks = sorted(tasks, key=lambda t: (t.due_date == "", t.due_date))
        elif sort == "Title":
            tasks = sorted(tasks, key=lambda t: t.title.lower())
        else:
            tasks = sorted(tasks, key=lambda t: t.created_at)
        return tasks

    def refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        tasks = self._filtered_sorted_tasks()
        for t in tasks:
            status = "\u2714" if t.completed else "\u2014"
            created = t.created_at.split("T")[0]
            tags = [f"priority_{t.priority}"]
            if t.completed:
                tags.append("completed")
            self.tree.insert(
                "", "end", iid=t.id,
                values=(status, t.title, t.priority, t.due_date or "\u2014", created),
                tags=tags,
            )
        total = len(self.store.tasks)
        done = len([t for t in self.store.tasks if t.completed])
        self.status_bar.config(
            text=f"{total} task(s) total  \u00b7  {done} completed  \u00b7  {total - done} pending"
        )

    def _selected_task(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.store.get(sel[0])

    def add_task(self):
        dlg = TaskDialog(self, title="Add Task")
        self.wait_window(dlg)
        if dlg.result:
            task = Task(id=str(uuid.uuid4()), **dlg.result)
            self.store.add(task)
            self.refresh_list()

    def edit_task(self):
        task = self._selected_task()
        if not task:
            messagebox.showinfo("No selection", "Please select a task to edit.")
            return
        dlg = TaskDialog(self, title="Edit Task", task=task)
        self.wait_window(dlg)
        if dlg.result:
            self.store.update(task.id, **dlg.result)
            self.refresh_list()

    def delete_task(self):
        task = self._selected_task()
        if not task:
            messagebox.showinfo("No selection", "Please select a task to delete.")
            return
        if messagebox.askyesno("Confirm delete", f"Delete task '{task.title}'?"):
            self.store.delete(task.id)
            self.refresh_list()

    def toggle_complete(self):
        task = self._selected_task()
        if not task:
            messagebox.showinfo("No selection", "Please select a task to toggle.")
            return
        self.store.update(task.id, completed=not task.completed)
        self.refresh_list()


if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()
