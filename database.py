import mysql.connector as mariadb

def create_connection():
    #MAIN PROGRAM
    # password = input("Password for root user: ")
    password = "JazminMaria@2004"

    return mariadb.connect(
        host="localhost",
        user="root",
        password=password
    )