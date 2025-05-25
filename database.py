import mysql.connector as mariadb

def create_connection():
    #MAIN PROGRAM
    password = input("Password for root user: ")


    return mariadb.connect(
        host="localhost",
        user="root",
        password=password
    )