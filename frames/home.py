import tkinter as tk
class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = tk.Label(self, text="Home Page")
        label.pack(pady=20)
        
        # Use string reference instead of direct import
        btn_orgs = tk.Button(self, text="Orgs Page", 
                           command=lambda: controller.show_frame("OrgsPage"))
        btn_orgs.pack()
        
        btn_students = tk.Button(self, text="Students Page",
                               command=lambda: controller.show_frame("StudentsPage"))
        btn_students.pack()

        btn_students = tk.Button(self, text="View Members",
                               command=lambda: controller.show_frame("ViewMembersPage"))
        btn_students.pack()