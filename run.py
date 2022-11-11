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
from telegrammodule import main,sendMessage
from binancedata import getBalance, getQuantity,getDecimalAmounts
import threading
import math
import ccxt



subaccount = SUB_ACCOUNT
exchange_id = EXCHANGE
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'apiKey': API_KEY,
    'secret': API_KEY_SECRET,
    'enableRateLimit': True,

    
    }
)

# fetch the BTC/USDT ticker for use in converting assets to price in USDT
ticker = exchange.fetch_ticker(SYMBOL)

# calculate the ticker price of BTC in terms of USDT by taking the midpoint of the best bid and ask
priceUSDT = Decimal((float(ticker['ask']) + float(ticker['bid'])) / 2)
startTime = time.time()


def getCurrentPrice():
    tickerr = exchange.fetch_ticker(SYMBOL)
    priceUSDT = Decimal((float(tickerr['ask']) + float(tickerr['bid'])) / 2)
    return round(priceUSDT,2)


print('Welcome to PyGRID v0.2')

currentprice = priceUSDT
stepsize = Decimal(Decimal(GRIDPERC)/Decimal(100)*currentprice)
step = 1
isAPIAvailable = False
stepprice = [currentprice-stepsize]
dust = 0
startBalance = Decimal(getBalance())
yesterdayBalance = Decimal(getBalance())
totalProfitSinceStartup = 0

state = True
enoughBalance = True

buyOrders = {}
buyOrderQuantity = {}
sellOrders = []




def truncate(number) -> Decimal:
    stepper = Decimal(10.0) ** Decimal(getDecimalAmounts(SYMBOL))
    return Decimal(math.trunc(Decimal(stepper) * Decimal(number)) / Decimal(stepper))

def createOrder(type,quantity,price):
    currentprice = round(getCurrentPrice(),2)
    if type == "buy":
        neworder = exchange.createOrder(SYMBOL,"limit","buy",quantity,price)
        response = neworder['id']
        saveOrder(response,price,quantity)
    if type == "sell":
        neworder = exchange.createOrder(SYMBOL,"limit","sell",quantity,price)
        response = neworder['id']
        sellOrders.insert(0,response)
        buyOrders.pop(max(buyOrders, key=buyOrders.get))
    sendMessage(f"Created {'BUY' if type=='buy' else 'SELL'} order at {price} \nQuantity is {quantity}\nCurrent balance is {getBalance()}\nCurrent price is {currentprice}")



def saveOrder(orderid,price,quantity=0):
    buyOrders[orderid] = price
    #buyOrderQuantity[orderid] = quantity

def calculateProfit(cost):
    sellTotal = cost
    buyTotal = Decimal(cost) / Decimal((1+(GRIDPERC/100)))

    totalprofit = sellTotal - buyTotal
    global totalProfitSinceStartup
    totalProfitSinceStartup += totalprofit
    return round(totalprofit,2)

def getSellPriceHighestBuyOrder():
    if buyOrders:
        highestValue = max(buyOrders.values())
        sellPrice = Decimal(truncate(highestValue * Decimal(((GRIDPERC/100)+1))))
        return round(sellPrice,2)


def checkSellOrder():
    if len(sellOrders) > 0:
        try:
            order = exchange.fetchOrder(sellOrders[0], symbol = SYMBOL, params = {})
            if order['status'] == 'closed':
                endTime = time.time()
                timeElapsed = endTime - startTime
                timeElapsedInHours = timeElapsed / 3600
                profitPerHour = Decimal(totalProfitSinceStartup) / Decimal(timeElapsedInHours)
                apr = round(((profitPerHour*8760/startBalance)*100),2)
                sendMessage(f"Sell order filled\nYour profit in this trade: {calculateProfit(Decimal(order['cost']))}\nYour total profit since bot start-up: {totalProfitSinceStartup}\nRuntime: {round(timeElapsed,2)} seconds\nProfit per hour: {round(profitPerHour,2)}\nAPR: {apr}")
                sellOrders.pop(0)
        except Exception as e: print(e)




def balanceChecker():
    try:
            currentprice = getCurrentPrice()
            balance = getBalance()
            buyorder = Decimal(getQuantity())*currentprice
            global enoughBalance
            if Decimal(balance) < buyorder:
                enoughBalance = False
                print(f"Insufficient funds to create buy orders")
                sendMessage(f"Insufficient funds to create buy orders")
            else:
                enoughBalance = True
    except Exception as e: 
        print(e) 




