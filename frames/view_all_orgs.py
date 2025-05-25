import getpass
import mysql.connector as mariadb
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

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
        btn_back = tk.Button(self, text="Back to Home", 
                           command=lambda: controller.show_frame("HomePage"))
        btn_back.pack()

        label = tk.Label(left_frame, text="All Organizations", font=("Arial", 16))
        label.pack(pady=10)

        # Add Org Entry + Button
        entry_frame = tk.Frame(left_frame)
        entry_frame.pack(pady=5)

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
            self.controller.mydb.commit()
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
