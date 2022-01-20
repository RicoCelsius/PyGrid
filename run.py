import builtins
from urllib import request
from binance.client import Client
from config import *
from binance.enums import *
import schedule
from time import *
from random import *
import time
import random
from decimal import *
from datetime import datetime
from telegrammodule import main,sendmessage
from binancedata import getQuantity,getDecimalAmounts
import threading
import math
import ccxt
import json
import requests

exchange_id = EXCHANGE
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'apiKey': API_KEY,
    'secret': API_KEY_SECRET,
    'enableRateLimit': True,
})


print('Welcome to PyGRID v0.2')
client = Client(API_KEY, API_KEY_SECRET)
currentprice = Decimal(client.get_symbol_ticker(symbol=SYMBOL)["price"])
stepsize = Decimal(Decimal(GRIDPERC)/Decimal(100)*currentprice)
step = 1
isAPIAvailable = False
stepprice = [currentprice-stepsize]


enoughBalance = False

buyOrders = {}
buyOrderQuantity = {}

def truncate(number) -> Decimal:
    stepper = Decimal(10.0) ** Decimal(getDecimalAmounts(SYMBOL))
    return Decimal(math.trunc(Decimal(stepper) * Decimal(number)) / Decimal(stepper))

def createOrder(type,quantity,price): 
   
    if type == "buy":
        neworder = exchange.createOrder(SYMBOL,"limit","buy",quantity,price,{})
        response = neworder['info']['orderId']
        saveOrder(response,price,quantity)
        sendmessage(f"Created BUY order at {price}, quantity is {quantity}")
    if type == "sell":
        neworder = exchange.createOrder(SYMBOL,"limit","sell",quantity,price,{})
        sendmessage(f"Buy order filled, creating sell order at {price}, quantity is {quantity}")
        buyOrders.pop(max(buyOrders, key=buyOrders.get))

#

def saveOrder(orderid,price,quantity=0):
    buyOrders[orderid] = price
    buyOrderQuantity[orderid] = quantity


#get order quantity, only for sell orders
def getOrderQuantity(orderid):
    if buyOrderQuantity:
     return buyOrderQuantity[orderid]


def getSellPriceHighestBuyOrder():
    if buyOrders:
        highestValue = max(buyOrders.values())
        print(highestValue)
        sellPrice = Decimal(truncate(highestValue * Decimal(((GRIDPERC/100)+1))))
        print(sellPrice)
        return sellPrice





def balanceChecker():
    try:
            currentprice = Decimal(client.get_symbol_ticker(symbol=SYMBOL)["price"])
            balance = client.get_asset_balance(asset='USDT')['free']
            buyorder = Decimal(getQuantity())*currentprice
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

round_to_tenths = [truncate(num) for num in stepprice]



def startup():
    balanceChecker()
    if enoughBalance == True:
            counter = 0
            print('Creating buy orders...')
            autoBuyBNB()
            while(counter < GRIDS):
                createOrder("buy",getQuantity(),round_to_tenths[counter])
                counter += 1

            
            
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
        try:
            balance = client.get_asset_balance(asset='BNB')['free']
            if Decimal(balance) <= 0.05:
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
                idnumber = str(max(buyOrders,key=buyOrders.get))
                order = client.get_order(
                symbol=SYMBOL,
                orderId = idnumber)
                if(order['status'] == 'FILLED'):
                    print(dt_string +' Order filled, calculating sell price...')
                    try:
                        createOrder("sell",getOrderQuantity(idnumber),getSellPriceHighestBuyOrder())
                    except Exception as e: 
                        print("Error occured at codeblock creating sell order (1)")
                        print(e)
        except Exception as e: 
            print("Error occured at codeblock creating sell order (2)")
            print(e)


        
        print("Checking if bot can create new buy orders...")
        if enoughBalance == True:
            if len(buyOrders) < GRIDS and len(buyOrders) != 0:
                    print("Can create new buy order(s)")
                    variableQuantity = getQuantity()
                    try:
                        createOrder("buy",getQuantity(),truncate(Decimal(min(buyOrders.values()))-stepsize))                
                    except Exception as e: print(e) 
        else: 
            print("Not sufficient funds to create buy orders")

        
        print('Checking if orders are still inside range')
        if 1 > 0:
            try:
                currentSetPrice = truncate(Decimal(client.get_symbol_ticker(symbol=SYMBOL)["price"])-stepsize)
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
                        orderId=orderToPop)
                        buyOrders.pop(orderToPop)
                        buyOrderQuantity.pop(orderToPop)
                    #adding buy order
                        createOrder("buy",getQuantity(),currentSetPrice) #not tested
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)

def startjob():
    schedule.every(2).seconds.do(job)
    if AUTO_BUY_BNB: schedule.every(100).seconds.do(autoBuyBNB)





try:
    t2 = threading.Thread(target=startjob())
    t2.start()
    t1 = threading.Thread(target=main())
    t1.start()
except Exception as e:
    print("Something went wrong with threading")
    print(e)

while 1:
    schedule.run_pending()
    time.sleep(1)




