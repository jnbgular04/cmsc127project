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

        # Main Notebook for Org Details and Reports
        self.main_notebook = ttk.Notebook(self)
        self.main_notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Org Details Tabs ---
        # Members Tab (Modified)
        self.tab_members = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.tab_members, text="Members")

        # Filtering options for Members tab
        filter_frame = tk.LabelFrame(self.tab_members, text="Filter Members")
        filter_frame.pack(pady=10, padx=10, fill="x")

        # Filter widgets
        filter_widgets = {}
        row_num = 0
        col_num = 0

        labels_and_vars = {
            "Status:": (tk.StringVar(), ['Active', 'Inactive', 'Expelled', 'Suspended', 'Alumni']),
            "Gender:": (tk.StringVar(), ['Male', 'Female']),
            "Degree Program:": (tk.StringVar(), []), # Will be populated from DB
            "Batch (Year Joined):": (tk.StringVar(), []), # Will be populated from DB
            "Committee:": (tk.StringVar(), []), # Will be populated from DB
            "Role:": (tk.StringVar(), []) # Will be populated from DB
        }

        self.filter_vars = {} # Store StringVar objects for easy access
        for label_text, (var, values) in labels_and_vars.items():
            tk.Label(filter_frame, text=label_text).grid(row=row_num, column=col_num, padx=5, pady=2, sticky="w")
            combo = ttk.Combobox(filter_frame, textvariable=var, values=values, state="readonly", width=20)
            combo.grid(row=row_num, column=col_num + 1, padx=5, pady=2, sticky="ew")
            combo.set("") # Set default empty value
            # Store var with a clean key, ensuring 'batch' is correctly mapped
            clean_key = label_text.replace(":", "").strip().lower().replace(" ", "_")
            if "batch_(year_joined)" in clean_key:
                clean_key = "batch" # Explicitly set for batch
            self.filter_vars[clean_key] = var
            filter_widgets[label_text] = combo # Store combo for later population

            col_num += 2
            if col_num >= 6: # 3 pairs of label/combobox per row
                row_num += 1
                col_num = 0

        # Filter and Clear Buttons
        btn_filter = tk.Button(filter_frame, text="Apply Filters", command=self.apply_member_filters)
        btn_filter.grid(row=row_num, column=0, columnspan=3, pady=10)
        btn_clear_filters = tk.Button(filter_frame, text="Clear Filters", command=self.clear_member_filters)
        btn_clear_filters.grid(row=row_num, column=3, columnspan=3, pady=10)


        self.tree_members = self.create_treeview(self.tab_members, [
            "Student No", "Name", "Status", "Gender", "Degree Program", "Batch", "Committee", "Role", "Semester", "AY"
        ])
        self.tree_members.pack(fill="both", expand=True) # Pack it after the filter frame

        self.tree_committees = self.create_tab("Committees", ["Committee Name"])
        self.tree_events = self.create_tab("Events", ["Event Name"])

        # --- Reports Tabs --- (Existing code, unchanged)
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

        # Active/Inactive Tab
        self.tab_active = ttk.Frame(self.reports_notebook)
        self.reports_notebook.add(self.tab_active, text="Active/Inactive Members")
        tk.Label(self.tab_active, text="Last n Semesters:").pack(side=tk.LEFT, padx=5, pady=10)
        self.n_sem_entry = tk.Entry(self.tab_active, width=5)
        self.n_sem_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(self.tab_active, text="Generate", command=self.view_active_inactive).pack(side=tk.LEFT, padx=5)
        self.tree_active = self.create_treeview(self.tab_active, ["Term", "Active", "Inactive", "Total", "% Active", "% Inactive"])

        # Alumni Tab
        self.tab_alumni = ttk.Frame(self.reports_notebook)
        self.reports_notebook.add(self.tab_alumni, text="Alumni as of Date")

        alumni_container = tk.Frame(self.tab_alumni)
        alumni_container.pack(fill="both", expand=True, padx=10, pady=10)

        input_frame = tk.Frame(alumni_container)
        input_frame.pack(side=tk.LEFT, anchor="n", padx=10)

        tk.Label(input_frame, text="As of Date (YYYY-MM-DD):").pack(pady=5, anchor="w")
        self.alumni_date_entry = tk.Entry(input_frame, width=15)
        self.alumni_date_entry.pack(pady=5)

        tk.Button(input_frame, text="Generate", command=self.view_alumni).pack(pady=10)

        self.tree_alumni = self.create_treeview(alumni_container, ["Student No", "Full Name", "Degree Program", "Date Graduated"])


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
            for tree in [self.tree_members, self.tree_committees, self.tree_events,
                         self.tree_exec, self.tree_active, self.tree_officers, self.tree_alumni]:
                tree.delete(*tree.get_children())

            # Initial load for members tab (without filters)
            self.load_members()

            cursor.execute("SELECT comm_name FROM committee WHERE org_name = %s", (org_name,))
            for row in cursor.fetchall():
                self.tree_committees.insert("", "end", values=row)

            cursor.execute("SELECT event FROM organization_event WHERE org_name = %s", (org_name,))
            for row in cursor.fetchall():
                self.tree_events.insert("", "end", values=row)

            cursor.execute("""
                SELECT DISTINCT acad_year FROM membership
                WHERE org_name = %s ORDER BY acad_year DESC
            """, (org_name,))
            ay_list = [row[0] for row in cursor.fetchall()]
            self.ay_dropdown["values"] = ay_list
            if ay_list:
                self.selected_ay.set(ay_list[0])

            self.load_member_filter_options() # New method to load filter options
            self.load_executive_roles()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_members(self, filters=None):
        """Loads members into tree_members, applying filters if provided."""
        if not self.current_org:
            return

        conn = self.controller.mydb
        cursor = conn.cursor()
        self.tree_members.delete(*self.tree_members.get_children())

        base_query = """
            SELECT
                s.student_no,
                CONCAT(s.first_name, ' ', s.last_name) AS name,
                m.status,
                s.sex AS gender,
                s.degree_program,
                m.year_joined AS batch,
                ca.comm_name,
                ca.role,
                m.semester,
                m.acad_year
            FROM membership m
            JOIN student s ON s.student_no = m.student_no
            LEFT JOIN committee_assignment ca
                ON ca.student_no = m.student_no AND ca.org_name = m.org_name
                AND ca.acad_year = m.acad_year AND ca.semester = m.semester
            WHERE m.org_name = %s
        """
        params = [self.current_org]
        where_clauses = []

        if filters:
            if filters.get("status"):
                where_clauses.append("m.status = %s")
                params.append(filters["status"])
            if filters.get("gender"):
                where_clauses.append("s.sex = %s")
                params.append(filters["gender"])
            if filters.get("degree_program"):
                where_clauses.append("s.degree_program = %s")
                params.append(filters["degree_program"])
            if filters.get("batch"):
                where_clauses.append("m.year_joined = %s")
                params.append(filters["batch"])
            if filters.get("committee"):
                where_clauses.append("ca.comm_name = %s")
                params.append(filters["committee"])
            if filters.get("role"):
                where_clauses.append("ca.role = %s")
                params.append(filters["role"])

        if where_clauses:
            base_query += " AND " + " AND ".join(where_clauses)

        base_query += " ORDER BY m.acad_year DESC, m.semester DESC"

        try:
            cursor.execute(base_query, params)
            members = cursor.fetchall()
            self.label_members.config(text=f"Members: {len(members)}")
            for row in members:
                self.tree_members.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load members.\n{str(e)}")

    def apply_member_filters(self):
        """Collects filter values and reloads the members treeview."""
        filters = {
            "status": self.filter_vars["status"].get() if self.filter_vars["status"].get() else None,
            "gender": self.filter_vars["gender"].get() if self.filter_vars["gender"].get() else None,
            "degree_program": self.filter_vars["degree_program"].get() if self.filter_vars["degree_program"].get() else None,
            "batch": self.filter_vars["batch"].get() if self.filter_vars["batch"].get() else None,
            "committee": self.filter_vars["committee"].get() if self.filter_vars["committee"].get() else None,
            "role": self.filter_vars["role"].get() if self.filter_vars["role"].get() else None,
        }
        # Remove empty filters
        active_filters = {k: v for k, v in filters.items() if v}
        self.load_members(active_filters)

    def clear_member_filters(self):
        """Clears all filter comboboxes and reloads all members."""
        for var in self.filter_vars.values():
            var.set("")
        self.load_members() # Reload all members without filters

    def load_member_filter_options(self):
        """Populates the comboboxes with distinct values from the database."""
        if not self.current_org:
            return

        conn = self.controller.mydb
        cursor = conn.cursor()

        try:
            # Populate Degree Program
            cursor.execute("SELECT DISTINCT degree_program FROM student ORDER BY degree_program")
            degree_programs = [row[0] for row in cursor.fetchall()]
            # Find the combobox for degree program and update its values
            for child in self.tab_members.winfo_children():
                if isinstance(child, tk.LabelFrame): # This is our filter_frame
                    for gc in child.winfo_children():
                        if isinstance(gc, ttk.Combobox) and gc.cget("textvariable") == str(self.filter_vars["degree_program"]):
                            gc["values"] = degree_programs
                            break

            # Populate Batch (year_joined)
            cursor.execute("SELECT DISTINCT year_joined FROM membership WHERE org_name = %s ORDER BY year_joined DESC", (self.current_org,))
            batches = [row[0] for row in cursor.fetchall()]
            for child in self.tab_members.winfo_children():
                if isinstance(child, tk.LabelFrame):
                    for gc in child.winfo_children():
                        if isinstance(gc, ttk.Combobox) and gc.cget("textvariable") == str(self.filter_vars["batch"]):
                            gc["values"] = batches
                            break

            # Populate Committee Names
            cursor.execute("SELECT DISTINCT comm_name FROM committee WHERE org_name = %s ORDER BY comm_name", (self.current_org,))
            committees = [row[0] for row in cursor.fetchall()]
            for child in self.tab_members.winfo_children():
                if isinstance(child, tk.LabelFrame):
                    for gc in child.winfo_children():
                        if isinstance(gc, ttk.Combobox) and gc.cget("textvariable") == str(self.filter_vars["committee"]):
                            gc["values"] = committees
                            break

            # Populate Roles (from committee_assignment)
            cursor.execute("SELECT DISTINCT role FROM committee_assignment WHERE org_name = %s ORDER BY role", (self.current_org,))
            roles = [row[0] for row in cursor.fetchall()]
            for child in self.tab_members.winfo_children():
                if isinstance(child, tk.LabelFrame):
                    for gc in child.winfo_children():
                        if isinstance(gc, ttk.Combobox) and gc.cget("textvariable") == str(self.filter_vars["role"]):
                            gc["values"] = roles
                            break

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load filter options.\n{str(e)}")

    def view_executive_committee(self):
        org = self.current_org
        print(org)
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

    def view_alumni(self):
        org = self.current_org
        as_of_date = self.alumni_date_entry.get().strip()

        if not as_of_date:
            messagebox.showwarning("Missing Date", "Please enter a valid date.")
            return

        try:
            cursor = self.controller.mydb.cursor()
            cursor.execute("""
                SELECT s.student_no,
                    CONCAT(s.last_name, ', ', s.first_name,
                                CASE WHEN s.middle_name IS NOT NULL AND s.middle_name != ''
                                    THEN CONCAT(' ', s.middle_name) ELSE '' END) AS full_name,
                    s.degree_program,
                    s.date_graduated
                FROM student s
                JOIN membership m ON s.student_no = m.student_no
                WHERE m.org_name = %s AND s.date_graduated IS NOT NULL AND s.date_graduated <= %s
                ORDER BY s.date_graduated DESC
            """, (org, as_of_date))

            rows = cursor.fetchall()
            self.populate_tree(self.tree_alumni,
                                ["Student No", "Full Name", "Degree Program", "Date Graduated"],
                                rows)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def populate_tree(self, tree, columns, rows):
        tree.delete(*tree.get_children())
        tree["columns"] = columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=130)
        for row in rows:
            tree.insert("", "end", values=row)