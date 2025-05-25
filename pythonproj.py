import getpass
import mysql.connector as mariadb
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

#for setting up of database
def setup_database(cursor):

    cursor.execute("CREATE DATABASE IF NOT EXISTS project")
    print("Created database 'project'.")

    cursor.execute("USE project")

    create_student_table = """
    CREATE TABLE student (
        student_no CHAR(10) PRIMARY KEY NOT NULL,
        first_name VARCHAR(30) NOT NULL,
        middle_name VARCHAR(30),
        last_name VARCHAR(30) NOT NULL,
        sex ENUM('Male','Female') NOT NULL,
        degree_program VARCHAR(100) NOT NULL,
        date_graduated DATE DEFAULT NULL,
        is_member BOOLEAN DEFAULT FALSE
    )
    """

    create_org_table = """CREATE TABLE organization (
        org_name VARCHAR(200) PRIMARY KEY NOT NULL
        );
    """
    create_org_event = """CREATE TABLE organization_event (
        org_name VARCHAR(200) NOT NULL,
        event VARCHAR(100) NOT NULL,
        CONSTRAINT org_event_pk PRIMARY KEY (org_name, event),
        CONSTRAINT org_event_fk FOREIGN KEY(org_name) REFERENCES organization(org_name)
        );
    """

    create_fee_table = """CREATE TABLE fee (
        org_name VARCHAR(200) NOT NULL,
        reference_no INT NOT NULL,
        balance DECIMAL(10,2) NOT NULL,
        semester_issued ENUM ('1st','2nd') NOT NULL,
        acad_year_issued VARCHAR(9) NOT NULL,
        type ENUM('Membership','Event','Miscellaneous') NOT NULL,    
        due_date DATE NOT NULL,
        date_paid DATE DEFAULT NULL,
        student_no CHAR(10) NOT NULL,
        CONSTRAINT fee_pk PRIMARY KEY (org_name, reference_no),
        CONSTRAINT fee_org_fk FOREIGN KEY(org_name) REFERENCES organization(org_name),
        CONSTRAINT fee_std_fk FOREIGN KEY(student_no) REFERENCES student(student_no)
        );
    """

    creat_table_committee= """CREATE TABLE committee (
        org_name VARCHAR(200) NOT NULL,
        comm_name VARCHAR(50) NOT NULL,
        CONSTRAINT comm_pk PRIMARY KEY (org_name, comm_name),
        CONSTRAINT comm_fk FOREIGN KEY(org_name) REFERENCES organization(org_name)
        );
    """

    create_table_membership = """ CREATE TABLE membership(
            student_no CHAR(10) NOT NULL ,
            org_name VARCHAR(200) NOT NULL,
            year_joined YEAR NOT NULL,
            semester ENUM ('1st','2nd') NOT NULL,
            acad_year VARCHAR(9) NOT NULL,
            status ENUM('Active', 'Inactive', 'Expelled', 'Suspended', 'Alumni') NOT NULL,
            CONSTRAINT membership_pk PRIMARY KEY (student_no, org_name, acad_year, semester),
            CONSTRAINT membership_std_fk FOREIGN KEY (student_no) REFERENCES student(student_no),
            CONSTRAINT membership_org_fk FOREIGN KEY (org_name) REFERENCES organization(org_name)
        );
    """
    create_comm_assignment = """
        CREATE TABLE committee_assignment (
            student_no CHAR(10) NOT NULL ,
            org_name VARCHAR(200)  NOT NULL,
            comm_name VARCHAR(50) NOT NULL  ,
            role VARCHAR(100) NOT NULL,
            semester ENUM ('1st','2nd') NOT NULL,
            acad_year VARCHAR(9) NOT NULL,
            CONSTRAINT comm_ass_pk PRIMARY KEY (student_no, org_name, acad_year, semester),
            CONSTRAINT comm_ass_std_fk FOREIGN KEY (student_no) REFERENCES student(student_no),
            CONSTRAINT comm_ass_org_fk FOREIGN KEY (org_name) REFERENCES organization(org_name),
            CONSTRAINT comm_ass_comm_fk FOREIGN KEY (org_name, comm_name) REFERENCES committee(org_name, comm_name)
        );
    """

    cursor.execute(create_student_table)
    cursor.execute(create_org_table)
    cursor.execute(create_org_event)
    cursor.execute(create_fee_table)
    cursor.execute(creat_table_committee)
    cursor.execute(create_table_membership)
    cursor.execute(create_comm_assignment)

#for checking if database exists already
def database_exists(cursor, db_name):
    cursor.execute("SHOW DATABASES")
    databases = [db[0] for db in cursor.fetchall()]
    return db_name in databases

#main application window
class MainApp(tk.Tk):
    def __init__(self,mydb):
        super().__init__()
        self.title("Multi-page App")
        self.geometry("1800x600")

        #store connection
        self.mydb = mydb

        # Container to hold all pages
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Dictionary of frames
        self.frames = {}

        for F in (HomePage, OrgsPage, StudentsPage, AddStudentPage, AddCommittee):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomePage)

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="Home Page")
        label.pack(pady=20)

        btn_orgs = tk.Button(self, text="Orgs Page", command=lambda: controller.show_frame(OrgsPage))
        btn_orgs.pack()

        btn_students = tk.Button(self, text="Students Page", command=lambda: controller.show_frame(StudentsPage))
        btn_students.pack()
        

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
        btn_back = tk.Button(left_frame, text="Back to Home", command=lambda: controller.show_frame(HomePage))
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

        btn_delete = tk.Button(left_frame, text="Delete Selected Org", command=self.delete_org)
        btn_delete.pack()

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
        tk.Label(right_frame, text="", height=9).pack() 
        

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
            mydb.commit()
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
    
class StudentsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # BACK TO HOME BUTTON
        btn_back = tk.Button(self, text="Back to Home", command=lambda: controller.show_frame(HomePage))
        btn_back.pack()

        label = tk.Label(self, text="All Currently Enrolled Students", font=("Arial", 16))
        label.pack(pady=10)

        # Entry + Button to add new org
        entry_frame = tk.Frame(self)
        entry_frame.pack(pady=5)

        btn_add_student = tk.Button(self, text="Add New Student", command=lambda: controller.show_frame(AddStudentPage))
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
        tk.Button(btn_frame, text="Back to Students", command=lambda: controller.show_frame(StudentsPage)).pack(side=tk.LEFT)

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

#MAIN PROGRAM
# password = input("Password for root user: ")
password = "JazminMaria@2004"

# Connect and setup database/tables
mydb = mariadb.connect(host="localhost", user="root", password=password)
cursor = mydb.cursor()

db_name = "project"
if database_exists(cursor, db_name):
    print(f"Database '{db_name}' already exists.")
else:
    setup_database(cursor)

##USE THE project DB
cursor.execute("USE project")

if __name__ == "__main__":
    app = MainApp(mydb)
    app.mainloop()
