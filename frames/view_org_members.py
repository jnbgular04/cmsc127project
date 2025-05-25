import tkinter as tk
from tkinter import ttk, messagebox
import uuid
from tkcalendar import DateEntry 

class ViewMembersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        btn_back = tk.Button(self, text="Back to Home", command=lambda: controller.show_frame("HomePage"))
        btn_back.pack(pady=5)

        tk.Label(self, text="Select Organization", font=("Arial", 12)).pack()
        self.org_var = tk.StringVar()
        self.org_dropdown = ttk.Combobox(self, textvariable=self.org_var, state="readonly")
        self.org_dropdown.pack(pady=5)
        self.org_dropdown.bind("<<ComboboxSelected>>", self.on_org_selected)

        btn_add_member = tk.Button(self, text="Add Member", command=self.open_add_member_form)
        btn_add_member.pack(pady=5)

        btn_add_fee = tk.Button(self, text="Manage Fees for Selected Member", command=self.open_member_fee)
        btn_add_fee.pack(pady=5)

        btn_add_comm = tk.Button(self, text="Assign Committee to Selected Member")
        btn_add_comm.pack(pady=5)

        btn_add_comm = tk.Button(self, text="Update Selected Member")
        btn_add_comm.pack(pady=5)

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

    def open_member_fee(self):
        org_name = self.org_var.get() 
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select Member", "Please select a member from the list.")
            return

        member_data = self.tree.item(selected)['values']
        manage_fee_page = self.controller.frames["ManageFeePage"]
        manage_fee_page.set_selected_org(org_name)
        manage_fee_page.set_selected_member_data(member_data) #sends data to selected_member_page

        self.controller.show_frame("ManageFeePage")

class ManageFeePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_org = tk.StringVar()
        self.label_text = tk.StringVar()
        self.selected_member = None

        # Top section using pack()
        tk.Button(self, text="Back", command=lambda: controller.show_frame("ViewMembersPage")).pack(pady=5)
        tk.Label(self, text="Manage Fee for Member", font=("Arial", 14)).pack(pady=5)
        self.label_org = tk.Label(self, textvariable=self.label_text, font=("Arial", 12))
        self.label_org.pack()
        self.member_label = tk.Label(self, text="", font=("Arial", 12))
        self.member_label.pack(pady=5)

        # Create a frame for the form elements that need grid layout
        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        # Amount field
        tk.Label(form_frame, text="Amount:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.amount_entry = tk.Entry(form_frame)
        self.amount_entry.grid(row=0, column=1, pady=5)

        # Fee type dropdown
        tk.Label(form_frame, text="Semester:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.fee_type = tk.StringVar()
        self.fee_type_dropdown = ttk.Combobox(
            form_frame,
            textvariable=self.fee_type,
            values=['Membership', 'Event', 'Miscellaneous'],
            state="readonly"
        )
        self.fee_type_dropdown.grid(row=1, column=1, pady=5)
        self.fee_type.set("Membership")

        self.acad_year_issued = tk.StringVar()
        tk.Label(form_frame, text="Acad Year Issued:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.acad_year_issued =tk.Entry(form_frame)
        self.acad_year_issued.grid(row=0, column=1, pady=5)

        # Due Date (required)
        tk.Label(form_frame, text="Due Date (required):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.due_date_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
        self.due_date_entry.grid(row=2, column=1, pady=5)

        # Date Paid (optional)
        tk.Label(form_frame, text="Date Paid (optional):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.date_paid_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
        self.date_paid_entry.grid(row=3, column=1, pady=5)
        self.date_paid_entry.delete(0, tk.END)

       
        tk.Button(self, text="Submit Fee", command=self.submit_fee).pack(pady=10)

    def set_selected_member_data(self, member_data):
        self.selected_member = member_data
        if member_data:
            self.member_label.config(text=f"{member_data[0]} - {member_data[1]} {member_data[2]}")
        else:
            self.member_label.config(text="No member selected.")

    def set_selected_org(self, org_name):
        self.selected_org.set(org_name)
        self.label_text.set(f"Fee for {org_name}")
        print("DEBUG: org_name received in set_selected_org:", org_name)
    
    def submit_fee(self): ## not yet finished!!
        student_no = self.selected_member[0]
        print(student_no)
        due_date = self.due_date_entry.get_date()
        paid_date = self.date_paid_entry.get_date() if self.date_paid_entry.get() else None
        
        print(f"Due Date: {due_date}")
        print(f"Date Paid: {paid_date}")

        student_no = self.selected_member[0]
        amount = self.amount_entry.get()
        acad_year=self.acad_year_issued.get()
        org_name = self.selected_org.get()
        ref_no = f"REF-{uuid.uuid4().hex[:10].upper()}"
        print(org_name)
        print(ref_no)  
        print(acad_year)  

        ##TODO : Implement checker for acad year

        if not amount:
            messagebox.showerror("Missing Info", "Please enter an amount.")
            return

        try:
            amount_float = float(amount)
        except ValueError:
            messagebox.showerror("Invalid Amount", "Please enter a valid number.")
            return

        try:
            cursor = self.controller.mydb.cursor()
            
            cursor.execute("""
                INSERT INTO fee (org_name, reference_no, balance, semester_issued, acad_year_issued, type, due_date, student_no)
                VALUES (%s, %s)
            """, (org_name, amount_float)) ##FIX HERE (ALREADY HAVE ALL VALUES FROM ABOVE, JUST ARRANGE SORRY SUMASAKIT NA ULO)
            self.controller.mydb.commit()
            messagebox.showinfo("Success", f"Fee of {amount_float} added to {student_no}.")
            self.amount_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))



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

            cursor.execute("""
                UPDATE student SET is_member = TRUE WHERE student_no = %s
            """, (student_no))
            self.controller.mydb.commit()

            messagebox.showinfo("Success", f"{student_label} added to {org_name}")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
