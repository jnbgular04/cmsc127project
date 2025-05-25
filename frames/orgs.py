import getpass
import mysql.connector as mariadb
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

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
                           command=lambda: controller.show_frame("HomePage"))
        btn_back.pack()

        label = tk.Label(left_frame, text="All Organizations", font=("Arial", 16))
        label.pack(pady=10)

        # Add Org Entry + Button
        entry_frame = tk.Frame(left_frame)
        entry_frame.pack(pady=5)
                
        self.new_org_var = tk.StringVar()
        tk.Label(entry_frame, text="New Org Name:").pack(side=tk.LEFT, padx=(0,5))
        self.entry_new_org = tk.Entry(entry_frame, textvariable=self.new_org_var)
        self.entry_new_org.pack(side=tk.LEFT)

        btn_add = tk.Button(entry_frame, text="Add Organization", command=self.add_organization)
        btn_add.pack(side=tk.LEFT, padx=5)

        btn_delete = tk.Button(left_frame, text="Delete Selected Organization", command=self.delete_org)
        btn_delete.pack()

        # btn_view_members = tk.Button(left_frame, text="View Selected Organization's Members", command=self.view_members)
        # btn_view_members.pack(pady=5)


         # Define Treeview columns
        columns = ("Organization Name",)
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings")

        for col in columns:
            heading_text = col.replace("_", " ").title()
            self.tree.heading(col, text=heading_text)
            self.tree.column(col, width=200, anchor="center")


        self.tree.pack(fill="both", expand=True, padx=10, pady=10)


       # --- RIGHT SIDE: Committee management ---
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill="y", padx=20)

        # for padding
        tk.Label(right_frame, text="", height=10).pack() 
        
        btn_add_comm = tk.Button(right_frame, text="Add Committee", command=lambda: controller.show_frame(AddCommittee))
        btn_add_comm.pack(pady=5)

        btn_view_committees = tk.Button(right_frame, text="View Committees", command=self.view_committees)
        btn_view_committees.pack(pady=5)

        self.committee_listbox = tk.Listbox(right_frame, height=15, width=40)
        self.committee_listbox.pack(pady=5)

        self.load_organizations()

    def load_organizations(self):
        # Clear the existing data in Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("SELECT org_name FROM organization")
            results = cursor.fetchall()

            for row in results:
                self.tree.insert("", "end", values=row)

        except mariadb.Error as err:
            print(f"HERE ERROR Error: {err}")

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

    def delete_org(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an organization to delete.")
            return
        
        org_name = self.tree.item(selected_item)["values"][0]
        print(org_name)

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{org_name}'?")
        if not confirm:
            return

        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("DELETE FROM organization WHERE org_name = %s", (org_name,))
            self.controller.mydb.commit()
            messagebox.showinfo("Deleted", f"Organization '{org_name}' deleted successfully.")
            self.load_organizations()
        except mariadb.Error as err:
            messagebox.showerror("Database Error", str(err))

    def view_committees(self):
        selected_item = self.tree.selection()
        org_name = self.tree.item(selected_item)["values"][0]
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

    # def view_members(self):
    #     selected_item = self.tree.selection()
    #     if not selected_item:
    #         messagebox.showwarning("Input Error", "Please select an organization.")
    #         return

    #     org_name = self.tree.item(selected_item)["values"][0]

    #     try:
    #         cursor = self.controller.mydb.cursor()
    #         cursor.execute("""
    #             SELECT s.student_no, s.first_name, s.last_name, m.acad_year, m.semester, m.status
    #             FROM membership m
    #             JOIN student s ON m.student_no = s.student_no
    #             WHERE m.org_name = %s
    #         """, (org_name,))
    #         results = cursor.fetchall()

    #         members_window = tk.Toplevel(self)
    #         members_window.title(f"Members of {org_name}")

    #         cols = ("Student No", "First Name", "Last Name", "Academic Year", "Semester", "Status")
    #         tree = ttk.Treeview(members_window, columns=cols, show="headings")
    #         for col in cols:
    #             tree.heading(col, text=col)
    #             tree.column(col, width=100)
    #         tree.pack(fill="both", expand=True)

    #         for row in results:
    #             tree.insert("", "end", values=row)

    #     except mariadb.Error as err:
    #         messagebox.showerror("Database Error", str(err))

class AddCommittee(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Add New Committee", font=("Arial", 16)).pack(pady=10)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        # Dropdown for organization names
        tk.Label(form_frame, text="Select Organization:").grid(row=0, column=0, sticky="e")
        self.org_dropdown = ttk.Combobox(form_frame, width=30)
        self.org_dropdown.grid(row=0, column=1)

        # Entry for committee name
        tk.Label(form_frame, text="Committee Name:").grid(row=1, column=0, sticky="e")
        self.entry_comm_name = tk.Entry(form_frame, width=32)
        self.entry_comm_name.grid(row=1, column=1)

        # Add Committee button
        btn_add_comm = tk.Button(form_frame, text="Add Committee", command=self.add_committee)
        btn_add_comm.grid(row=2, column=0, columnspan=2, pady=10)

        # Back button
        btn_back = tk.Button(self, text="Back to Orgs Page", command=lambda: controller.show_frame(OrgsPage))
        btn_back.pack(pady=5)

        self.load_organizations()

    def load_organizations(self):
        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("SELECT org_name FROM organization")
            results = cursor.fetchall()
            org_names = [row[0] for row in results]
            self.org_dropdown["values"] = org_names
        except mariadb.Error as err:
            messagebox.showerror("Database Error", str(err))

    def add_committee(self):
        org_name = self.org_dropdown.get()
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