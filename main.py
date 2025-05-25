import getpass
import mysql.connector as mariadb
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from database import create_connection
from frames.home import HomePage
from frames.orgs import AddCommittee, OrgsPage
from frames.students import AddStudentPage, StudentsPage
from frames.view_org_members import ManageFeePage, AddMemberPage, ViewMembersPage

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

        #Think of routing in cmsc 100
        pages = {
            "HomePage": HomePage,
            "OrgsPage": OrgsPage,
            "StudentsPage": StudentsPage,
            "AddStudentPage": AddStudentPage,
            "AddCommittee": AddCommittee,
            "ViewMembersPage": ViewMembersPage,
            "AddMemberPage" : AddMemberPage,
            "ManageFeePage" : ManageFeePage
        }

        for name, F in pages.items():
            frame = F(container, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("HomePage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


# Connect and setup database/tables
mydb = create_connection();
cursor = mydb.cursor()

db_name = "project"
if database_exists(cursor, db_name):
    print(f"Database '{db_name}' exists.")
else:
    setup_database(cursor)

cursor.execute("USE project")

if __name__ == "__main__":
    app = MainApp(mydb)
    app.mainloop()
