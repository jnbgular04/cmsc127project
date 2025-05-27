import tkinter as tk
from tkinter import ttk, messagebox

class OrgFinancesPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.selected_org = tk.StringVar()
        self.selected_semester = tk.StringVar()
        self.selected_ay = tk.StringVar()

        # --- Back Button ---
        tk.Button(self, text="Back to Admin Home", command=lambda: controller.show_frame("AdminHomePage")).pack(pady=10)

        tk.Label(self, text="Organization Finances", font=("Arial", 18)).pack(pady=10)

        # --- Filter section ---
        filter_frame = tk.Frame(self)
        filter_frame.pack(pady=10)

        # Org Dropdown
        tk.Label(filter_frame, text="Organization:").grid(row=0, column=0, padx=5)
        self.org_dropdown = ttk.Combobox(filter_frame, textvariable=self.selected_org, state="readonly")
        self.org_dropdown.grid(row=0, column=1, padx=5)

        # Semester Dropdown
        tk.Label(filter_frame, text="Semester:").grid(row=0, column=2, padx=5)
        self.sem_dropdown = ttk.Combobox(filter_frame, textvariable=self.selected_semester, values=["", "1st", "2nd"], state="readonly")
        self.sem_dropdown.grid(row=0, column=3, padx=5)

        # AY Entry
        tk.Label(filter_frame, text="Academic Year:").grid(row=0, column=4, padx=5)
        self.ay_entry = tk.Entry(filter_frame, textvariable=self.selected_ay, width=10)
        self.ay_entry.grid(row=0, column=5, padx=5)

        # Buttons
        tk.Button(filter_frame, text="Filter", command=self.load_fees).grid(row=0, column=6, padx=10)
        tk.Button(filter_frame, text="Clear", command=self.clear_filters).grid(row=0, column=7, padx=5)

        # Checkbox for unpaid
        self.unpaid_only = tk.BooleanVar()
        tk.Checkbutton(filter_frame, text="Only Unpaid Membership Fees", variable=self.unpaid_only).grid(row=0, column=8, padx=10)

        # --- Treeview for fees ---
        columns = ["Ref No", "Student No", "Type", "Balance", "Due Date", "Date Paid", "Semester Issued", "AY Issued"]
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        # --- Totals section ---
        self.totals_label = tk.Label(self, text="", font=("Arial", 12))
        self.totals_label.pack(pady=5)

        # --- Reports Section ---
        self.reports_notebook = ttk.Notebook(self)
        self.reports_notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Highest Debt Tab ---
        self.tab_debt = ttk.Frame(self.reports_notebook)
        self.reports_notebook.add(self.tab_debt, text="Highest Debt")

        frame_debt = tk.Frame(self.tab_debt)
        frame_debt.pack(fill="both", expand=True, padx=10, pady=10)

        input_debt = tk.Frame(frame_debt)
        input_debt.pack(side=tk.LEFT, anchor="n", padx=10)

        tk.Label(input_debt, text="Semester:").pack(anchor="w")
        self.debt_semester = tk.StringVar()
        ttk.Combobox(input_debt, textvariable=self.debt_semester, values=["1st", "2nd"], width=10, state="readonly").pack(pady=5)

        tk.Label(input_debt, text="Academic Year:").pack(anchor="w")
        self.debt_ay = tk.StringVar()
        tk.Entry(input_debt, textvariable=self.debt_ay, width=12).pack(pady=5)

        tk.Button(input_debt, text="Generate", command=self.view_highest_debt).pack(pady=10)

        self.tree_debt = self.create_report_tree(frame_debt, ["Student No", "Full Name", "Total Balance"])


        # Total Paid/Unpaid Tab
        self.tab_total = ttk.Frame(self.reports_notebook)
        self.reports_notebook.add(self.tab_total, text="Total Paid vs Unpaid")

        frame_total = tk.Frame(self.tab_total)
        frame_total.pack(fill="both", expand=True, padx=10, pady=10)

        left_total = tk.Frame(frame_total)
        left_total.pack(side=tk.LEFT, anchor="n", padx=10)

        tk.Label(left_total, text="As of Date (YYYY-MM-DD):").pack(pady=5, anchor="w")
        self.total_date_var = tk.StringVar()
        tk.Entry(left_total, textvariable=self.total_date_var, width=15).pack(pady=5)

        tk.Button(left_total, text="Generate", command=self.view_total_paid_unpaid).pack(pady=10)

        self.tree_total = self.create_report_tree(frame_total, ["As of", "Total Paid (₱)", "Total Unpaid (₱)"])

        # --- Late Payments Tab ---
        self.tab_late = ttk.Frame(self.reports_notebook)
        self.reports_notebook.add(self.tab_late, text="Late Payments")

        frame_late = tk.Frame(self.tab_late)
        frame_late.pack(fill="both", expand=True, padx=10, pady=10)

        # Inputs
        left_late = tk.Frame(frame_late)
        left_late.pack(side=tk.LEFT, anchor="n", padx=10)

        tk.Label(left_late, text="Semester:").pack(pady=5, anchor="w")
        self.late_semester = tk.StringVar()
        ttk.Combobox(left_late, textvariable=self.late_semester, values=["1st", "2nd"], width=10, state="readonly").pack()

        tk.Label(left_late, text="Academic Year:").pack(pady=5, anchor="w")
        self.late_ay = tk.StringVar()
        tk.Entry(left_late, textvariable=self.late_ay, width=10).pack()

        tk.Button(left_late, text="Generate", command=self.view_late_payments).pack(pady=10)

        self.tree_late = self.create_report_tree(frame_late, ["Student No", "Full Name", "Ref No", "Due Date", "Date Paid"])

        # --- Unpaid Membership Fees Tab ---
        self.tab_unpaid = ttk.Frame(self.reports_notebook)
        self.reports_notebook.add(self.tab_unpaid, text="Unpaid Membership Fees")

        frame_unpaid = tk.Frame(self.tab_unpaid)
        frame_unpaid.pack(fill="both", expand=True, padx=10, pady=10)

        left_unpaid = tk.Frame(frame_unpaid)
        left_unpaid.pack(side=tk.LEFT, anchor="n", padx=10)

        tk.Label(left_unpaid, text="Semester:").pack(pady=5, anchor="w")
        self.unpaid_semester = tk.StringVar()
        ttk.Combobox(left_unpaid, textvariable=self.unpaid_semester, values=["1st", "2nd"], width=10, state="readonly").pack()

        tk.Label(left_unpaid, text="Academic Year:").pack(pady=5, anchor="w")
        self.unpaid_ay = tk.StringVar()
        tk.Entry(left_unpaid, textvariable=self.unpaid_ay, width=10).pack()

        tk.Button(left_unpaid, text="Generate", command=self.view_unpaid_membership).pack(pady=10)

        self.tree_unpaid = self.create_report_tree(frame_unpaid, ["Student No", "Full Name", "Semester", "AY", "Balance"])


        self.load_organizations()

    def load_organizations(self):
        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("SELECT org_name FROM organization ORDER BY org_name")
            orgs = [row[0] for row in cursor.fetchall()]
            self.org_dropdown["values"] = orgs
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_filters(self):
        self.selected_org.set("")
        self.selected_semester.set("")
        self.selected_ay.set("")
        self.tree.delete(*self.tree.get_children())
        self.totals_label.config(text="")

    def load_fees(self):
        org = self.selected_org.get()
        sem = self.selected_semester.get()
        ay = self.selected_ay.get()

        if not org:
            messagebox.showwarning("Missing Info", "Please select an organization.")
            return

        self.tree.delete(*self.tree.get_children())

        try:
            cursor = self.controller.mydb.cursor()
            query = """
                SELECT *
                FROM fee
                WHERE org_name = %s
            """
            params = [org]

            if sem:
                query += " AND semester_issued = %s"
                params.append(sem)
            if ay:
                query += " AND acad_year_issued = %s"
                params.append(ay)
            if self.unpaid_only.get():
                query += " AND type = 'Membership' AND balance > 0"


            cursor.execute(query, params)
            rows = cursor.fetchall()

            total_paid = 0
            total_unpaid = 0
            total_balance = 0.0

            for row in rows:
                values = (
                    row[1],  # Ref No
                    row[8],  # Student No
                    row[5],  # Type
                    row[2],  # Balance
                    row[6],  # Due Date
                    row[7],  # Date Paid
                    row[3],  # Semester Issued
                    row[4],  # AY Issued
                )
                self.tree.insert("", "end", values=values)
                balance = row[2]
                total_balance += float(balance)
                if balance == 0:
                    total_paid += 1
                else:
                    total_unpaid += 1

            self.totals_label.config(
                text=f"Total Records: {len(rows)} | Paid: {total_paid} | Unpaid: {total_unpaid} | Total Balance: ₱{total_balance:.2f}"
            )

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_report_tree(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=130)
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        return tree

    def populate_tree(self, tree, columns, rows):
        tree.delete(*tree.get_children())
        tree["columns"] = columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=130)
        for row in rows:
            tree.insert("", "end", values=row)


    def view_highest_debt(self):
        org = self.selected_org.get().strip()
        sem = self.debt_semester.get().strip()
        ay = self.debt_ay.get().strip()

        if not org or not sem or not ay:
            messagebox.showwarning("Missing Info", "Please select organization, semester, and academic year.")
            return

        try:
            cursor = self.controller.mydb.cursor()

            # Sum balances by student for the given org/sem/ay
            cursor.execute("""
                SELECT s.student_no, CONCAT(s.last_name, ', ', s.first_name), SUM(f.balance) AS total_debt
                FROM fee f
                JOIN student s ON f.student_no = s.student_no
                WHERE f.org_name = %s AND f.semester_issued = %s AND f.acad_year_issued = %s
                GROUP BY s.student_no
                HAVING total_debt = (
                    SELECT MAX(total_balance)
                    FROM (
                        SELECT SUM(balance) AS total_balance
                        FROM fee
                        WHERE org_name = %s AND semester_issued = %s AND acad_year_issued = %s
                        GROUP BY student_no
                    ) AS sub
                )
            """, (org, sem, ay, org, sem, ay))

            rows = cursor.fetchall()
            self.populate_tree(self.tree_debt, ["Student No", "Full Name", "Total Balance"], rows)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_total_paid_unpaid(self):
        org = self.selected_org.get()
        date_str = self.total_date_var.get().strip()

        if not org or not date_str:
            messagebox.showwarning("Missing Info", "Please select an organization and input a date.")
            return

        try:
            cursor = self.controller.mydb.cursor()

            # Total paid
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0)
                FROM fee
                WHERE org_name = %s AND date_paid IS NOT NULL AND date_paid <= %s
            """, (org, date_str))
            total_paid = cursor.fetchone()[0]

            # Total unpaid (due but not paid)
            cursor.execute("""
                SELECT COALESCE(SUM(balance), 0)
                FROM fee
                WHERE org_name = %s AND date_paid IS NULL AND due_date <= %s
            """, (org, date_str))
            total_unpaid = cursor.fetchone()[0]

            # Display results
            self.populate_tree(self.tree_total, ["As of", "Total Paid (₱)", "Total Unpaid (₱)"], [
                (date_str, f"{total_paid:.2f}", f"{total_unpaid:.2f}")
            ])

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_late_payments(self):
        org = self.selected_org.get()
        sem = self.late_semester.get()
        ay = self.late_ay.get()

        if not org or not sem or not ay:
            messagebox.showwarning("Missing Info", "Please select organization, semester, and academic year.")
            return

        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("""
                SELECT s.student_no,
                    CONCAT(s.last_name, ', ', s.first_name),
                    f.reference_no,
                    f.due_date,
                    f.date_paid
                FROM fee f
                JOIN student s ON f.student_no = s.student_no
                WHERE f.org_name = %s
                AND f.semester_issued = %s
                AND f.acad_year_issued = %s
                AND f.date_paid IS NOT NULL
                AND f.date_paid > f.due_date
            """, (org, sem, ay))

            rows = cursor.fetchall()
            self.populate_tree(self.tree_late, ["Student No", "Full Name", "Ref No", "Due Date", "Date Paid"], rows)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_unpaid_membership(self):
        org = self.selected_org.get()
        sem = self.unpaid_semester.get()
        ay = self.unpaid_ay.get()

        if not org or not sem or not ay:
            messagebox.showwarning("Missing Info", "Please select organization, semester, and academic year.")
            return

        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("""
                SELECT s.student_no,
                    CONCAT(s.last_name, ', ', s.first_name),
                    f.semester_issued,
                    f.acad_year_issued,
                    f.balance
                FROM fee f
                JOIN student s ON f.student_no = s.student_no
                WHERE f.org_name = %s
                AND f.semester_issued = %s
                AND f.acad_year_issued = %s
                AND f.type = 'Membership'
                AND f.balance > 0
            """, (org, sem, ay))

            rows = cursor.fetchall()
            self.populate_tree(self.tree_unpaid, ["Student No", "Full Name", "Semester", "AY", "Balance"], rows)

        except Exception as e:
            messagebox.showerror("Error", str(e))
