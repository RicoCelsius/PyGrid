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
# fetch the BTC/USDT ticker for use in converting assets to price in USDT
ticker = exchange.fetch_ticker(config.symbol)

# calculate the ticker price of BTC in terms of USDT by taking the midpoint of the best bid and ask
priceUSDT = Decimal((float(ticker['ask']) + float(ticker['bid'])) / 2)
print("LUNA Price = " + str(priceUSDT))


def getCurrentPrice():
    priceUSDT = Decimal((float(ticker['ask']) + float(ticker['bid'])) / 2)
    return priceUSDT

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
    # print(marketStructure)
    # print(marketStructure['precision'])
    #lenstr = len(str(marketStructure['precision']['amount']))
    lenstr = 3
    if config.compound == True:
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
    else:
        
        
        
         return round(Decimal(config.dollarquantity)/getCurrentPrice(),lenstr)
