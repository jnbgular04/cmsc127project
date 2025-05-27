import tkinter as tk
from tkinter import ttk
import mysql.connector as mariadb
from tkinter import messagebox

class OrgEventPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_org = ""

        # Title
        tk.Label(self, text="Organization Events", font=("Arial", 16)).pack(pady=10)

        # Treeview to show current events
        self.tree = ttk.Treeview(self, columns=("Organization", "Event"), show="headings")
        self.tree.heading("Organization", text="Organization")
        self.tree.heading("Event", text="Event")
        self.tree.column("Organization", anchor=tk.CENTER, width=150)
        self.tree.column("Event", anchor=tk.CENTER, width=200)
        self.tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        self.org_name_var = tk.StringVar()
        tk.Label(form_frame, textvariable=self.org_name_var, font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, padx=5, pady=5)


        tk.Label(form_frame, text="Event Name:").grid(row=1, column=0, padx=5, pady=5)
        self.event_entry = tk.Entry(form_frame)
        self.event_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(self, text="Add Event", command=self.add_event).pack(pady=10)

        tk.Button(self, text="Back to Org Admin Page", command=lambda: controller.show_frame("OrgAdminHomePage")).pack(pady=10)

        self.load_events()

   
    def load_organization(self, org_name):
        self.current_org = org_name
        self.org_name_var.set(f"Organization: {org_name}")
        self.load_events()

    def load_events(self):
        org_name =  self.current_org
        print(self.current_org)
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("SELECT org_name, event FROM organization_event WHERE org_name = %s", (org_name,))
            for org_name, event in cursor.fetchall():
                self.tree.insert("", "end", values=(org_name, event))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load events:\n{e}")

    def add_event(self):
        org_name = getattr(self, "current_org", None)  # safely get org_name
        event = self.event_entry.get().strip()

        if not org_name or not event:
            messagebox.showwarning("Input Error", "Both Organization and Event Name are required.")
            return

        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("INSERT INTO organization_event (org_name, event) VALUES (%s, %s)", (org_name, event))
            self.controller.mydb.commit()
            messagebox.showinfo("Success", "Event added successfully.")
            self.event_entry.delete(0, tk.END)
            self.load_events()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))