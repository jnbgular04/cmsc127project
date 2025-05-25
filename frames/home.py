import tkinter as tk
from tkinter import ttk
import mysql.connector as mariadb
from tkinter import messagebox

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = tk.Label(self, text="Welcome to Organization Management System!")
        label.pack(pady=20)
        
        # Use string in main as reference
        btn_all_orgs = tk.Button(self, text="See All Registered Organizations", 
                           command=lambda: controller.show_frame("OrgsPage"))
        btn_all_orgs.pack()

        org_frame = tk.Frame(self)
        org_frame.pack(pady=5)
        tk.Label(org_frame, text="Add New Organization:").pack(side=tk.LEFT, padx=(0,5))
        self.new_org_var = tk.StringVar()
        self.entry_new_org = tk.Entry(org_frame, textvariable=self.new_org_var)
        self.entry_new_org.pack(side=tk.LEFT)
        btn_confirm_add = tk.Button(org_frame, text="Add", 
                                    command=lambda: self.add_organization())
        btn_confirm_add.pack(side=tk.LEFT, padx=(5, 0))

        # For the delete organization dropdown
        delete_frame = tk.Frame(self)
        delete_frame.pack(pady=5)
        tk.Label(delete_frame, text="Delete Organization:").pack(side=tk.LEFT, padx=(0, 5))
        self.delete_org_dropdown = ttk.Combobox(delete_frame, width=30)
        self.delete_org_dropdown.pack(side=tk.LEFT)

        btn_confirm_delete = tk.Button(delete_frame, text="Delete", 
                                    command=lambda: self.delete_organization())
        btn_confirm_delete.pack(side=tk.LEFT, padx=(5, 0))

        # For the view organization dropdown
        view_frame = tk.Frame(self)
        view_frame.pack(pady=5)
        tk.Label(view_frame, text="View Details of Organization:").pack(side=tk.LEFT, padx=(0, 5))
        self.view_org_dropdown = ttk.Combobox(view_frame, width=30)
        self.view_org_dropdown.pack(side=tk.LEFT)

        btn_confirm_view = tk.Button(view_frame, text="View",
                                     command=lambda: self.view_organization_details())
        btn_confirm_view.pack(side=tk.LEFT, padx=(5, 0))


        btn_students = tk.Button(self, text="Students Page",
                               command=lambda: controller.show_frame("StudentsPage"))
        btn_students.pack()

        btn_refresh = tk.Button(self, text="Refresh Page", command=self.load_organizations)
        btn_refresh.pack(pady=5)

        self.load_organizations()

    def load_organizations(self):
        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("SELECT org_name FROM organization")
            results = cursor.fetchall()
            org_names = [row[0] for row in results]
            self.delete_org_dropdown["values"] = org_names
            self.view_org_dropdown["values"] = org_names
        except mariadb.Error as err:
            messagebox.showerror("Database Error", str(err))
    
    def view_organization_details(self):
        selected_org = self.view_org_dropdown.get()
        if not selected_org:
            messagebox.showwarning("No Selection", "Please select an organization.")
            return

        # Pass the org name to the destination page
        org_page = self.controller.frames["OrgManagePage"]
        org_page.load_organization(selected_org)

        # Navigate to the page
        self.controller.show_frame("OrgManagePage")

    def add_organization(self):
        org_name = self.new_org_var.get().strip()

        if not org_name:
            messagebox.showwarning("Input Error", "Organization name cannot be empty.")
            return
        
        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("INSERT INTO organization (org_name) VALUES (%s)", (org_name,))
            self.controller.mydb.commit()
            messagebox.showinfo("Success", f"Organization '{org_name}' added successfully.")
            self.new_org_var.set("")  # clear input
            self.load_organizations()  # refresh list
        except mariadb.Error as err:
            messagebox.showerror("Database Error", str(err))


    def delete_organization(self):
        selected_org = self.delete_org_dropdown.get()
        print("Selected organization:", selected_org)
        if not selected_org:
            messagebox.showwarning("Selection Error", "Please select an organization to delete.")
            return
        
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{selected_org}'?")
        if not confirm:
            return
    
        try:
            cursor = self.controller.mydb.cursor()
            #delete everything under the org
            cursor.execute("DELETE FROM committee WHERE org_name = %s", (selected_org,))
            cursor.execute("DELETE FROM organization_event WHERE org_name = %s", (selected_org,))
            cursor.execute("DELETE FROM fee WHERE org_name = %s", (selected_org,))
            cursor.execute("DELETE FROM membership WHERE org_name = %s", (selected_org,))
            cursor.execute("DELETE FROM committee_assignment WHERE org_name = %s", (selected_org,))
            cursor.execute("DELETE FROM organization WHERE org_name = %s", (selected_org,))
            self.controller.mydb.commit()
            messagebox.showinfo("Deleted", f"Organization '{selected_org}' deleted successfully.")
            self.load_organizations()
        except mariadb.Error as err:
            messagebox.showerror("Database Error", str(err))
        
