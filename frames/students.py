import mysql.connector as mariadb
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
   
class StudentsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.show_with_orgs_var = tk.BooleanVar(value=False)



        # Back Button
        tk.Button(self, text="Back to Home", command=lambda: controller.show_frame("AdminHomePage")).pack(pady=5)

        tk.Label(self, text="Student Records", font=("Arial", 16)).pack(pady=10)

        # Treeview
        columns = (
            "student_no",
            "first_name",
            "middle_name",
            "last_name",
            "sex",
            "degree_program",
            "date_graduated",
            "is_member"
        )

        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=150, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Buttons
        
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        
        chk_with_orgs = tk.Checkbutton(
            btn_frame, text="Only show students with orgs", variable=self.show_with_orgs_var,
            command=self.load_students
        )
        chk_with_orgs.pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="View Details", command=self.view_student_details).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Refresh", command=self.load_students).pack(side=tk.LEFT, padx=5)

        # Optional: Add/Delete/Update buttons for debugging/admin control
        # You may comment these out if Global Admin is not allowed to do this
        tk.Button(btn_frame, text="Add New Student", command=self.add_student_popup).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Selected Student", command=self.delete_student).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Update Selected Student", command=self.update_student_popup).pack(side=tk.LEFT, padx=5)

        self.load_students()

    def load_students(self):
        self.tree.delete(*self.tree.get_children())

        try:
            cursor = self.controller.mydb.cursor()

            if self.show_with_orgs_var.get():
                cursor.execute("""
                    SELECT student_no, first_name, middle_name, last_name, sex,
                        degree_program, date_graduated, is_member
                    FROM student
                    WHERE is_member = TRUE
                """)
            else:
                cursor.execute("""
                    SELECT student_no, first_name, middle_name, last_name, sex,
                        degree_program, date_graduated, is_member
                    FROM student
                """)

            for row in cursor.fetchall():
                row = list(row)
                row[-1] = "Yes" if row[-1] else "No"
                self.tree.insert("", "end", values=row)

        except mariadb.Error as err:
            messagebox.showerror("Database Error", str(err))



    def view_student_details(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Student", "Please select a student to view.")
            return

        data = self.tree.item(selected[0])['values']
        student_no = data[0]

        popup = tk.Toplevel(self)
        popup.title(f"Student Details: {student_no}")
        popup.geometry("800x600")
        popup.grab_set()

        # ----- BASIC INFO -----
        info_frame = tk.LabelFrame(popup, text="Basic Info", padx=10, pady=10)
        info_frame.pack(fill="x", padx=10, pady=10)

        labels = [
            "Student No", "First Name", "Middle Name", "Last Name",
            "Sex", "Degree Program", "Date Graduated", "Is Member"
        ]
        for i, label in enumerate(labels):
            tk.Label(info_frame, text=label + ":", anchor="w", width=20).grid(row=i, column=0, sticky="w")
            tk.Label(info_frame, text=data[i]).grid(row=i, column=1, sticky="w")

        # ----- MEMBERSHIPS -----
        self.create_tree_section(popup, "Organization Memberships",
            columns=["Org", "Status", "Year Joined", "Semester", "AY"],
            query="""
                SELECT org_name, status, year_joined, semester, acad_year
                FROM membership
                WHERE student_no = %s
                ORDER BY acad_year DESC, semester DESC
            """,
            param=(student_no,)
        )

        # ----- COMMITTEES -----
        self.create_tree_section(popup, "Committee Roles",
            columns=["Org", "Committee", "Role", "Semester", "AY"],
            query="""
                SELECT org_name, comm_name, role, semester, acad_year
                FROM committee_assignment
                WHERE student_no = %s
                ORDER BY acad_year DESC, semester DESC
            """,
            param=(student_no,)
        )

        # ----- FEES -----
        self.create_tree_section(popup, "Fee Records",
            columns=["Org", "Ref No", "Type", "Balance", "Due Date", "Date Paid"],
            query="""
                SELECT org_name, reference_no, type, balance, due_date, date_paid
                FROM fee
                WHERE student_no = %s
                ORDER BY acad_year_issued DESC, semester_issued DESC
            """,
            param=(student_no,)
        )

        # Close button
        tk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

    def add_student_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Add New Student")
        popup.geometry("400x500")
        popup.grab_set()

        fields = [
            "Student No", "First Name", "Middle Name", "Last Name",
            "Sex (Male/Female)", "Degree Program",
            "Date Graduated (YYYY-MM-DD or empty)", "Is Member (Yes/No)"
        ]

        entry_vars = {}
        for i, field in enumerate(fields):
            tk.Label(popup, text=field + ":").grid(row=i, column=0, sticky="e", padx=5, pady=5)
            var = tk.StringVar()
            entry = tk.Entry(popup, textvariable=var)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry_vars[field] = var

        def save_student():
            data = {k: v.get().strip() for k, v in entry_vars.items()}

            if not data["Student No"] or not data["First Name"] or not data["Last Name"]:
                messagebox.showerror("Input Error", "Student No, First Name, and Last Name are required.")
                return

            if data["Sex (Male/Female)"] not in ("Male", "Female"):
                messagebox.showerror("Input Error", "Sex must be 'Male' or 'Female'.")
                return

            is_member_str = data["Is Member (Yes/No)"].lower()
            if is_member_str == "yes":
                is_member = True
            elif is_member_str == "no":
                is_member = False
            else:
                messagebox.showerror("Input Error", "Is Member must be 'Yes' or 'No'.")
                return

            try:
                cursor = self.controller.mydb.cursor()
                cursor.execute("""
                    INSERT INTO student (
                        student_no, first_name, middle_name, last_name,
                        sex, degree_program, date_graduated, is_member
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    data["Student No"],
                    data["First Name"],
                    data["Middle Name"] or None,
                    data["Last Name"],
                    data["Sex (Male/Female)"],
                    data["Degree Program"],
                    data["Date Graduated (YYYY-MM-DD or empty)"] or None,
                    is_member
                ))
                self.controller.mydb.commit()
                messagebox.showinfo("Success", f"Student '{data['Student No']}' added.")
                popup.destroy()
                self.load_students()
            except mariadb.Error as err:
                messagebox.showerror("Database Error", str(err))

        tk.Button(popup, text="Save", command=save_student).grid(row=len(fields), column=0, columnspan=2, pady=15)
 

    def delete_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Select a student to delete.")
            return

        student_no = self.tree.item(selected[0])["values"][0]
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete student '{student_no}'?")
        if not confirm:
            return

        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("DELETE FROM student WHERE student_no = %s", (student_no,))
            self.controller.mydb.commit()
            self.load_students()
            messagebox.showinfo("Deleted", f"Student {student_no} deleted.")
        except mariadb.Error as err:
            messagebox.showerror("Database Error", str(err))

    def update_student_popup(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Student", "Please select a student to update.")
            return

        original_data = self.tree.item(selected[0])['values']
        student_no = original_data[0]

        popup = tk.Toplevel(self)
        popup.title(f"Update Student: {student_no}")
        popup.geometry("400x500")
        popup.grab_set()

        fields = [
            "First Name", "Middle Name", "Last Name", "Sex (Male/Female)",
            "Degree Program", "Date Graduated (YYYY-MM-DD or empty)", "Is Member (Yes/No)"
        ]

        entry_vars = {}
        for i, field in enumerate(fields):
            tk.Label(popup, text=field + ":").grid(row=i, column=0, sticky="e", padx=5, pady=5)
            var = tk.StringVar()
            entry = tk.Entry(popup, textvariable=var)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry_vars[field] = var

        # Safely populate only non-None values
        fields_map = {
            "First Name": original_data[1],
            "Middle Name": original_data[2],
            "Last Name": original_data[3],
            "Sex (Male/Female)": original_data[4],
            "Degree Program": original_data[5],
            "Date Graduated (YYYY-MM-DD or empty)": original_data[6],
            "Is Member (Yes/No)": original_data[7],
        }

        for key, value in fields_map.items():
            if value != "None":
                entry_vars[key].set(value)

        def save_update():
            data = {k: v.get().strip() for k, v in entry_vars.items()}

            if data["Sex (Male/Female)"] not in ("Male", "Female"):
                messagebox.showerror("Invalid Input", "Sex must be 'Male' or 'Female'.")
                return

            is_member_str = data["Is Member (Yes/No)"].lower()
            if is_member_str == "yes":
                is_member = True
            elif is_member_str == "no":
                is_member = False
            else:
                messagebox.showerror("Invalid Input", "Is Member must be 'Yes' or 'No'.")
                return

            try:
                cursor = self.controller.mydb.cursor()
                cursor.execute("""
                    UPDATE student
                    SET first_name = %s, middle_name = %s, last_name = %s,
                        sex = %s, degree_program = %s, date_graduated = %s, is_member = %s
                    WHERE student_no = %s
                """, (
                    data["First Name"],
                    data["Middle Name"] or None,
                    data["Last Name"],
                    data["Sex (Male/Female)"],
                    data["Degree Program"],
                    data["Date Graduated (YYYY-MM-DD or empty)"] or None,
                    is_member,
                    student_no
                ))
                self.controller.mydb.commit()
                messagebox.showinfo("Updated", f"Student '{student_no}' updated successfully.")
                popup.destroy()
                self.load_students()
            except mariadb.Error as err:
                messagebox.showerror("Database Error", str(err))

        tk.Button(popup, text="Save", command=save_update).grid(row=len(fields), column=0, columnspan=2, pady=15)

    def create_tree_section(self, parent, title, columns, query, param):
        frame = tk.LabelFrame(parent, text=title, padx=10, pady=5)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        tree = ttk.Treeview(frame, columns=columns, show="headings", height=6)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)
        tree.pack(fill="both", expand=True)

        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute(query, param)
            rows = cursor.fetchall()
            for row in rows:
                tree.insert("", "end", values=row)
        except mariadb.Error as err:
            messagebox.showerror("Database Error", str(err))

