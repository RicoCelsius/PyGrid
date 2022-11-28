
import mysql.connector
import config
from datetime import datetime


try:
    mydb = mysql.connector.connect(
    host=f'{config.mysql_host}',
    user=f'{config.mysql_username}',
    password=f'{config.mysql_password}',
    database=f'{config.database_name}'
    )
    cursor = mydb.cursor()
except Exception as e: 
    print(e)

def checkIfTableExist():
    sql = "SHOW TABLES LIKE 'trades'"
    cursor.execute(sql)
    result = cursor.fetchone()
    if not result: cursor.execute("CREATE TABLE trades (dateTime TIMESTAMP, side VARCHAR(255), id VARCHAR(255), price VARCHAR(255), quantity VARCHAR(255), status VARCHAR(255))")
checkIfTableExist()


def write(side,tradeId,price,quantity,status):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    sql = 'INSERT INTO trades (dateTime, side, id, price, quantity, status) VALUES (%s, %s,%s,%s,%s)'
    val = (f'{dt_string}', f'{side}',f'{tradeId}',f'{price}',f'{quantity}',f'{status}')
    cursor.execute(sql, val)


 

