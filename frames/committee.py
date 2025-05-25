import getpass
import mysql.connector as mariadb
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

class OrgCommittee(tk.Frame):
    def __init__(self, parent, controller):
