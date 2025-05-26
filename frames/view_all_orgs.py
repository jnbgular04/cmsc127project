import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector as mariadb

class OrgsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # --- MAIN CONTAINER: holds everything horizontally ---
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # --- LEFT SIDE: Org controls and treeview ---
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill="both", expand=True)

        # BACK TO HOME BUTTON
        btn_back = tk.Button(self, text="Back to Home", 
                             command=lambda: controller.show_frame("AdminHomePage"))
        btn_back.pack()

        label = tk.Label(left_frame, text="All Organizations", font=("Arial", 16))
        label.pack(pady=10)

        # Treeview
        columns = ("Organization Name",)
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Action Buttons
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(pady=10)

        btn_add = tk.Button(btn_frame, text="Add Organization", command=self.add_organization_prompt)
        btn_add.grid(row=0, column=0, padx=5)

        btn_delete = tk.Button(btn_frame, text="Delete Selected", command=self.delete_organization)
        btn_delete.grid(row=0, column=1, padx=5)

        btn_view = tk.Button(btn_frame, text="View Details", command=self.view_organization_details)
        btn_view.grid(row=0, column=2, padx=5)

        btn_refresh = tk.Button(self, text="Refresh Page", command=self.load_organizations)
        btn_refresh.pack(pady=5)

        # Load organizations into the table
        self.load_organizations()

    def load_organizations(self):
        self.tree.delete(*self.tree.get_children())  # clear table
        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("SELECT org_name FROM organization")
            for (org_name,) in cursor.fetchall():
                self.tree.insert("", "end", values=(org_name,))
        except mariadb.Error as err:
            messagebox.showerror("Database Error", str(err))

    def add_organization_prompt(self):
        popup = tk.Toplevel(self)
        popup.title("Add New Organization")
        popup.grab_set()  # Make the popup modal

        tk.Label(popup, text="Enter Organization Name:").pack(padx=10, pady=(10, 5))

        entry = tk.Entry(popup, width=40)
        entry.pack(padx=10, pady=5)
        entry.focus()

        def on_submit():
            org_name = entry.get().strip()
            if not org_name:
                messagebox.showwarning("Input Error", "Organization name cannot be empty.")
                return
            try:
                cursor = self.controller.mydb.cursor()
                cursor.execute("INSERT INTO organization (org_name) VALUES (%s)", (org_name,))
                self.controller.mydb.commit()
                messagebox.showinfo("Success", f"Organization '{org_name}' added successfully.")
                popup.destroy()
                self.load_organizations()
            except mariadb.Error as err:
                messagebox.showerror("Database Error", str(err))

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add", command=on_submit).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=popup.destroy).pack(side=tk.LEFT, padx=5)

        popup.transient(self)
        popup.geometry("+%d+%d" % (self.winfo_rootx()+100, self.winfo_rooty()+100))


    def delete_organization(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an organization to delete.")
            return

        org_name = self.tree.item(selected_item[0])["values"][0]
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{org_name}'?")
        if not confirm:
            return

        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("DELETE FROM committee WHERE org_name = %s", (org_name,))
            cursor.execute("DELETE FROM organization_event WHERE org_name = %s", (org_name,))
            cursor.execute("DELETE FROM fee WHERE org_name = %s", (org_name,))
            cursor.execute("DELETE FROM membership WHERE org_name = %s", (org_name,))
            cursor.execute("DELETE FROM committee_assignment WHERE org_name = %s", (org_name,))
            cursor.execute("DELETE FROM organization WHERE org_name = %s", (org_name,))
            self.controller.mydb.commit()
            messagebox.showinfo("Deleted", f"Organization '{org_name}' deleted.")
            self.load_organizations()
        except mariadb.Error as err:
            messagebox.showerror("Database Error", str(err))

    def view_organization_details(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an organization to view.")
            return

        org_name = self.tree.item(selected_item[0])["values"][0]
        org_page = self.controller.frames["OrgDetailsPage"]
        org_page.load_organization(org_name)
        self.controller.show_frame("OrgDetailsPage")

