import builtins
from urllib import request
from config import *
import schedule
from time import *
from random import *
import time
import random

from datetime import datetime
from telegrammodule import main,sendMessage
# from binancedata import getBalance, getQuantity,getDecimalAmounts
import threading
import math
import ccxt
import symboldata

import builtins
from urllib import request
import config
from decimal import *
import json
import requests
import math
import ccxt




exchange_class = getattr(ccxt, config.exchange)
exchange = exchange_class({
    'apiKey': config.api_key,
    'secret': config.api_key_secret,
    'enableRateLimit': True,
})

lastQuantity = []
currentQuantity = None
mayAdapt = True
ordersDict = {}
# fetch the BTC/USDT ticker for use in converting assets to price in USDT
ticker = exchange.fetch_ticker(config.symbol)

# calculate the ticker price of BTC in terms of USDT by taking the midpoint of the best bid and ask
priceUSD = Decimal((float(ticker['ask']) + float(ticker['bid'])) / 2)
print("Price = " + str(priceUSD))



def getCurrentPrice():
    priceUSD = Decimal((float(ticker['ask']) + float(ticker['bid'])) / 2)
    return priceUSD

def getBalance():
    balance = exchange.fetchBalance()['BUSD']['free']
    print(str(balance))
    return str(balance)

def getDecimalAmounts(symbol):
    #response = requests.get("https://api.binance.com/api/v3/exchangeInfo?symbol="+symbol)
    #minQty = float(response.json()["symbols"][0]["filters"][2]["minQty"])
    amountDecimals = 3
    return amountDecimals
    


def getQuantity():
    marketStructure = exchange.markets[config.symbol]
    global apr
    global mayAdapt
    global currentQuantity
    lenstr = symboldata.basePrecision
    if config.compound:
        try:
            balance = exchange.fetchBalance()['USD']['free']
            quotePrice = getCurrentPrice()
            quantityDollars = Decimal(balance)*Decimal((config.compound_wallet_perc/100))
            quoteQuantity = quantityDollars/quotePrice
            
            
            lastQuantity.insert(0,round(quoteQuantity,lenstr))
            print(f"Length lastQuantity = {len(lastQuantity)}")

            if len(lastQuantity) > 3:
                lastQuantity.pop()
            return round(quoteQuantity,lenstr) if quantityDollars > config.dollarquantity else round(Decimal(config.dollarquantity)/getCurrentPrice(),lenstr)
        except: return lastQuantity[0]
    elif config.apr_target_mode:
        #x=5*z/y, target = z, hapr = y
        x = None
        if apr == None or apr == 0:
            return round(Decimal(config.dollarquantity)/getCurrentPrice(),lenstr)
        if mayAdapt == False: return currentQuantity
        elif target_apr != float(apr) and mayAdapt:
            f = 100
            x = (f * target_apr) / apr
            inverseFactor = 1/f
            xKwadraat = x*x
            fDelenDoorxKwad = f/xKwadraat
            plus1min1 = -1 if target_apr < apr else 1
            slope = (float((fDelenDoorxKwad))+float(inverseFactor))*(plus1min1)
            configQuantity = Decimal(config.dollarquantity)/getCurrentPrice()
            
            new_quantity_delta = (Decimal(slope) * configQuantity) if currentQuantity == None else Decimal(slope) * currentQuantity
            
            new_quantity = (configQuantity + new_quantity_delta) if currentQuantity == None else currentQuantity + new_quantity_delta
            
            #sendMessage(f'x={x},slope={slope},new_quantity={new_quantity},target={target_apr},apr={apr}')
            currentPrice=getCurrentPrice()

            safetyFactor = Decimal(1.1)
        
            mayAdapt = False

            if Decimal(new_quantity)*currentPrice > symboldata.minNotional*safetyFactor:
                currentQuantity = new_quantity
                return round(abs(new_quantity),lenstr)
            else:
                minimumQuantity = (symboldata.minNotional/currentPrice)*safetyFactor
                currentQuantity = minimumQuantity
                return round(minimumQuantity,lenstr)
            

            


        
    else:
         return round(Decimal(config.dollarquantity)/getCurrentPrice(),lenstr)



exchange_class = getattr(ccxt, config.exchange)
exchange = exchange_class({
    'apiKey': api_key,
    'secret': api_key_secret,
    'enableRateLimit': True,
    }
)

# fetch the BTC/USDT ticker for use in converting assets to price in USDT
ticker = exchange.fetch_ticker(symbol)

# calculate the ticker price of BTC in terms of USDT by taking the midpoint of the best bid and ask
priceUSD = Decimal((float(ticker['ask']) + float(ticker['bid'])) / 2)
startTime = time.time()


def getCurrentPrice():
    ticker = exchange.fetch_ticker(symbol)
    priceUSD = Decimal((float(ticker['ask']) + float(ticker['bid'])) / 2)
    return round(priceUSD,symboldata.pricePrecision)


print('Welcome to PyGRID v0.2')

currentprice = priceUSD
stepsize = Decimal(Decimal(gridperc)/Decimal(100)*currentprice)
step = 1
isAPIAvailable = False
stepprice = [currentprice-stepsize]
dust = 0
startBalance = Decimal(getBalance())
yesterdayBalance = Decimal(getBalance())
totalProfitSinceStartup = 0
apr = None

state = True
enoughBalance = True







def truncate(number) -> Decimal:
    stepper = Decimal(10.0) ** Decimal(getDecimalAmounts(symbol))
    return Decimal(math.trunc(Decimal(stepper) * Decimal(number)) / Decimal(stepper))

