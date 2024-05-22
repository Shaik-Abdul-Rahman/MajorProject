from mysql import connector

conn = connector.connect(database = 'db-hlx8d21axvv7',
username = 'db-hlx8d21axvv7',
password = 'QPDMAVVtbc39RG0l4R0ytGsO',
host = 'up-us-sjo1-mysql-1.db.run-on-seenode.com',
port = 11550)

cursor = conn.cursor()

#cursor.execute('CREAT TABLE users ')
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL
                )''')


sql = "INSERT INTO users (username, email) VALUES (%s, %s)"
values = [
    ("user1", "user1@example.com"),
    ("user2", "user2@example.com"),
    ("user3", "user3@example.com")
]

cursor.executemany(sql, values)


conn.commit()
conn.close()