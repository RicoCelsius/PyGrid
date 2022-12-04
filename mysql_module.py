
import mysql.connector
import config
from datetime import datetime
import time
mydb=None
cursor=None
isConnected=False

print(config.mysql_database)
print(config.mysql_host)
table=f'trades2'

try:
    mydb = mysql.connector.connect(
    host=f'{config.mysql_host}',
    user=f'{config.mysql_username}',
    password=f'{config.mysql_password}',
    database=f'{config.mysql_database}',
    auth_plugin='mysql_native_password'
    )
    isConnected=True
    cursor = mydb.cursor()
   
except Exception as e: 
    print(e)




def checkIfTableExist():
    sql = f"SHOW TABLES LIKE '{table}'"
    cursor.execute(sql)
    result = cursor.fetchone()
    if not result: cursor.execute(f"CREATE TABLE {table} (dateTime TIMESTAMP, side VARCHAR(255), id VARCHAR(255), price VARCHAR(255), quantity VARCHAR(255), status VARCHAR(255), cancelled VARCHAR(255))")
if isConnected: checkIfTableExist()


def write(side,tradeId,price,quantity,status,cancelled):
    now = datetime.now()
    dt_string = time.strftime('%Y-%m-%d %H:%M:%S')

    sql = f'INSERT INTO {table} (dateTime, side, id, price, quantity, status, cancelled) VALUES (%s,%s, %s,%s,%s,%s,%s)'
    val = (f'{dt_string}', f'{side}',f'{tradeId}',f'{price}',f'{quantity}',f'{status}',f'{cancelled}')
    cursor.execute(sql, val)
    mydb.commit()



def getHighestPriceInDB():
    myList = []
    try:
        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT * FROM {table} WHERE status='open' AND side='sell' AND cancelled='True' ORDER BY price DESC")
        myresult = mycursor.fetchall()
        myList = list(myresult)
        if len(myList) > 0:
            print(myList[0])
            highestPrice = myList[0][3]
            orderId = myList[0][2]
            print(orderId)
            print(highestPrice)
            return myList
        else: return myList
    except IndexError: 
        print('No cancelled sell orders in db')
        myList = []
        return myList
    

def deleteRow(orderId):
    mycursor = mydb.cursor()
    val = (f"{orderId}",)
    sql = f"DELETE FROM {table} WHERE id = %s"
    mycursor.execute(sql,val)
    mydb.commit()





getHighestPriceInDB()
 

