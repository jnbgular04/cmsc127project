import mysql.connector as mariadb
import getpass

def create_connection():
    #MAIN PROGRAM
    # password = "JazminMaria@2004"
    password = getpass.getpass("Password for root user: ")


    return mariadb.connect(
        host="localhost",
        user="root",
        password=password
    )