while step < GRIDS:
    stepprice.append(stepprice[step-1]-stepsize)
    step += 1

round_to_tenths = [truncate(num) for num in stepprice]



def startup():
    #balanceChecker()
    if enoughBalance == True:
            counter = 0
            print(f'Creating buy orders...')
            #autoBuyBNB()
            while(counter < GRIDS):
                createOrder("buy",getQuantity(),round_to_tenths[counter])
                counter += 1

            
            
def connectivityCheck():
    global isAPIAvailable
    print(f"Checking connectivity to the API...")
    try:
        status = exchange.fetchStatus(params = {})
        if status['status'] == 'ok':
            isAPIAvailable = True
        else: isAPIAvailable = False
    except Exception as e:
        print(f"Error occured with pinging the API server")
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
    try: printLengths()
    except: pass


    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    connectivityCheck()
    if isAPIAvailable == True and state == True:
        balanceChecker()
        checkSellOrder()
        print(f"{dt_string} Checking if orders have been filled...")         
        try:
            if len(buyOrders) != 0:
                idnumber = str(max(buyOrders,key=buyOrders.get))
                order = exchange.fetchOrder(idnumber, symbol = SYMBOL, params = {})
                if(order['status'] == 'closed'):
                    print(f"{dt_string} Order filled, calculating sell price...")
                    try:
                        marketStructure = exchange.markets[SYMBOL]
                        lenstr = 3
                        createOrder("sell",round(Decimal(order['filled']),lenstr),getSellPriceHighestBuyOrder())
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
                    print(f"Can create new buy order(s)")
                    try:
                        createOrder("buy",getQuantity(),truncate(Decimal(min(buyOrders.values()))-stepsize))                
                    except Exception as e: 
                        print(e) 
                        #print(e)
        else: 
            print(f"Not sufficient funds to create buy orders")

        
        print(f'Checking if orders are still inside range')
        if 1 > 0:
            try:
                currentSetPrice = truncate(getCurrentPrice()-stepsize)
                maxBuyOrder = Decimal(max(buyOrders.values()))
                threshold = (maxBuyOrder)*(1+(Decimal(GRIDPERC)/100))
                if (Decimal(currentSetPrice) > Decimal(max(buyOrders.values()))*(1+(Decimal(GRIDPERC)/100))) and (order['status'] == 'open'):
                    try:
                        print(f"{dt_string} Cancelling lowest order and bringing it on top")
                        sendMessage('Cancelling lowest order and bringing it on top')
                        orderToPop = min(buyOrders, key=buyOrders.get)
                        print(str(orderToPop))
                        exchange.cancel_order (str(orderToPop),symbol=SYMBOL)
                        try:
                            order = exchange.fetchOrder(orderToPop, symbol = SYMBOL, params = {})
                            filledQuantity = order['filled']
                            if filledQuantity > 0:
                                if exchange.has['createMarketOrder']:
                                    exchange.createOrder(SYMBOL,'market','sell',filledQuantity,{})
                        except Exception as e:
                                sendMessage(str(e))
                                buyOrders.pop(orderToPop)
                        
                        buyOrders.pop(orderToPop)
                
                    #adding buy order
                        createOrder("buy",getQuantity(),Decimal(max(buyOrders.values()))*(1+(Decimal(GRIDPERC)/100)))
                    except ccxt.ExchangeError as e:
                        
                        buyOrders.pop(orderToPop)
                        
                    except Exception as e:
                        pass
                    
            except Exception as e:
                print(e)

def dailyUpdate():
    currentBalance = Decimal(getBalance())
    global yesterdayBalance
    sendMessage(f"Your daily update \n Current balance: {currentBalance} \n Balance yesterday: {str(yesterdayBalance)} \n Difference: {str(currentBalance-yesterdayBalance)}")
    yesterdayBalance = Decimal(currentBalance)

def startjob():
    schedule.every(1).seconds.do(job)
    schedule.every(1).day.do(dailyUpdate)


def printLengths():
    print(f"Length buyOrders is {len(buyOrders)} Length buyOrderQuantity is {len(buyOrderQuantity)}, sellorders is {len(sellOrders)} stepprice is {len(stepprice)}  ")
    



try:
    t2 = threading.Thread(target=startjob())
    t2.start()
    t1 = threading.Thread(target=main())
    t1.start()
except Exception as e:
    print(f"Something went wrong with threading")
    print(e)

while 1:
    schedule.run_pending()
    time.sleep(0.1)




