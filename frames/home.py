import tkinter as tk
from tkinter import ttk
import mysql.connector as mariadb
from tkinter import messagebox

class AdminHomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = tk.Label(self, text="Welcome to Organization Management System!")
        label.pack(pady=20)
        
        # Use string in main as reference
        btn_all_orgs = tk.Button(self, text="View All Registered Organizations", 
                           command=lambda: controller.show_frame("OrgsPage"))
        btn_all_orgs.pack()

        btn_students = tk.Button(self, text="View Student Records",
                               command=lambda: controller.show_frame("StudentsPage"))
        btn_students.pack()

        btn_students = tk.Button(self, text="View Organization Finances",
                               command=lambda: controller.show_frame("OrgFinancesPage"))
        btn_students.pack()

        tk.Button(self, text="Go Back to Landing Page",
                  command=lambda: controller.show_frame("LandingPage")).pack(pady=20)
    
        
class OrgAdminHomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.label = tk.Label(self, text="Organization Admin Home Page", font=("Arial", 16))
        self.label.pack(pady=20)

        self.info_label = tk.Label(self, text="")
        self.info_label.pack(pady=10)

        btn_view_members = tk.Button(self, text="View Members", 
                            command=self.load_members)
        btn_view_members.pack()

        tk.Button(self, text="Manage Organization Committees",
                  command=self.view_my_org).pack(pady=5)
        
        # Organization Fees
        tk.Button(self, text="Manage Organization Fees",
                  ).pack(pady=5)

        # 
        tk.Button(self, text="View Organization Events",
                  ).pack(pady=5)
        
        tk.Button(self, text="Generate Organization Reports",
                  command=self.generate_reports).pack(pady=5)

        tk.Button(self, text="Go Back to Landing Page",
                  command=lambda: controller.show_frame("LandingPage")).pack(pady=20)

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        org_name = getattr(self.controller, 'selected_org', 'N/A')
        self.info_label.config(text=f"Logged in as Org Admin for: {org_name}")

    def generate_reports(self):
        org_name = getattr(self.controller, 'selected_org', None)
        org_page = self.controller.frames["IndivOrgDetailsPage"]
        org_page.load_organization(org_name)
        self.controller.show_frame("IndivOrgDetailsPage")
        print(org_name)

    def view_my_org(self):
        org_name = getattr(self.controller, 'selected_org', None)
        if not org_name:
            messagebox.showerror("Error", "No organization selected.")
            return
        org_page = self.controller.frames["OrgManagePage"]
        org_page.load_organization(org_name)
        self.controller.from_org_admin = True
        self.controller.show_frame("OrgManagePage")

    def load_organization(self, org_name):
        self.org_name = org_name   
        self.label.config(text=f"Showing details for: {self.org_name}")
    
    def load_members(self):
        org_name = getattr(self.controller, 'selected_org', None)
        if not org_name:
            messagebox.showerror("Error", "No organization selected.")
            return

        members_page = self.controller.frames["ViewMembersPage"]
        members_page.load_members(org_name)
        self.controller.show_frame("ViewMembersPage")
    
       

class StudentHomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="Student Home Page", font=("Arial", 16))
        label.pack(pady=20)

        tk.Label(self, text="This view is for students to see their organization memberships and fees.").pack(pady=10)

        tk.Button(self, text="View My Memberships",
                  command=lambda: controller.show_frame("ViewMembersPage")).pack(pady=5)

        tk.Button(self, text="View My Fees",
                  command=lambda: controller.show_frame("AddFeePage")).pack(pady=5)

        tk.Button(self, text="Go Back to Landing Page",
                  command=lambda: controller.show_frame("LandingPage")).pack(pady=20)