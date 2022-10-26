import builtins
from urllib import request
from config import API_KEY,API_KEY_SECRET,COMPOUND_WALLET_PERC,SYMBOL,COMPOUND,DOLLARQUANTITY,EXCHANGE
from decimal import *
import json
import requests
import math
import ccxt


exchange_id = EXCHANGE
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'apiKey': API_KEY,
    'secret': API_KEY_SECRET,
    'enableRateLimit': True,
})

lastQuantity = []
# fetch the BTC/USDT ticker for use in converting assets to price in USDT
ticker = exchange.fetch_ticker(SYMBOL)

# calculate the ticker price of BTC in terms of USDT by taking the midpoint of the best bid and ask
priceUSDT = Decimal((float(ticker['ask']) + float(ticker['bid'])) / 2)
print("LUNA Price = " + str(priceUSDT))


def getCurrentPrice():
    priceUSDT = Decimal((float(ticker['ask']) + float(ticker['bid'])) / 2)
    return priceUSDT

def getBalance():
    balance = exchange.fetchBalance()['USD']['free']
    print(str(balance))
    return str(balance)

def getDecimalAmounts(symbol):
    #response = requests.get("https://api.binance.com/api/v3/exchangeInfo?symbol="+symbol)
    #minQty = float(response.json()["symbols"][0]["filters"][2]["minQty"])
    amountDecimals = 3
    return amountDecimals
    


def getQuantity():
    lenstr = len(str(marketStructure['precision']['amount']).split(".")[1])
    if COMPOUND == True:
        try:
            balance = exchange.fetchBalance()['USD']['free']
            quotePrice = getCurrentPrice()
            quantityDollars = Decimal(balance)*Decimal((COMPOUND_WALLET_PERC/100))
            quoteQuantity = quantityDollars/quotePrice
            marketStructure = exchange.markets[SYMBOL]
            
            lastQuantity.insert(0,round(quoteQuantity,lenstr))
            print(f"Length lastQuantity = {len(lastQuantity)}")

            if len(lastQuantity) > 3:
                lastQuantity.pop()
            return round(quoteQuantity,lenstr)
        except: return lastQuantity[0]
    else:
        
        
        
         return round(Decimal(DOLLARQUANTITY)/getCurrentPrice(),lenstr)
