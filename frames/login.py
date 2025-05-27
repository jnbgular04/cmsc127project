import tkinter as tk
from tkinter import messagebox
import mysql.connector as mariadb

class OrgAdminLogin(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Enter Organization Name to Continue:").pack(pady=10)
        self.org_name_var = tk.StringVar()
        tk.Entry(self, textvariable=self.org_name_var).pack(pady=5)

        tk.Button(self, text="Proceed", command=self.verify_org).pack(pady=5)
        tk.Button(self, text="Back", command=lambda: controller.show_frame("LandingPage")).pack(pady=10)

    def verify_org(self):
        org_name = self.org_name_var.get().strip()
        if not org_name:
            messagebox.showwarning("Input Error", "Please enter an organization name.")
            return

        cursor = self.controller.mydb.cursor()
        cursor.execute("SELECT org_name FROM organization WHERE org_name = %s", (org_name,))
        result = cursor.fetchone()
        if result:
            self.controller.selected_org = org_name
            self.controller.show_frame("OrgAdminHomePage")
        else:
            messagebox.showerror("Not Found", "Organization not found.")



class StudentLogin(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Enter Your Student Number to Continue:").pack(pady=10)
        self.student_no_var = tk.StringVar()
        tk.Entry(self, textvariable=self.student_no_var).pack(pady=5)

        tk.Button(self, text="Proceed", command=self.verify_student).pack(pady=5)
        tk.Button(self, text="Back", command=lambda: controller.show_frame("LandingPage")).pack(pady=10)

    def verify_student(self):
        student_no = self.student_no_var.get().strip()
        if not student_no:
            messagebox.showwarning("Input Error", "Please enter your student number.")
            return

        cursor = self.controller.mydb.cursor()
        cursor.execute("SELECT student_no FROM student WHERE student_no = %s", (student_no,))
        result = cursor.fetchone()
        if result:
            self.controller.selected_student = student_no
            home_page = self.controller.frames["StudentHomePage"]
            home_page.load_student(student_no)
            self.controller.show_frame("StudentHomePage")
        else:
            messagebox.showerror("Not Found", "Student not found.")
