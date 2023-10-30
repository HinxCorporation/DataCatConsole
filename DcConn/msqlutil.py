import mysql.connector

import Config.config as config


def create_conn():
    # Connect to MySQL
    cnx = mysql.connector.connect(
        host=config.get_mysql_host(),
        port=config.get_mysql_port(),
        user=config.get_mysql_user(),
        password=config.get_mysql_pwd(),
        database=config.get_mysql_database()
    )
    return cnx


# Check if the connection is successful
def check_connection(cnx):
    if cnx.is_connected():
        print("Connection established.")
        return True
    else:
        print("Connection failed.")
        return False

# Define the SQL query for inserting into the table
