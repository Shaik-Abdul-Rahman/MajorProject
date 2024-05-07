from mysql import connector
import time
#from sensors import *

def get_db_connection():
    conn = connector.connect(
        host='up-us-sjo1-mysql-1.db.run-on-seenode.com',
        port=11550,
        user='db-hlx8d21axvv7',
        password='QPDMAVVtbc39RG0l4R0ytGsO',
        database='db-hlx8d21axvv7'
    )
    return conn

user = [0,0,0,0,1,2]

def main():
    

    while True:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE active = %s',(1,))
        data = cursor.fetchone()
        print(data[3:8])
        time.sleep(2)
        '''
        Uncomment when connected with raspberry pi
        from sensors import *

        appliances = Bulb(data[3:8])

        '''

        conn.close()

if __name__ == '__main__':
    

    main()