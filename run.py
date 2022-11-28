from urllib import request
from config import *
import schedule
from time import *
from random import *
import time
from datetime import datetime
from telegrammodule import main,sendMessage
import threading
import math
import ccxt
import symboldata
from collections import OrderedDict
from operator import getitem
from urllib import request
import config
from decimal import *
import math
import ccxt
if config.mysql_enabled: import mysql



exchange_class = getattr(ccxt, config.exchange)
exchange = exchange_class({
    'apiKey': config.api_key,
    'secret': config.api_key_secret,
    'enableRateLimit': True,
})

lastQuantity = []
currentQuantity = None
mayAdapt = True
max_bought_before_cooldown = config.max_bought_before_cooldown
ordersDict = {}
# fetch the BTC/USDT ticker for use in converting assets to price in USDT
ticker = exchange.fetch_ticker(config.symbol)

# calculate the ticker price of BTC in terms of USDT by taking the midpoint of the best bid and ask
priceUSD = Decimal((float(ticker['ask']) + float(ticker['bid'])) / 2)




def getCurrentPrice():
    priceUSD = Decimal((float(ticker['ask']) + float(ticker['bid'])) / 2)
    return priceUSD

def getBalance():
    balance = exchange.fetchBalance()['BUSD']['free']
    return str(balance)


    


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
        elif config.target_apr != float(apr) and mayAdapt:
            f = 100
            x = (f * config.target_apr) / apr
            inverseFactor = 1/f
            xKwadraat = x*x
            fDelenDoorxKwad = f/xKwadraat
            plus1min1 = -1 if config.target_apr < apr else 1
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
enoughBalance = True







def truncate(number) -> Decimal:
    stepper = Decimal(10.0) ** Decimal(symboldata.pricePrecision)
    return Decimal(math.trunc(Decimal(stepper) * Decimal(number)) / Decimal(stepper))

def createOrder(type,quantity,price):
    params = {"post_only": True} if config.post_order_only else {}
    currentprice = round(getCurrentPrice(),symboldata.pricePrecision)
    if type == "buy":
        neworder = exchange.createOrder(symbol,"limit","buy",quantity,price,params)
    else:
        print(f'Quantity is {quantity}')
        print(f'Orders dict: {ordersDict}')
        neworder = exchange.createOrder(symbol,"limit","sell",quantity,price,params)
        buyOrderToPop = sortDict(getSpecificDict('buy'),'price',True,'key')
        ordersDict.pop(buyOrderToPop[0])

    response = neworder['id']
    ordersDict[response] = {
    'side':type,
    'quantity':quantity,
    'price':price,
    'status':'open'
    }

    if config.mysql_enabled: mysql.write(type,response,price,quantity,'open')
    sendMessage(f"Created {'BUY' if type=='buy' else 'SELL'} order at {price} \nQuantity is {quantity}\nCurrent balance is {getBalance()}\nCurrent price is {currentprice}")



def calculateProfit(cost):
    global totalProfitSinceStartup
    buyTotal = Decimal(cost) / Decimal((1+(gridperc/100)))

    totalprofit = cost - buyTotal
    totalProfitSinceStartup += totalprofit
    return round(totalprofit,3)

def getSellPriceHighestBuyOrder():
    filteredDict = {}
    if ordersDict:
        for (key, value) in ordersDict.items():
        # Check if key is even then add pair to new dictionary
            if value['side'] == 'buy':
                filteredDict[key] = value
        sortedDict = OrderedDict(sorted(filteredDict.items(),
            key = lambda x: getitem(x[1], 'price'), reverse=True))

        maxValue = list(sortedDict.values())[0]['price']
        sellPrice = Decimal(truncate(Decimal(maxValue) * Decimal(((gridperc/100)+1))))

        return round(sellPrice,3)





def getSpecificDict(buyorsell):
    filteredDict = {}
    for (key, value) in ordersDict.items():
   # Check if key is even then add pair to new dictionary
        if value['side'] == f'{buyorsell}':
            filteredDict[key] = value
    return filteredDict

def sortDict(dictToBeSorted,key,reverse,keyorvalue):
    res = OrderedDict(sorted(dictToBeSorted.items(),
       key = lambda x: getitem(x[1], f'{key}'), reverse=reverse))
    return list(res.keys()) if keyorvalue == 'key' else list(res.values())

