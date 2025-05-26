import tkinter as tk
from tkinter import ttk
import mysql.connector as mariadb
from tkinter import messagebox

class OrgManagePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.label = tk.Label(self, text="",font=("Arial", 14))
        self.label.pack(pady=10)

        # --- MAIN CONTAINER: holds everything horizontally ---
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        btn_view_members = tk.Button(main_frame, text="View Members", 
                             command=self.load_members)
        btn_view_members.pack()
        
        # BACK TO HOME BUTTON - MODIFIED
        self.btn_back = tk.Button(main_frame, text="Back to Home", command=self.go_back)
        self.btn_back.pack()

        btn_add_comm = tk.Button(main_frame, text="Add Committee",
                                 command=self.go_to_add_committee)
        btn_add_comm.pack(pady=5)

        # Optional: Keep the button if you want manual refresh capability
        btn_view_committees = tk.Button(main_frame, text="Refresh Committees", command=self.view_committees)
        btn_view_committees.pack(pady=5)


        self.committee_listbox = tk.Listbox(main_frame, height=15, width=40)
        self.committee_listbox.pack(pady=5)

    def go_back(self):
        if hasattr(self.controller, 'from_org_admin') and self.controller.from_org_admin:
            self.controller.show_frame("OrgAdminHomePage")
            # Reset the flag after use to prevent incorrect routing from other pages
            self.controller.from_org_admin = False 
        else:
            self.controller.show_frame("OrgsPage")

    def load_organization(self, org_name):
        self.org_name = org_name   
        self.label.config(text=f"Showing details for: { self.org_name}")
        self.view_committees()

    def load_members(self):
        # Get the ViewMembersPage frame instance
        members_page = self.controller.frames["ViewMembersPage"]
        # Call a method on ViewMembersPage to load members for current org
        members_page.load_members(self.org_name)
        
        # Switch to the ViewMembersPage frame
        self.controller.show_frame("ViewMembersPage")

    def go_to_add_committee(self):
        org_name = self.org_name   # however you track the current org
        add_comm_page = self.controller.frames["AddCommittee"]
        add_comm_page.load_organization(org_name)
        self.controller.show_frame("AddCommittee")

    def view_committees(self):
        org_name = self.org_name
        print(org_name)

        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("""
                SELECT comm_name
                FROM committee
                WHERE org_name = %s
            """, (org_name,))
            results = cursor.fetchall()

            self.committee_listbox.delete(0, tk.END)
            if results:
                for row in results:
                    self.committee_listbox.insert(tk.END, row[0])
            else:
                self.committee_listbox.insert(tk.END, "No committees found for this organization.")
        except mariadb.Error as err:
            messagebox.showerror("Database Error", str(err))

class AddCommittee(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.add_comm_label = tk.Label(self, text="",font=("Arial", 14))
        self.add_comm_label.pack(pady=10)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        # Entry for committee name
        tk.Label(form_frame, text="Committee Name:").grid(row=1, column=0, sticky="e")
        self.entry_comm_name = tk.Entry(form_frame, width=32)
        self.entry_comm_name.grid(row=1, column=1)

        # Add Committee button
        btn_add_comm = tk.Button(form_frame, text="Add Committee", command=self.add_committee)
        btn_add_comm.grid(row=2, column=0, columnspan=2, pady=10)

        # Back button
        btn_back = tk.Button(self, text="Back to Orgs Page", command=self.go_back_from_add_committee)
        btn_back.pack(pady=5)

    def go_back_from_add_committee(self):
        org_manage_page = self.controller.frames["OrgManagePage"]
        # Ensure the OrgManagePage is loaded with the correct organization again
        # This is important if OrgManagePage relies on self.org_name when it is raised.
        org_manage_page.load_organization(self.org_name) 
        self.controller.show_frame("OrgManagePage")

    def load_organization(self, org_name):
        self.org_name = org_name   
        print("Loaded org:", self.org_name) 
        self.add_comm_label.config(text=f"Add Committee to: { self.org_name}")
        # You can also load from the DB here

    def add_committee(self):
        org_name = self.org_name
        comm_name = self.entry_comm_name.get().strip()

        if not org_name or not comm_name:
            messagebox.showwarning("Input Error", "Both fields are required.")
            return

        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("""
                INSERT INTO committee (org_name, comm_name)
                VALUES (%s, %s)
            """, (org_name, comm_name))
            self.controller.mydb.commit()
            messagebox.showinfo("Success", f"Committee '{comm_name}' added to '{org_name}'")
            self.entry_comm_name.delete(0, tk.END)
        except mariadb.Error as err:
            messagebox.showerror("Database Error", str(err))