def createOrder(type,quantity,price):
    currentprice = round(getCurrentPrice(),symboldata.pricePrecision)
    if type == "buy":
        neworder = exchange.createOrder(symbol,"limit","buy",quantity,price)
        response = neworder['id']

        ordersDict[f'{response}'] = {
            'side':'buy',
            'quantity':f'{quantity}',
            'price':{f'price'},
            'status':'open'
            }

    if type == "sell":
        neworder = exchange.createOrder(symbol,"limit","sell",quantity,price)
        response = neworder['id']
        ordersDict.pop(f'{response}')
    sendMessage(f"Created {'BUY' if type=='buy' else 'SELL'} order at {price} \nQuantity is {quantity}\nCurrent balance is {getBalance()}\nCurrent price is {currentprice}")



# def saveOrder(orderid,price,quantity=0):
#     buyOrders[orderid] = price
#     #buyOrderQuantity[orderid] = quantity

def calculateProfit(cost):
    sellTotal = cost
    buyTotal = Decimal(cost) / Decimal((1+(gridperc/100)))

    totalprofit = sellTotal - buyTotal
    global totalProfitSinceStartup
    totalProfitSinceStartup += totalprofit
    return round(totalprofit,3)

def getSellPriceHighestBuyOrder():
    if ordersDict:
        maxValue = None
        for x in ordersDict.values():
            print(max(ordersDict[x]['price']))
            maxValue = max(x)
        sellPrice = Decimal(truncate(maxValue * Decimal(((gridperc/100)+1))))
        return round(sellPrice,3)


def checkSellOrder():
    global apr
    global mayAdapt
    if len(sellOrders) > 0:
        try:
            order = exchange.fetchOrder(sellOrders[0], symbol = symbol, params = {})
            if order['status'] == 'closed':
                endTime = time.time()
                timeElapsed = endTime - startTime
                timeElapsedInHours = timeElapsed / 3600
                profitPerHour = Decimal(totalProfitSinceStartup) / Decimal(timeElapsedInHours)
                apr = round(((profitPerHour*8760/startBalance)*100),2)
                sendMessage(f"Sell order filled\nYour profit in this trade: {calculateProfit(Decimal(order['cost']))}\nYour total profit since bot start-up: {totalProfitSinceStartup}\nRuntime: {round(timeElapsedInHours,2)} hours\nProfit per hour: {round(profitPerHour,2)}\nAPR: {apr}\nTarget APR: {config.target_apr}")
                sellOrders.pop(0)
                mayAdapt = True
        except Exception as e: print(e)





while step < grids:
    stepprice.append(stepprice[step-1]-stepsize)
    step += 1

round_to_tenths = [truncate(num) for num in stepprice]



def startup():
    #balanceChecker()
    if enoughBalance :
            counter = 0
            print(f'Creating buy orders...')
            #autoBuyBNB()
            while(counter < grids):
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
#     if(AUTO_BUY_BNB ):
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
    if isAPIAvailable  and state :
        checkSellOrder()
        print(f"{dt_string} Checking if orders have been filled...")         
        try:
            if len(buyOrders) != 0:
                idnumber = str(max(buyOrders,key=buyOrders.get))
                order = exchange.fetchOrder(idnumber, symbol = symbol, params = {})
                if(order['status'] == 'closed'):
                    print(f"{dt_string} Order filled, calculating sell price...")
                    try:
                        marketStructure = exchange.markets[symbol]
                        lenstr = symboldata.basePrecision
                        createOrder("sell",round(Decimal(order['filled']),lenstr),getSellPriceHighestBuyOrder())
                        #setDust()
                    except Exception as e: 
                        print("Error occured at codeblock creating sell order (1)")
                        print(e)
        except Exception as e: 
            print("Error  occured at codeblock creating sell order (2)")
            print(e)


        
        print("Checking if bot can create new buy orders...")
        if enoughBalance :
            if len(buyOrders) < grids and len(buyOrders) != 0:
                    print(f"Can create new buy order(s)")
                    try:
                        createOrder("buy",getQuantity(),truncate(Decimal(min(buyOrders.values()))-stepsize))                
                    except Exception as e: 
                        print(e) 
                        #print(e)
        else: 
            print(f"Not sufficient funds to create buy orders")

        
        print(f'Checking if orders are still inside range')
        try:
            currentSetPrice = truncate(getCurrentPrice()-stepsize)
            maxBuyOrder = Decimal(max(buyOrders.values()))
            threshold = (maxBuyOrder)*(1+(Decimal(gridperc)/100))
            if (Decimal(currentSetPrice) > Decimal(max(buyOrders.values()))*(1+(Decimal(gridperc)/100))) and (order['status'] == 'open'):
                try:
                    print(f"{dt_string} Cancelling lowest order and bringing it on top")
                    sendMessage('Cancelling lowest order and bringing it on top')
                    orderToPop = min(buyOrders, key=buyOrders.get)
                    print(str(orderToPop))
                    exchange.cancel_order (str(orderToPop),symbol=symbol)
                    try:
                        order = exchange.fetchOrder(orderToPop, symbol = symbol, params = {})
                        filledQuantity = order['filled']
                        if filledQuantity > 0:
                            if exchange.has['createMarketOrder']:
                                exchange.createOrder(symbol,'market','sell',filledQuantity,{})
                    except Exception as e:
                            sendMessage(str(e))
                            buyOrders.pop(orderToPop)
                    
                    buyOrders.pop(orderToPop)
            
                #adding buy order
                    global currentQuantity
                    createOrder("buy",getQuantity(),Decimal(max(buyOrders.values()))*(1+(Decimal(gridperc)/100)))
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