def checkSellOrder():
    global apr
    global mayAdapt
    sellOrderDict = getSpecificDict('sell')
    sortedSellOrders = sortDict(sellOrderDict,'price',False,'key')
    if len(sortedSellOrders) > 0:
        try:
            idToFetch = sortedSellOrders[0]
            order = exchange.fetchOrder(idToFetch, symbol = symbol, params = {})
            if order['status'] == 'closed':
                endTime = time.time()
                timeElapsed = endTime - startTime
                timeElapsedInHours = timeElapsed / 3600
                profitPerHour = Decimal(totalProfitSinceStartup) / Decimal(timeElapsedInHours)
                apr = round(((profitPerHour*8760/startBalance)*100),2)
                sendMessage(f"Sell order filled\nYour profit in this trade: {calculateProfit(Decimal(order['cost']))}\nYour total profit since bot start-up: {totalProfitSinceStartup}\nRuntime: {round(timeElapsedInHours,2)} hours\nProfit per hour: {round(profitPerHour,2)}\nAPR: {apr}\nTarget APR: {config.target_apr}")
                ordersDict.pop(idToFetch)
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
        isAPIAvailable = True if status['status'] == 'ok' else False
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
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    connectivityCheck()
    if isAPIAvailable:
        checkSellOrder()
        print(f"{dt_string} Checking if orders have been filled...")         
        try:
            buyOrderDict = getSpecificDict('buy')
            buyOrdersList = list(buyOrderDict)
            idnumberDict = sortDict(buyOrderDict,'price',True,'key')
            idnumberList = list(idnumberDict)
            if len(buyOrdersList) != 0:
                idnumber = idnumberList[0]
                order = exchange.fetchOrder(idnumber, symbol = symbol, params = {})
                if(order['status'] == 'closed'):
                    print(f"{dt_string} Order filled, calculating sell price...")
                    try:
                        marketStructure = exchange.markets[symbol]
                        lenstr = symboldata.basePrecision
                        createOrder("sell",round(Decimal(order['filled']),lenstr),getSellPriceHighestBuyOrder())
                        #setDust()
                    except Exception as e: 
                        print(e)
        except Exception as e: 
            print(e)


        
        print("Checking if bot can create new buy orders...")
        if enoughBalance:
            buyOrdersDict = getSpecificDict('buy')
            sortedBuyOrders = sortDict(buyOrderDict,'price',False,'value')[0]['price']
            if len(buyOrdersDict) < grids and len(buyOrdersDict) != 0:
                    print(f"Can create new buy order(s)")
                    try:
                        createOrder("buy",getQuantity(),truncate(Decimal(sortedBuyOrders)-stepsize))                
                    except Exception as e: 
                        print(e) 
                        #print(e)
        else: 
            print(f"Not sufficient funds to create buy orders")

        
        print(f'Checking if orders are still inside range')
        try:
            currentSetPrice = truncate(getCurrentPrice()-stepsize)
            buyOrderDict = getSpecificDict('buy')
            sortedBuyOrders = sortDict(buyOrderDict,'price',True,'value')
            maxBuyOrder = Decimal(sortedBuyOrders[0]['price'])
            threshold = (maxBuyOrder)*(1+(Decimal(gridperc)/100))
            if (Decimal(currentSetPrice) > Decimal(maxBuyOrder))*(1+(Decimal(gridperc)/100)) and (order['status'] == 'open'):
                try:
                    print(f"{dt_string} Cancelling lowest order and bringing it on top")
                    sendMessage('Cancelling lowest order and bringing it on top')
                    orderToPop = sortDict(buyOrderDict,'price',False,'key')[0]
                    exchange.cancel_order (str(orderToPop),symbol=symbol)
                    try:
                        order = exchange.fetchOrder(orderToPop, symbol = symbol, params = {})
                        filledQuantity = order['filled']
                        if filledQuantity > 0:
                            if exchange.has['createMarketOrder']:
                                exchange.createOrder(symbol,'market','sell',filledQuantity,{})
                    except Exception as e:
                            sendMessage(str(e))
                        
                    
                    ordersDict.pop(orderToPop)
            
                #adding buy order
                    global currentQuantity
                    createOrder("buy",getQuantity(),Decimal(maxBuyOrder)*(1+(Decimal(gridperc)/100)))
                except ccxt.ExchangeError as e:
                    sendMessage(str(e))
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





try:
    threading.Thread(target=startjob()).start()
    threading.Thread(target=main()).start()
except Exception as e:
    print(e)

while 1:
    schedule.run_pending()
    time.sleep(0.1)




