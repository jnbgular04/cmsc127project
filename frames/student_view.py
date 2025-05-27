from tkinter import ttk, messagebox
import tkinter as tk

class StudentViewPage(tk.Frame):
    def init(self, parent, controller):
        super().init(parent)
        self.controller = controller
        tk.Label(self, text="My Organization Involvement", font=("Arial", 18, "bold")).pack(pady=10)

    # TABS
    self.tabs = ttk.Notebook(self)
    self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

    self.tab_memberships = self.create_tab("My Memberships", ["Organization", "Status", "Year Joined", "Semester", "Academic Year"])
    self.tab_fees = self.create_tab("My Fees & Dues", ["Ref No", "Org", "Type", "Balance", "Due Date", "Date Paid"])
    self.tab_committees = self.create_tab("My Committee Roles", ["Organization", "Committee", "Role", "Semester", "Academic Year"])

    # Back button
    tk.Button(self, text="Back", command=lambda: controller.show_frame("StudentHomePage")).pack(pady=5)

    def create_tab(self, title, columns):
        frame = ttk.Frame(self.tabs)
        self.tabs.add(frame, text=title)

        tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        return tree

    def tkraise(self, *args, **kwargs):
        """Refreshes data each time the page is shown."""
        super().tkraise(*args, **kwargs)
        self.load_data()

    def load_data(self):
        student_no = getattr(self.controller, "student_no", None)
        if not student_no:
            messagebox.showerror("Not Logged In", "Student session not found.")
            return

    # LOAD MEMBERSHIPS
    self.load_tree_data(
        self.tab_memberships,
        """
        SELECT org_name, status, year_joined, semester, acad_year
        FROM membership
        WHERE student_no = %s
        ORDER BY acad_year DESC, semester DESC
        """,
        (student_no,)
    )

    # LOAD FEES
    self.load_tree_data(
        self.tab_fees,
        """
        SELECT reference_no, org_name, type, balance, due_date, date_paid
        FROM fee
        WHERE student_no = %s
        ORDER BY acad_year_issued DESC, semester_issued DESC
        """,
        (student_no,)
    )

    # LOAD COMMITTEES
    self.load_tree_data(
        self.tab_committees,
        """
        SELECT org_name, comm_name, role, semester, acad_year
        FROM committee_assignment
        WHERE student_no = %s
        ORDER BY acad_year DESC, semester DESC
        """,
        (student_no,)
    )

    def load_tree_data(self, tree, query, params):
        # Clear tree
        for item in tree.get_children():
            tree.delete(item)

        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute(query, params)
            for row in cursor.fetchall():
                tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

