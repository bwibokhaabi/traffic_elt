from mysql.connector import (connection)

#establishing the connectioncd ..
conn = connection.MySQLConnection(user='root',
                                  password='', 
                                  host='127.0.0.1'
                                )
cursor = conn.cursor()

cursor.execute("DROP database IF EXISTS DatabaseName")


sql = "CREATE database DatabaseName";


cursor.execute(sql)


print("List of databases: ")
cursor.execute("SHOW DATABASES")
print(cursor.fetchall())

#Closing the connection
conn.close()