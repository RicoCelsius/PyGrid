import builtins
from urllib import request
from config import *
import schedule
from time import *
from random import *
import time
import random
from decimal import *
from datetime import datetime
from telegrammodule import main,sendmessage
from binancedata import getBalance, getQuantity,getDecimalAmounts
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

# fetch the BTC/USDT ticker for use in converting assets to price in USDT
ticker = exchange.fetch_ticker(SYMBOL)

# calculate the ticker price of BTC in terms of USDT by taking the midpoint of the best bid and ask
priceUSDT = Decimal((float(ticker['ask']) + float(ticker['bid'])) / 2)
print("LUNA Price = " + str(priceUSDT))


def getCurrentPrice():
    tickerr = exchange.fetch_ticker(SYMBOL)
    priceUSDT = Decimal((float(tickerr['ask']) + float(tickerr['bid'])) / 2)
    return priceUSDT


print('Welcome to PyGRID v0.2')

currentprice = priceUSDT
stepsize = Decimal(Decimal(GRIDPERC)/Decimal(100)*currentprice)
step = 1
isAPIAvailable = False
stepprice = [currentprice-stepsize]
dust = 0
yesterdayBalance = Decimal(getBalance())


enoughBalance = True

buyOrders = {}
buyOrderQuantity = {}




def truncate(number) -> Decimal:
    stepper = Decimal(10.0) ** Decimal(getDecimalAmounts(SYMBOL))
    return Decimal(math.trunc(Decimal(stepper) * Decimal(number)) / Decimal(stepper))

def createOrder(type,quantity,price):
    currentprice = getCurrentPrice()
    if type == "buy":
        neworder = exchange.createOrder(SYMBOL,"limit","buy",quantity,price,{})
        response = neworder['id']
        saveOrder(response,price,quantity)
    if type == "sell":
        neworder = exchange.createOrder(SYMBOL,"limit","sell",quantity,price,{})
        buyOrders.pop(max(buyOrders, key=buyOrders.get))
    sendmessage(f"Created {'BUY' if type=='buy' else 'SELL'} order at {price} \n Quantity is {quantity}\n Current balance is {getBalance()}\n Current price is {currentprice}")

#

def testOrder():
    print("Test order \n ")

def saveOrder(orderid,price,quantity=0):
    buyOrders[orderid] = price
    buyOrderQuantity[orderid] = quantity


#get order quantity, only for sell orders
def getOrderQuantity(orderid):
    if buyOrderQuantity:
        return (buyOrderQuantity[orderid])


def getSellPriceHighestBuyOrder():
    if buyOrders:
        highestValue = max(buyOrders.values())
        print(highestValue)
        sellPrice = Decimal(truncate(highestValue * Decimal(((GRIDPERC/100)+1))))
        print(sellPrice)
        return sellPrice





def balanceChecker():
    try:
            currentprice = getCurrentPrice()
            balance = getBalance()
            buyorder = Decimal(getQuantity())*currentprice
            print("Buyorder in dollars: " + str(buyorder))
            print(str(balance))
            print(currentprice)
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
    #balanceChecker()
    if enoughBalance == True:
            counter = 0
            print('Creating buy orders...')
            #autoBuyBNB()
            while(counter < GRIDS):
                createOrder("buy",getQuantity(),round_to_tenths[counter])
                counter += 1

            
            
def connectivityCheck():
    global isAPIAvailable
    print("Checking connectivity to the API...")
    try:
        status = exchange.fetchStatus(params = {})
        if status['status'] == 'ok':
            isAPIAvailable = True
        else: isAPIAvailable = False
    except Exception as e:
        print("Error occured with pinging the API server")
        print(e)
        isAPIAvailable = False
        
# def autoBuyBNB():
#     if(AUTO_BUY_BNB == True):
#         sleep(randint(1,5))
#         try:
#             balance = client.get_asset_balance(asset='BNB')['free']
#             if Decimal(balance) <= 0.05:
#                 print("Not enough BNB in wallet, bot will market buy 0.1 BNB")
#                 order = client.order_market_buy(
#                 symbol='BNBUSDT',
#                 quantity=0.1)
#         except Exception as e:
#             print(e)

# def setDust():
#     global dust
#     dust = Decimal(truncate(client.get_asset_balance(asset='LUNA')['free']))
    
startup()

def job():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    connectivityCheck()
    if isAPIAvailable == True:
        balanceChecker()
        print(dt_string + " Checking if orders have been filled...")         
        try:
            if len(buyOrders) != 0:
                idnumber = str(max(buyOrders,key=buyOrders.get))
                order = exchange.fetchOrder(idnumber, symbol = SYMBOL, params = {})
                if(order['status'] == 'closed'):
                    print(dt_string +' Order filled, calculating sell price...')
                    try:
                        origQty = Decimal(order['filled'])
                        if PAY_FEE_BNB == False:
                            fee = Decimal((TRADING_FEE/100))*origQty
                        else: fee = 0
                        quantityy = origQty - fee
                        if dust < quantityy:
                            createOrder("sell",(quantityy+dust),getSellPriceHighestBuyOrder())
                        else:
                            createOrder("sell",(quantityy),getSellPriceHighestBuyOrder())
                        #setDust()
                    except Exception as e: 
                        print("Error occured at codeblock creating sell order (1)")
                        print(e)
        except Exception as e: 
            print("Error  occured at codeblock creating sell order (2)")
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
                currentSetPrice = truncate(getCurrentPrice()-stepsize)
                maxBuyOrder = Decimal(max(buyOrders.values()))
                threshold = (maxBuyOrder)*(1+(Decimal(2*GRIDPERC)/100))
                print("Max buy order = "+ str(maxBuyOrder) + " Threshold = "+ str(threshold) + "Currset price =" + str(currentSetPrice))
                if Decimal(currentSetPrice) > Decimal(max(buyOrders.values()))*(1+(Decimal(GRIDPERC)/100)):
                    try:
                        print(dt_string + 'Cancelling lowest order and bringing it on top')
                        orderToPop = min(buyOrders, key=buyOrders.get)
                        print(str(orderToPop))
                        exchange.cancel_order (str(orderToPop))
                        try:
                            order = exchange.fetchOrder(orderToPop, symbol = SYMBOL, params = {})
                            filledQuantity = order['filled']
                            if filledQuantity > 0:
                                if exchange.has['createMarketOrder']:
                                    exchange.createOrder(SYMBOL,'market','sell',filledQuantity,{})
                        except Exception as e: sendmessage(str(e))
                        buyOrders.pop(orderToPop)
                        buyOrderQuantity.pop(orderToPop)
                    #adding buy order
                        createOrder("buy",getQuantity(),currentSetPrice)
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)

def dailyUpdate():
    currentBalance = Decimal(getBalance())
    global yesterdayBalance
    sendmessage(f"Your daily update \n Current balance: {currentBalance} \n Balance yesterday: {str(yesterdayBalance)} \n Difference: {str(currentBalance-yesterdayBalance)}")
    yesterdayBalance = Decimal(currentBalance)

def startjob():
    schedule.every(2).seconds.do(job)
    schedule.every(1).day.do(dailyUpdate())
    #if AUTO_BUY_BNB: schedule.every(100).seconds.do(autoBuyBNB)





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




