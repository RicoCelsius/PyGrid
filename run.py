import builtins
from binance.client import Client
from config import *
from binance.enums import *
import schedule
from time import *
from random import *
import time
import random
import json
import logging
from decimal import *
from datetime import datetime
# from telegrammodule import *


print('Welcome to PyGRID v0.2')
client = Client(API_KEY, API_KEY_SECRET)
currentprice = Decimal(client.get_symbol_ticker(symbol=SYMBOL)["price"])
stepsize = Decimal(Decimal(GRIDPERC)/Decimal(100)*currentprice)
step = 1
isAPIAvailable = False
stepprice = [currentprice-stepsize]

enoughBalance = False

buyOrders = {}

def saveOrder(orderid, price):
    buyOrders[orderid] = price



def getSellPriceHighestBuyOrder():
    if buyOrders:
        highestValue = max(buyOrders.values())
        print(highestValue)
        sellPrice = Decimal(round(highestValue * Decimal(((GRIDPERC/100)+1)),2))
        print(sellPrice)
        return sellPrice



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
    except Exception as e: print(e)



while step < GRIDS:
    stepprice.append(stepprice[step-1]-stepsize)
    step += 1

round_to_tenths = [round(num, 2) for num in stepprice]



def startup():
    balanceChecker()
    if enoughBalance == True:
            counter = 0
            print('Creating buy orders...')
            autoBuyBNB()
            while(counter < GRIDS):
                print(str(round_to_tenths[counter]))
                r1 = random.randint(0, 1000000)
                neworder = client.order_limit_buy(
                symbol=SYMBOL,
                quantity=QUANTITY,
                price=round_to_tenths[counter],
                newClientOrderId = str(r1))
                saveOrder(str(r1),round_to_tenths[counter])
                print(str(buyOrders))
                counter = counter + 1

            
            
def connectivityCheck():
    global isAPIAvailable
    print("Checking connectivity to binance API...")
    try:
        client.ping()
        isAPIAvailable = True
    except:
        print("Binance API not available")
        isAPIAvailable = False
        
def autoBuyBNB():
    if(AUTO_BUY_BNB == True):
        sleep(randint(1,5))
        balance = client.get_asset_balance(asset='BNB')['free']
        if Decimal(balance) <= 0.1:
            try:
                print("Not enough BNB in wallet, bot will market buy 0.1 BNB")
                order = client.order_market_buy(
                symbol='BNBUSDT',
                quantity=0.1)
            except Exception as e:
                print(e)

        
    
startup()

def job():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    connectivityCheck()
    if isAPIAvailable == True:
        print(dt_string + " Binance API is available")
        balanceChecker()
        print(dt_string + " Checking if orders have been filled...")

        try:
            if len(buyOrders) != 0:
                order = client.get_order(
            symbol=SYMBOL,
            origClientOrderId =str(max(buyOrders,key=buyOrders.get)))
                if(order['status'] == 'FILLED'):
                    print(dt_string +' Order filled, calculating sell price...')
                    sellPrice = getSellPriceHighestBuyOrder()
                    try:
                        neworder = client.order_limit_sell(
                        symbol=SYMBOL,
                        quantity=QUANTITY,
                        price=sellPrice)
                        print(dt_string + " SELL ORDER PLACED AT PRICE " + str(sellPrice) + " BUY ORDER was at " + str(list(buyOrders.values())[0]))
                        buyOrders.pop(max(buyOrders, key=buyOrders.get))
                    except Exception as e: 
                        print("Error occured at codeblock creating sell order (1)")
                        print(e)
        except Exception as e: 
            print("Error occured at codeblock creating sell order (2)")
            print(e)


        
        print("Checking if bot can create new buy orders...")
        print("Len buyorders = "+str(len(buyOrders)) +" GRIDS = "+str(GRIDS))
        if enoughBalance == True:
            if len(buyOrders) < GRIDS:
                    r1 = random.randint(0, 1000000)
                    price = round(Decimal(min(buyOrders.values()))-stepsize,2)
                    print("Can create new buy order(s)"+ "price= "+ str(price)+ "orderid=" + str(r1))
                    try:
                        neworder = client.order_limit_buy(
                        symbol=SYMBOL,
                        quantity=QUANTITY,
                        price=price,
                        newClientOrderId = str(r1)
                        )
                        saveOrder(str(r1), price)  
                        print("Saved order to dict")                 
                    except Exception as e: print(e) 
        else: 
            print("Not sufficient funds to create buy orders")

        
        print('Checking if orders are still inside range')
        if 1 > 0:
            try:
                currentSetPrice = round(Decimal(client.get_symbol_ticker(symbol=SYMBOL)["price"])-stepsize,2)
                maxBuyOrder = Decimal(max(buyOrders.values()))
                threshold = (maxBuyOrder)*(1+(Decimal(2*GRIDPERC)/100))
                print("Max buy order = "+ str(maxBuyOrder) + " Threshold = "+ str(threshold) + "Curr price =" + str(currentprice))
                if Decimal(currentSetPrice) > Decimal(max(buyOrders.values()))*(1+(Decimal(GRIDPERC)/100)):
                    try:
                        print(dt_string + 'Cancelling lowest order and bringing it on top')
                        orderToPop = min(buyOrders, key=buyOrders.get)
                        print(str(orderToPop))
                        client.cancel_order(
                        symbol=SYMBOL,
                        origClientOrderId=orderToPop)
                        buyOrders.pop(orderToPop)
                        print("Adding buy order bug1")
                    #adding buy order
                        r1 = random.randint(0, 1000000)
                        neworder = client.order_limit_buy(
                        symbol=SYMBOL,
                        quantity=QUANTITY,
                        price=currentSetPrice,
                        newClientOrderId = str(r1))
                        saveOrder(str(r1),currentSetPrice)
                        print("Adding buy order bug2")
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)


schedule.every(2).seconds.do(job)
if AUTO_BUY_BNB: schedule.every(10).seconds.do(autoBuyBNB)


while 1:
   schedule.run_pending()
   time.sleep(1)