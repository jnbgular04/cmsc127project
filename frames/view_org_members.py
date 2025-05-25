import tkinter as tk
from tkinter import ttk, messagebox

class ViewMembersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Back button
        btn_back = tk.Button(self, text="Back to Home", command=lambda: controller.show_frame("HomePage"))
        btn_back.pack(pady=5)

        tk.Label(self, text="Select Organization", font=("Arial", 12)).pack()
        self.org_var = tk.StringVar()
        self.org_dropdown = ttk.Combobox(self, textvariable=self.org_var, state="readonly")
        self.org_dropdown.pack(pady=5)
        self.org_dropdown.bind("<<ComboboxSelected>>", self.on_org_selected)

        # btn_add_member = tk.Button(self, text="Add Member", command=self.open_add_member_form)
        btn_add_member = tk.Button(self, text="Add Member", command=self.open_add_member_form)
        btn_add_member.pack(pady=5)

        # Title label
        self.label_title = tk.Label(self, text="Members of Organization", font=("Arial", 16))
        self.label_title.pack(pady=5)

        # Treeview to show members
        cols = ("Student No", "First Name", "Last Name", "Academic Year", "Semester", "Status")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_organizations()

    def load_organizations(self):
        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("SELECT org_name FROM organization")
            orgs = [row[0] for row in cursor.fetchall()]
            self.org_dropdown['values'] = orgs
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load organizations.\n{e}")

    def on_org_selected(self):
        org_name = self.org_var.get()
        self.label_title.config(text=f"'{org_name}'")
        self.load_members(org_name)

    def load_members(self, org_name):
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("""
                SELECT s.student_no, s.first_name, s.last_name, m.acad_year, m.semester, m.status
                FROM membership m
                JOIN student s ON m.student_no = s.student_no
                WHERE m.org_name = %s
            """, (org_name,))
            results = cursor.fetchall()

            for row in results:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

class ViewMembersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Back button
        btn_back = tk.Button(self, text="Back to Home", command=lambda: controller.show_frame("HomePage"))
        btn_back.pack(pady=5)

        tk.Label(self, text="Select Organization", font=("Arial", 12)).pack()
        self.org_var = tk.StringVar()
        self.org_dropdown = ttk.Combobox(self, textvariable=self.org_var, state="readonly")
        self.org_dropdown.pack(pady=5)
        self.org_dropdown.bind("<<ComboboxSelected>>", self.on_org_selected)

        # btn_add_member = tk.Button(self, text="Add Member", command=self.open_add_member_form)
        btn_add_member = tk.Button(self, text="Add Member", command=self.open_add_member_form)
        btn_add_member.pack(pady=5)

        # Title label
        self.label_title = tk.Label(self, text="Members of Organization", font=("Arial", 16))
        self.label_title.pack(pady=5)

        # Treeview to show members
        cols = ("Student No", "First Name", "Last Name", "Academic Year", "Semester", "Status")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_organizations()

    def load_organizations(self):
        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("SELECT org_name FROM organization")
            orgs = [row[0] for row in cursor.fetchall()]
            self.org_dropdown['values'] = orgs
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load organizations.\n{e}")

    def on_org_selected(self,event):
        org_name = self.org_var.get()
        self.label_title.config(text=f"'{org_name}'")
        self.load_members(org_name)

    def load_members(self, org_name):
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("""
                SELECT s.student_no, s.first_name, s.last_name, m.acad_year, m.semester, m.status
                FROM membership m
                JOIN student s ON m.student_no = s.student_no
                WHERE m.org_name = %s
            """, (org_name,))
            results = cursor.fetchall()

            for row in results:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def open_add_member_form(self):
        org_name = self.org_var.get()
        if not org_name:
            messagebox.showwarning("Select Organization", "Please select an organization first.")
            return

        # Get the AddMemberPage instance from controller
        add_member_page = self.controller.frames["AddMemberPage"]

        # Set the selected organization in the AddMemberPage
        add_member_page.selected_org.set(org_name)

        # Load student list
        add_member_page.load_students()

        # Show AddMemberPage
        self.controller.show_frame("AddMemberPage")

class AddMemberPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.selected_org = tk.StringVar()

        tk.Label(self, text="Add Student to: ", font=("Arial", 16)).pack(pady=10)

        # Show selected org
        self.label_org = tk.Label(self, textvariable=self.selected_org, font=("Arial", 12))
        self.label_org.pack()

        tk.Label(self, text="Select Student :", font=("Arial", 12)).pack(pady=10)

        # Dropdown for students
        self.student_var = tk.StringVar()
        self.student_dropdown = ttk.Combobox(self, textvariable=self.student_var, state="readonly", width=30)
        self.student_dropdown.pack(pady=5)

        # Dropdown for Students
        tk.Label(self, text="Semester : ", font=("Arial", 12)).pack(pady=10)
        self.semester_var = tk.StringVar()
        self.semester_dropdown = ttk.Combobox(
            self,  # parent widget
            textvariable=self.semester_var,
            values=["1st", "2nd"],  
            state="readonly"
        )

        self.semester_var.set("1st")  #default value
        self.semester_dropdown.pack(pady=5)

        self.entry_acad_year = tk.StringVar()
        tk.Label(self, text="Acad Year ", font=("Arial", 12)).pack(pady=10)
        self.entry_acad_year = tk.Entry(self, textvariable=self.entry_acad_year)
        self.entry_acad_year.pack(pady=5)

        #Dropdown for Status
        tk.Label(self, text="Status : ", font=("Arial", 12)).pack(pady=10)
        self.status_var = tk.StringVar()
        self.status_dropdown = ttk.Combobox(
            self,  # parent widget
            textvariable=self.status_var,
            values=['Active', 'Inactive', 'Expelled', 'Suspended', 'Alumni'],  
            state="readonly"
        )

        self.status_var.set("Active")  #default value
        self.status_dropdown.pack(pady=5)

        # Add button
        btn_add = tk.Button(self, text="Add Member", command=self.add_member_to_org)
        btn_add.pack(pady=5)

        # Back
        btn_back = tk.Button(self, text="Back", command=lambda: controller.show_frame("ViewMembersPage"))
        btn_back.pack(pady=5)

    def load_students(self):
        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("""
                SELECT student_no, first_name, last_name FROM student
                WHERE date_graduated IS NULL
            """)
            students = cursor.fetchall()
            self.student_dropdown['values'] = [f"{s[0]} - {s[1]} {s[2]}" for s in students]
            self.student_mapping = {f"{s[0]} - {s[1]} {s[2]}": s[0] for s in students}
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_member_to_org(self):
        student_label = self.student_var.get()
        student_no = self.student_mapping.get(student_label)
        org_name = self.selected_org.get()
        semester = self.semester_var.get()

        if not student_no:
            messagebox.showwarning("Selection Error", "Please select a student.")
            return
        acad_year = "2024-2025"
        status = "Active"

        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("""
                INSERT INTO membership (student_no, org_name, year_joined, semester, acad_year, status)
                VALUES (%s, %s, YEAR(CURDATE()), %s, %s, %s)
            """, (student_no, org_name, semester, acad_year, status))
            self.controller.mydb.commit()

            # TO ADD : UPDATE STUDENT is_member TO TRUE IF NOT LISTED AS IS A MEMBER

            messagebox.showinfo("Success", f"{student_label} added to {org_name}")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
