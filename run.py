from binance.client import Client
from config import *
from binance.enums import *
import schedule
import time
import random
import json
import logging
from decimal import *
import datetime
from telegrammodule import *

Log_Format = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename="logs.log", level=logging.INFO, format = Log_Format)
logger = logging.getLogger()
client = Client(API_KEY, API_KEY_SECRET)
currentprice = Decimal(client.get_symbol_ticker(symbol=SYMBOL)["price"])
stepsize = Decimal(Decimal(GRIDPERC)/Decimal(100)*currentprice)
step = 1
isAPIAvailable = False
stepprice = [currentprice-stepsize]
orderidlist = []
enoughBalance = False


def balanceChecker():
    try:
            currentprice = Decimal(client.get_symbol_ticker(symbol=SYMBOL)["price"])
            balance = client.get_asset_balance(asset='USDT')['free']
            buyorder = Decimal(QUANTITY)*currentprice
            print("buyorder in dollars: " + str(buyorder))
            print(str(balance))
            global enoughBalance
            if Decimal(balance) < buyorder:
                enoughBalance = False
                print("Insufficient funds to create buy orders")
            else:
                enoughBalance = True
    except: print("Oops! something went wrong!")
    logging.exception('')
    pass



while step < GRIDS:
    stepprice.append(stepprice[step-1]-stepsize)
    step += 1

round_to_tenths = [round(num, 2) for num in stepprice]



def startup():
    balanceChecker()
    orders = client.get_open_orders(symbol=SYMBOL)
    amountbuyorders = len(orders)
    if enoughBalance == True:
        if amountbuyorders == 0:
            counter = 0
            print('No buy orders open. creating orders.')
            while(len(client.get_open_orders(symbol=SYMBOL)) < GRIDS):
                r1 = random.randint(0, 100000)
                neworder = client.order_limit_buy(
                symbol=SYMBOL,
                quantity=QUANTITY,
                price=round_to_tenths[counter],
                newClientOrderId = str(r1))
                orderidlist.append(r1)
                print('ORDER LIST' + str(orderidlist))
                if(counter < len(client.get_open_orders(symbol=SYMBOL))):
                    counter += 1
        else: print("Not sufficient funds to create buy orders") 
            
            
def connectivityCheck():
    global isAPIAvailable
    print("Checking connectivity to binance API...")
    try:
        client.ping()
        isAPIAvailable = True
    except:
        print("Binance API not available")
        isAPIAvailable = False
        


    
startup()

def job():
    connectivityCheck()
    if isAPIAvailable == True:
        print("Binance API is available")





        balanceChecker()
        print("Checking if orders have been filled...")


        try:
            if len(orderidlist) != 0:
                order = client.get_order(
            symbol=SYMBOL,
            origClientOrderId =str(orderidlist[0]))
                if(order['status'] == 'FILLED'):
                    print('Order filled, calculating sell price...')
                    try:
                        neworder = client.order_limit_sell(
                        symbol=SYMBOL,
                        quantity=QUANTITY,
                        price=round(round_to_tenths[0]*Decimal(1+(GRIDPERC/100)),2))
                        logger.info('Trying to remove id from list: ' + 'ORDERIDLIST: '+str(orderidlist)+' unique ID to remove: ' + str(Decimal(order['clientOrderId']) ))
                        round_to_tenths.pop(0)
                        orderidlist.pop(0)
                    except: 
                        logging.exception('')
                        logger.info('Error, please investigate price: '+ str(round(round_to_tenths[0]*Decimal(1+(GRIDPERC/100)),2)))
        except: logger.exception('')

        
        print("Checking if bot can create new buy orders...")
        print(str(orderidlist))
        if enoughBalance == True:
            if len(orderidlist) < GRIDS:
                    r1 = random.randint(0, 100000)
                    price = round((min(round_to_tenths))-stepsize,2)
                    neworder = client.order_limit_buy(
                    symbol=SYMBOL,
                    quantity=QUANTITY,
                    price=price,
                    newClientOrderId = str(r1)
                    )
                    orderidlist.append(r1)
                    print("Appended it now, "+str(orderidlist))
                    round_to_tenths.append(price)
        else: 
            logger.info("Error with creating buy orders")
            print("Not sufficient funds to create buy orders")

        
        print('Checking if orders are still inside range')
        if 1 > 0:
            try:
                newprice = round(Decimal(client.get_symbol_ticker(symbol=SYMBOL)["price"])-stepsize,2)
                logger.info("Bughunt, newprice is " + str(newprice) + "Round_to_tenths[0] is" + str(Decimal(round_to_tenths[0])) + "1+(Decimal(GRIDPERC)/100) is " + str(1+(Decimal(GRIDPERC)/100)))
                if Decimal(newprice) > Decimal(round_to_tenths[0])*(1+(Decimal(GRIDPERC)/100)):
                    try:
                        print('Cancelling lowest order and bringing it on top')
                        client.cancel_order(
                        symbol=SYMBOL,
                        origClientOrderId=orderidlist[-1]
                        )
                        round_to_tenths.pop(-1)
                        orderidlist.pop(-1)
                        r1 = random.randint(0, 1000000)
                        neworder = client.order_limit_buy(
                        symbol=SYMBOL,
                        quantity=QUANTITY,
                        price=newprice,
                        newClientOrderId = str(r1))
                        orderidlist.insert(0,r1)
                        round_to_tenths.insert(0,newprice)
                    except:
                        print("Order doesnt exist")
                        logging.exception('')
            except:
                logging.exception('')






    




    
        

    

print('Welcome to PyGRID v0.1')
schedule.every(2).seconds.do(job)

while 1:
   schedule.run_pending()
   time.sleep(1)