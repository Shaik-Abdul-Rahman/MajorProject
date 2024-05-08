import mysql.connector

def delete_users_table():
    try:
        # Connect to the MySQL server
        conn = mysql.connector.connect(
        host='up-us-sjo1-mysql-1.db.run-on-seenode.com',
        port=11550,
        user='db-hlx8d21axvv7',
        password='QPDMAVVtbc39RG0l4R0ytGsO',
        database='db-hlx8d21axvv7'
    )

        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()

        alter_query = "ALTER TABLE users MODIFY rfid VARCHAR(20);"  # Adjust the size as needed
        cursor.execute(alter_query)

        # Commit the changes to the database
        conn.commit()

        print("Column size adjusted successfully")

    except mysql.connector.Error as error:
        print("Failed to adjust column size: {}".format(error))

    finally:
        # Close the cursor and connection
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# Call the function to delete the 'users' table
delete_users_table()
