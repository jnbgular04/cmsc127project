import tkinter as tk
from tkinter import ttk, messagebox

class OrgFinancesPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.selected_org = tk.StringVar()
        self.selected_semester = tk.StringVar()
        self.selected_ay = tk.StringVar()

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

        # --- Treeview for fees ---
        columns = ["Ref No", "Student No", "Type", "Balance", "Due Date", "Date Paid"]
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        # --- Totals section ---
        self.totals_label = tk.Label(self, text="", font=("Arial", 12))
        self.totals_label.pack(pady=5)

        # --- Back Button ---
        tk.Button(self, text="Back to Admin Home", command=lambda: controller.show_frame("AdminHomePage")).pack(pady=10)

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
                SELECT reference_no, student_no, type, balance, due_date, date_paid
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

            cursor.execute(query, params)
            rows = cursor.fetchall()

            total_paid = 0
            total_unpaid = 0
            total_balance = 0.0

            for row in rows:
                self.tree.insert("", "end", values=row)
                balance = row[3]
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
