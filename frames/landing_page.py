import tkinter as tk
from tkinter import messagebox

class LandingPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="Welcome to the Organization Management System!", font=("Arial", 16))
        label.pack(pady=20)

        tk.Label(self, text="Select how you'd like to use the system:").pack(pady=10)

        btn_system_admin = tk.Button(self, text="Global Admin",
                                     command=lambda: controller.show_frame("AdminHomePage"))
        btn_system_admin.pack(pady=5)

        btn_org_admin = tk.Button(self, text="Organization Admin",
                                  command=lambda: controller.show_frame("OrgAdminLogin"))
        btn_org_admin.pack(pady=5)

        btn_student = tk.Button(self, text="Student",
                                command=lambda: controller.show_frame("StudentLogin"))
        btn_student.pack(pady=5)
