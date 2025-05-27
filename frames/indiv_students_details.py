import tkinter as tk
from tkinter import ttk
import mysql.connector as mariadb
from tkinter import messagebox

class IndivStudentMembership(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        canvas = tk.Canvas(self)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Button(self.scrollable_frame, text="Back",
                  command=lambda: controller.show_frame("StudentHomePage")).pack(pady=10)

        self.membership_frame = tk.LabelFrame(self.scrollable_frame, text="Organization Memberships", padx=10, pady=10)
        self.membership_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.committee_frame = tk.LabelFrame(self.scrollable_frame, text="Committee Roles", padx=10, pady=10)
        self.committee_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.fee_frame = tk.LabelFrame(self.scrollable_frame, text="Fee Records", padx=10, pady=10)
        self.fee_frame.pack(fill="both", expand=True, padx=10, pady=5)

          # Mouse wheel scrolling
        self.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def load_student(self, stdn_num):
        self.student_data = stdn_num
        student_no = stdn_num

        self.create_tree_section(
            self.membership_frame,
            columns=["Org", "Status", "Year Joined", "Semester", "AY"],
            query="""
                SELECT org_name, status, year_joined, semester, acad_year
                FROM membership
                WHERE student_no = %s
                ORDER BY acad_year DESC, semester DESC
            """,
            param=(student_no,)
        )

        self.create_tree_section(
            self.committee_frame,
            columns=["Org", "Committee", "Role", "Semester", "AY"],
            query="""
                SELECT org_name, comm_name, role, semester, acad_year
                FROM committee_assignment
                WHERE student_no = %s
                ORDER BY acad_year DESC, semester DESC
            """,
            param=(student_no,)
        )

        self.create_tree_section(
            self.fee_frame,
            columns=["Org", "Ref No", "Type", "Balance", "Due Date", "Date Paid"],
            query="""
                SELECT org_name, reference_no, type, balance, due_date, date_paid
                FROM fee
                WHERE student_no = %s
                ORDER BY acad_year_issued DESC, semester_issued DESC
            """,
            param=(student_no,)
        )

    def create_tree_section(self, parent, columns, query, param):
        # Clear old widgets in frame
        for widget in parent.winfo_children():
            widget.destroy()

        tree = ttk.Treeview(parent, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        tree.pack(fill="both", expand=True)

        cursor = self.controller.mydb.cursor()
        cursor.execute(query, param)
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)

import tkinter as tk
from tkinter import ttk, messagebox

class ViewFeesPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.student_no = None   
        tk.Label(self, text="Your Fee Records", font=("Arial", 16)).pack(pady=10)

        self.tree = ttk.Treeview(
            self,
            columns=["Org", "Ref No", "Type", "Balance", "Due Date", "Date Paid"],
            show="headings",
            selectmode="browse"
        )
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        for col in ["Org", "Ref No", "Type", "Balance", "Due Date", "Date Paid"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        tk.Button(self, text="Mark Selected Fee as Paid", command=self.mark_fee_as_paid).pack(pady=10)

        tk.Button(self, text="Back", command=lambda: controller.show_frame("StudentHomePage")).pack()

    def load_fees(self, student_no):
        self.student_no = student_no
        for row in self.tree.get_children():
            self.tree.delete(row)

        cursor = self.controller.mydb.cursor()
        cursor.execute("""
            SELECT org_name, reference_no, type, balance, due_date, date_paid
            FROM fee
            WHERE student_no = %s
            ORDER BY acad_year_issued DESC, semester_issued DESC
        """, (student_no,))

        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def mark_fee_as_paid(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("No selection", "Please select a fee from the list.")
            return

        values = self.tree.item(selected_item)["values"]
        ref_no = values[1]  
        date_paid = values[5]
        print(date_paid)

        if date_paid != "None":
            messagebox.showinfo("Already Paid", "This fee has already been marked as paid.")
            return
        
        try:
            cursor = self.controller.mydb.cursor()
            # Update fee row, setting date_paid to today
            cursor.execute("""
                UPDATE fee
                SET date_paid = CURDATE(), balance = 0
                WHERE reference_no = %s AND student_no = %s
            """, (ref_no, self.student_no))
            self.controller.mydb.commit()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update fee: {e}")
            return

        messagebox.showinfo("Success", f"Fee {ref_no} marked as paid.")
        self.load_fees(self.student_no)