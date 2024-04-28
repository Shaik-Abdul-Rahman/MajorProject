import mysql.connector

# Connect to MySQL Server
connection = mysql.connector.connect(database = 'db-hlx8d21axvv7',
username = 'db-hlx8d21axvv7',
password = 'QPDMAVVtbc39RG0l4R0ytGsO',
host = 'up-us-sjo1-mysql-1.db.run-on-seenode.com',
port = 11550)


# Create a Cursor Object
cursor = connection.cursor()

# Execute SQL Command to Select the First Row
cursor.execute("SHOW TABLES")

tables = cursor.fetchall()

    # Iterate over the list of tables and print their names
for table in tables:
    print(table[0])

cursor.close()
connection.close()