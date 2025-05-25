import mysql.connector as mariadb
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
   
class StudentsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # BACK TO HOME BUTTON
        btn_back = tk.Button(self, text="Back to Home", command=lambda: controller.show_frame("HomePage"))
        btn_back.pack()

        label = tk.Label(self, text="All Currently Enrolled Students", font=("Arial", 16))
        label.pack(pady=10)

        # Entry + Button to add new org
        entry_frame = tk.Frame(self)
        entry_frame.pack(pady=5)

        btn_add_student = tk.Button(self, text="Add New Student", command=lambda: controller.show_frame("AddStudentPage"))
        btn_add_student.pack(pady=5)

        btn_delete = tk.Button(self, text="Delete Selected Student", command=self.delete_student)
        btn_delete.pack()

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

        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        for col in columns:
            heading_text = col.replace("_", " ").title()
            self.tree.heading(col, text=heading_text)
            self.tree.column(col, width=200, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Refresh Button
        btn_refresh = tk.Button(self, text="Refresh", command=self.load_students)
        btn_refresh.pack(pady=5)

        self.load_students()

    def load_students(self):
        # Clear the existing data in Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("""
                SELECT student_no, first_name, middle_name, last_name, sex, degree_program, date_graduated, is_member
                FROM student
                WHERE date_graduated IS NULL
            """)
            results = cursor.fetchall()

            for row in results:
                # Convert boolean 'is_member' to string for display if needed
                row_display = list(row)
                # Optional: format is_member boolean to Yes/No string
                row_display[-1] = "Yes" if row[-1] else "No"
                self.tree.insert("", "end", values=row_display)

        except mariadb.Error as err:
            print(f"HERE ERROR Error: {err}")
    
    def delete_student(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an organization to delete.")
            return
        
        selected_student = self.tree.item(selected_item)["values"][0]
        print(selected_student)

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete student with student number '{selected_student}'?")
        if not confirm:
            return

        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("DELETE FROM student WHERE student_no = %s", (selected_student,))
            self.controller.mydb.commit()
            messagebox.showinfo("Deleted", f"Student with Student no. '{selected_student}' deleted successfully.")
            self.load_students()
        except mariadb.Error as err:
            messagebox.showerror("Database Error", str(err))

class AddStudentPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Add New Student", font=("Arial", 16)).pack(pady=10)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        # Student fields
        labels = [
            "Student No", "First Name", "Middle Name", "Last Name", 
            "Sex (Male/Female)", "Degree Program", "Date Graduated (YYYY-MM-DD or empty)", "Is Member (Yes/No)"
        ]
        self.entries = {}

        for i, label_text in enumerate(labels):
            tk.Label(form_frame, text=label_text).grid(row=i, column=0, sticky="e", pady=2)
            entry = tk.Entry(form_frame)
            entry.grid(row=i, column=1, pady=2)
            self.entries[label_text] = entry

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Student", command=self.add_student).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Back to Students", command=lambda: controller.show_frame("StudentsPage")).pack(side=tk.LEFT)

    def add_student(self):
        # Collect data from entries
        data = {}
        for key, entry in self.entries.items():
            data[key] = entry.get().strip()

        # Validation examples
        if not data["Student No"]:
            tk.messagebox.showwarning("Input Error", "Student No is required.")
            return
        if not data["First Name"]:
            tk.messagebox.showwarning("Input Error", "First Name is required.")
            return
        if not data["Last Name"]:
            tk.messagebox.showwarning("Input Error", "Last Name is required.")
            return
        if data["Sex (Male/Female)"] not in ("Male", "Female"):
            tk.messagebox.showwarning("Input Error", "Sex must be 'Male' or 'Female'.")
            return
        if not data["Degree Program"]:
            tk.messagebox.showwarning("Input Error", "Degree Program is required.")
            return

        # Process optional fields
        date_graduated = data["Date Graduated (YYYY-MM-DD or empty)"] or None
        is_member_str = data["Is Member (Yes/No)"].lower()
        if is_member_str == "yes":
            is_member = True
        elif is_member_str == "no":
            is_member = False
        else:
            tk.messagebox.showwarning("Input Error", "Is Member must be 'Yes' or 'No'.")
            return

        # Insert into DB
        try:
            cursor = self.controller.mydb.cursor()
            insert_sql = """
                INSERT INTO student (student_no, first_name, middle_name, last_name, sex, degree_program, date_graduated, is_member)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (
                data["Student No"],
                data["First Name"],
                data["Middle Name"] or None,
                data["Last Name"],
                data["Sex (Male/Female)"],
                data["Degree Program"],
                date_graduated,
                is_member
            ))
            self.controller.mydb.commit()

            tk.messagebox.showinfo("Success", f"Student '{data['Student No']}' added successfully.")
            # Clear inputs
            for entry in self.entries.values():
                entry.delete(0, tk.END)
        except mariadb.Error as err:
            tk.messagebox.showerror("Database Error", str(err))