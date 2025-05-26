import mysql.connector as mariadb
import getpass

def create_connection():
    #MAIN PROGRAM
    # password = input("Password for root user: ")
    password = getpass.getpass("Password for root user: ")


    return mariadb.connect(
        host="localhost",
        user="root",
        password=password
    )