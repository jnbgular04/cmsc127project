import tkinter as tk
from tkinter import ttk, messagebox

class OrgDetailsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.org_name = None
        self.current_org = None

        # Back button
        btn_back = tk.Button(self, text="Back to Orgs Page",
                             command=lambda: controller.show_frame("OrgsPage"))
        btn_back.pack(pady=10)

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

        # Main Notebook for Org Details and Reports
        self.main_notebook = ttk.Notebook(self)
        self.main_notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Org Details Tabs ---
        self.tree_members = self.create_tab("Members", ["Student No", "Name", "Status", "Semester", "AY"])
        self.tree_committees = self.create_tab("Committees", ["Committee Name"])
        self.tree_events = self.create_tab("Events", ["Event Name"])
        self.tree_fees = self.create_tab("Fees", ["Ref No", "Student No", "Type", "Balance", "Due Date", "Date Paid"])

        # --- Reports Tabs ---
        self.reports_notebook = ttk.Notebook(self)
        self.reports_notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Executive Committee Tab
        self.tab_exec = ttk.Frame(self.reports_notebook)
        self.reports_notebook.add(self.tab_exec, text="Executive Committee")
        tk.Label(self.tab_exec, text="Academic Year:").pack(side=tk.LEFT, padx=5, pady=10)
        self.selected_ay = tk.StringVar()
        self.ay_dropdown = ttk.Combobox(self.tab_exec, textvariable=self.selected_ay, width=15, state="readonly")
        self.ay_dropdown.pack(side=tk.LEFT, padx=5)
        tk.Button(self.tab_exec, text="Generate", command=self.view_executive_committee).pack(side=tk.LEFT, padx=5)
        self.tree_exec = self.create_treeview(self.tab_exec, ["Student No", "Full Name", "Executive Role", "Term"])

        # Active/Inactive Tab
        self.tab_active = ttk.Frame(self.reports_notebook)
        self.reports_notebook.add(self.tab_active, text="Active/Inactive Members")
        tk.Label(self.tab_active, text="Last n Semesters:").pack(side=tk.LEFT, padx=5, pady=10)
        self.n_sem_entry = tk.Entry(self.tab_active, width=5)
        self.n_sem_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(self.tab_active, text="Generate", command=self.view_active_inactive).pack(side=tk.LEFT, padx=5)
        self.tree_active = self.create_treeview(self.tab_active, ["Term", "Active", "Inactive", "Total", "% Active", "% Inactive"])

        # Officers Tab
        self.tab_officers = ttk.Frame(self.reports_notebook)
        self.reports_notebook.add(self.tab_officers, text="Past Officers")

        officers_container = tk.Frame(self.tab_officers)
        officers_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Left: Input Panel
        input_frame = tk.Frame(officers_container)
        input_frame.pack(side=tk.LEFT, anchor="n", padx=10)

        tk.Label(input_frame, text="Role:").pack(pady=5, anchor="w")
        self.selected_role = tk.StringVar()
        self.role_entry = ttk.Combobox(input_frame, textvariable=self.selected_role, width=20, state="readonly")
        self.role_entry.pack(pady=5)

        tk.Label(input_frame, text="Last n Semesters (optional):").pack(pady=5, anchor="w")
        self.pres_n_sem_entry = tk.Entry(input_frame, width=5)
        self.pres_n_sem_entry.pack(pady=5)

        tk.Button(input_frame, text="Generate", command=self.view_officers).pack(pady=10)

        # Right: Treeview
        self.tree_officers = self.create_treeview(officers_container, ["Student No", "Full Name", "Term"])


    def create_tab(self, title, columns):
        frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(frame, text=title)
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")
        tree.pack(fill="both", expand=True)
        return tree

    def create_treeview(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=130)
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        return tree

    def load_organization(self, org_name):
        self.org_name = org_name
        self.current_org = org_name
        self.label_title.config(text=f"Organization: {org_name}")

        conn = self.controller.mydb
        cursor = conn.cursor()

        try:
            for tree in [self.tree_members, self.tree_committees, self.tree_events, self.tree_fees,
                         self.tree_exec, self.tree_active, self.tree_officers]:
                tree.delete(*tree.get_children())

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

            cursor.execute("SELECT comm_name FROM committee WHERE org_name = %s", (org_name,))
            for row in cursor.fetchall():
                self.tree_committees.insert("", "end", values=row)

            cursor.execute("SELECT event FROM organization_event WHERE org_name = %s", (org_name,))
            for row in cursor.fetchall():
                self.tree_events.insert("", "end", values=row)

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

            cursor.execute("""
                SELECT DISTINCT acad_year FROM membership
                WHERE org_name = %s ORDER BY acad_year DESC
            """, (org_name,))
            ay_list = [row[0] for row in cursor.fetchall()]
            self.ay_dropdown["values"] = ay_list
            if ay_list:
                self.selected_ay.set(ay_list[0])

            # Load executive roles dynamically
            self.load_executive_roles()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_executive_committee(self):
        org = self.current_org
        ay = self.selected_ay.get()
        if not ay:
            messagebox.showwarning("Missing AY", "Select an academic year.")
            return
        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("""
                SELECT s.student_no,
                    CONCAT(s.last_name, ', ', s.first_name,
                        CASE WHEN s.middle_name IS NOT NULL AND s.middle_name != ''
                        THEN CONCAT(' ', s.middle_name) ELSE '' END) AS full_name,
                    ca.role,
                    CONCAT(ca.semester, ' Sem. ', ca.acad_year)
                FROM student s
                JOIN membership m ON s.student_no = m.student_no AND m.org_name = %s
                JOIN committee_assignment ca ON s.student_no = ca.student_no AND m.org_name = ca.org_name
                AND m.acad_year = ca.acad_year AND m.semester = ca.semester
                JOIN committee c ON ca.org_name = c.org_name AND ca.comm_name = c.comm_name
                WHERE ca.comm_name = 'Executive' AND ca.acad_year = %s
                ORDER BY ca.acad_year, ca.semester
            """, (org, ay))
            rows = cursor.fetchall()
            self.populate_tree(self.tree_exec, ["Student No", "Full Name", "Executive Role", "Term"], rows)
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
            self.populate_tree(self.tree_active,
                ["Term", "Active", "Inactive", "Total", "% Active", "% Inactive"], results)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_officers(self):
        org = self.current_org
        role = self.selected_role.get().strip()
        n_semesters = self.pres_n_sem_entry.get().strip()

        if not role:
            messagebox.showwarning("Missing Role", "Please select a role.")
            return

        try:
            cursor = self.controller.mydb.cursor()

            if n_semesters:
                try:
                    n = int(n_semesters)
                except ValueError:
                    messagebox.showerror("Invalid Input", "Enter a valid number of semesters.")
                    return

                cursor.execute("""
                    SELECT DISTINCT acad_year, semester
                    FROM committee_assignment
                    WHERE org_name = %s
                    ORDER BY acad_year DESC, FIELD(semester, '2nd', '1st')
                    LIMIT %s
                """, (org, n))
                terms = cursor.fetchall()

                term_filter = " OR ".join(["(ca.acad_year = %s AND ca.semester = %s)"] * len(terms))
                term_params = []
                for ay, sem in terms:
                    term_params.extend([ay, sem])

                query = f"""
                    SELECT s.student_no,
                        CONCAT(s.last_name, ', ', s.first_name,
                            CASE WHEN s.middle_name IS NOT NULL AND s.middle_name != ''
                            THEN CONCAT(' ', s.middle_name) ELSE '' END) AS full_name,
                        CONCAT(ca.semester, ' Sem. ', ca.acad_year)
                    FROM student s
                    JOIN committee_assignment ca ON s.student_no = ca.student_no
                    WHERE ca.org_name = %s AND ca.role = %s AND ({term_filter})
                    ORDER BY ca.acad_year DESC, ca.semester DESC
                """
                cursor.execute(query, [org, role] + term_params)
            else:
                cursor.execute("""
                    SELECT s.student_no,
                        CONCAT(s.last_name, ', ', s.first_name,
                            CASE WHEN s.middle_name IS NOT NULL AND s.middle_name != ''
                            THEN CONCAT(' ', s.middle_name) ELSE '' END) AS full_name,
                        CONCAT(ca.semester, ' Sem. ', ca.acad_year)
                    FROM student s
                    JOIN committee_assignment ca ON s.student_no = ca.student_no
                    WHERE ca.org_name = %s AND ca.role = %s
                    ORDER BY ca.acad_year DESC, ca.semester DESC
                """, (org, role))

            rows = cursor.fetchall()
            self.populate_tree(self.tree_officers, ["Student No", "Full Name", "Term"], rows)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_executive_roles(self):
        """Fetch and populate distinct executive roles for the current organization."""
        if not self.current_org:
            return
        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("""
                SELECT DISTINCT role
                FROM committee_assignment
                WHERE org_name = %s AND comm_name = 'Executive'
                ORDER BY role
            """, (self.current_org,))
            roles = [row[0] for row in cursor.fetchall()]
            self.role_entry["values"] = roles
            if roles:
                self.selected_role.set(roles[0])  # Optionally auto-select first role
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load executive roles.\n{str(e)}")


    def populate_tree(self, tree, columns, rows):
        tree.delete(*tree.get_children())
        tree["columns"] = columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=130)
        for row in rows:
            tree.insert("", "end", values=row)
