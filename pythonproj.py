## install mysql
## type pip install mysql-connector-python into command line

import getpass
import mysql.connector as mariadb

## each user logs in as admin to gain access to the 
password = input("Password for root user: ")

mydb = mariadb.connect(
    host="localhost",
    user="root",
    password=password
)

cursor = mydb.cursor()

##create database
cursor.execute("SHOW DATABASES")

for x in cursor:
    print(x)

# Drop the database if it exists
cursor.execute("DROP DATABASE IF EXISTS project")
print("Dropped database 'project' if it existed.")

# Create the database if it does not exist
cursor.execute("CREATE DATABASE IF NOT EXISTS project")
print("Created database 'project' if it didn't exist already.")

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
cursor.execute(create_student_table)
print("Created table 'student'.")


cursor.execute("SHOW TABLES")

tables = cursor.fetchall()

print("Tables in 'project' database:")
for table in tables:
    print(table[0])  # Each table name is inside a tuple