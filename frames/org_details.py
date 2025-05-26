import tkinter as tk
from tkinter import ttk, messagebox

class OrgDetailsPage(tk.Frame):
    def __init__(self, parent, controller): 
        super().__init__(parent)
        self.controller = controller
        self.org_name = None
        self.current_org = None  # For consistency with report usage

        # Title
        self.label_title = tk.Label(self, text="", font=("Arial", 18, "bold"))
        self.label_title.pack(pady=10)

        # Summary Frame
        summary_frame = tk.Frame(self)
        summary_frame.pack(pady=5)

        self.label_members = tk.Label(summary_frame, text="Members: 0", width=25)
        self.label_members.pack(side=tk.LEFT, padx=10)

        self.label_committees = tk.Label(summary_frame, text="Committees: 0", width=25)
        self.label_committees.pack(side=tk.LEFT, padx=10)

        self.label_fees = tk.Label(summary_frame, text="Unpaid Fees: 0", width=25)
        self.label_fees.pack(side=tk.LEFT, padx=10)

        self.label_events = tk.Label(summary_frame, text="Events: 0", width=25)
        self.label_events.pack(side=tk.LEFT, padx=10)

        # Tabs for org details
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree_members = self.create_tab("Members", ["Student No", "Name", "Status", "Semester", "AY"])
        self.tree_committees = self.create_tab("Committees", ["Committee Name"])
        self.tree_events = self.create_tab("Events", ["Event Name"])
        self.tree_fees = self.create_tab("Fees", ["Ref No", "Student No", "Type", "Balance", "Due Date", "Date Paid"])

        # --- Reports Section ---
        self.reports_frame = tk.LabelFrame(self, text="Reports", padx=10, pady=10)
        self.reports_frame.pack(fill="x", padx=20, pady=10)

        # AY dropdown
        tk.Label(self.reports_frame, text="Academic Year:").grid(row=0, column=0, padx=5)
        self.selected_ay = tk.StringVar()
        self.ay_dropdown = ttk.Combobox(self.reports_frame, textvariable=self.selected_ay, width=15, state="readonly")
        self.ay_dropdown.grid(row=0, column=1)

        # Last n semesters
        tk.Label(self.reports_frame, text="Last n Semesters:").grid(row=0, column=2, padx=5)
        self.n_sem_entry = tk.Entry(self.reports_frame, width=5)
        self.n_sem_entry.grid(row=0, column=3)

        # Report buttons
        tk.Button(self.reports_frame, text="Executive Committee", command=self.view_executive_committee).grid(row=1, column=0, pady=5)
        tk.Button(self.reports_frame, text="Active/Inactive Summary", command=self.view_active_inactive).grid(row=1, column=1)
        tk.Button(self.reports_frame, text="View Presidents", command=self.view_presidents).grid(row=1, column=2)

        # Treeview for displaying report results
        self.report_tree = ttk.Treeview(self.reports_frame, show="headings", height=10)
        self.report_tree.grid(row=2, column=0, columnspan=5, pady=10, sticky="ew")

        # Back button
        btn_back = tk.Button(self, text="Back to Orgs Page",
                            command=lambda: controller.show_frame("OrgsPage"))
        btn_back.pack(pady=10)


    def create_tab(self, title, columns):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)

        tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")
        tree.pack(fill="both", expand=True)
        return tree

    def load_organization(self, org_name):
        self.org_name = org_name
        self.current_org = org_name
        self.label_title.config(text=f"Organization: {org_name}")

        conn = self.controller.mydb
        cursor = conn.cursor()

        try:
            # Clear all trees
            for tree in [self.tree_members, self.tree_committees, self.tree_events, self.tree_fees]:
                tree.delete(*tree.get_children())

            # Load members
            cursor.execute("""
                SELECT m.student_no, CONCAT(s.first_name, ' ', s.last_name), m.status, m.semester, m.acad_year
                FROM membership m
                JOIN student s ON s.student_no = m.student_no
                WHERE m.org_name = %s
            """, (org_name,))
            members = cursor.fetchall()
            self.label_members.config(text=f"Members: {len(members)}")
            for row in members:
                self.tree_members.insert("", "end", values=row)

            # Load committees
            cursor.execute("SELECT comm_name FROM committee WHERE org_name = %s", (org_name,))
            committees = cursor.fetchall()
            self.label_committees.config(text=f"Committees: {len(committees)}")
            for row in committees:
                self.tree_committees.insert("", "end", values=row)

            # Load events
            cursor.execute("SELECT event FROM organization_event WHERE org_name = %s", (org_name,))
            events = cursor.fetchall()
            self.label_events.config(text=f"Events: {len(events)}")
            for row in events:
                self.tree_events.insert("", "end", values=row)

            # Load unpaid fees
            cursor.execute("""
                SELECT reference_no, student_no, type, balance, due_date, date_paid
                FROM fee
                WHERE org_name = %s AND date_paid IS NULL
            """, (org_name,))
            fees = cursor.fetchall()
            unpaid_count = sum(1 for f in fees if f[3] > 0)
            self.label_fees.config(text=f"Unpaid Fees: {unpaid_count}")
            for row in fees:
                self.tree_fees.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def populate_report_tree(self, columns, rows):
        self.report_tree.delete(*self.report_tree.get_children())
        self.report_tree["columns"] = columns
        for col in columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, anchor="center", width=130)
        for row in rows:
            self.report_tree.insert("", "end", values=row)

    def view_executive_committee(self):
        org = self.current_org
        ay = self.selected_ay.get()
        if not ay:
            messagebox.showwarning("Missing AY", "Select an academic year.")
            return
        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("""
                SELECT s.student_no, CONCAT(s.last_name, ', ', s.first_name, IFNULL(CONCAT(' ', s.middle_name), '')) AS full_name,
                    ca.role, CONCAT(ca.semester, ' Sem. ', ca.acad_year) AS term
                FROM student s
                JOIN committee_assignment ca ON s.student_no = ca.student_no
                WHERE ca.org_name = %s AND ca.comm_name = 'Executive' AND ca.acad_year = %s
                ORDER BY ca.acad_year, ca.semester
            """, (org, ay))
            rows = cursor.fetchall()
            self.populate_report_tree(["Student No", "Full Name", "Executive Role", "Term"], rows)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_active_inactive(self):
        org = self.current_org
        try:
            n = int(self.n_sem_entry.get())
        except ValueError:
            messagebox.showwarning("Invalid Input", "Enter a valid number of semesters.")
            return
        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("""
                SELECT DISTINCT acad_year, semester
                FROM membership
                WHERE org_name = %s
                ORDER BY acad_year DESC, FIELD(semester, '2nd', '1st')
                LIMIT %s
            """, (org, n))
            terms = cursor.fetchall()
            results = []
            for ay, sem in terms:
                cursor.execute("""
                    SELECT
                        SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END),
                        SUM(CASE WHEN status = 'Inactive' THEN 1 ELSE 0 END),
                        COUNT(*)
                    FROM membership
                    WHERE org_name = %s AND acad_year = %s AND semester = %s
                """, (org, ay, sem))
                active, inactive, total = cursor.fetchone()
                if total == 0: continue
                results.append((
                    f"{sem} Sem. {ay}", active, inactive, total,
                    round(100 * active / total, 2),
                    round(100 * inactive / total, 2)
                ))
            self.populate_report_tree(
                ["Term", "Active", "Inactive", "Total", "% Active", "% Inactive"],
                results
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_presidents(self):
        org = self.current_org
        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("""
                SELECT s.student_no, CONCAT(s.last_name, ', ', s.first_name, IFNULL(CONCAT(' ', s.middle_name), '')) AS full_name,
                    CONCAT(ca.semester, ' Sem. ', ca.acad_year)
                FROM student s
                JOIN committee_assignment ca ON s.student_no = ca.student_no
                WHERE ca.org_name = %s AND ca.role = 'President'
                ORDER BY ca.acad_year DESC, ca.semester DESC
            """, (org,))
            rows = cursor.fetchall()
            self.populate_report_tree(["Student No", "Full Name", "Term"], rows)
        except Exception as e:
            messagebox.showerror("Error", str(e))
