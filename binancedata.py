import builtins
from urllib import request
from binance.client import Client
from binance.enums import *
from config import API_KEY,API_KEY_SECRET,COMPOUND_WALLET_PERC,SYMBOL,COMPOUND,QUANTITY,EXCHANGE
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

# fetch the BTC/USDT ticker for use in converting assets to price in USDT
ticker = exchange.fetch_ticker(SYMBOL)

# calculate the ticker price of BTC in terms of USDT by taking the midpoint of the best bid and ask
priceUSDT = Decimal((float(ticker['ask']) + float(ticker['bid'])) / 2)
print("LUNA Price = " + str(priceUSDT))


def getCurrentPrice():
    priceUSDT = Decimal((float(ticker['ask']) + float(ticker['bid'])) / 2)
    return priceUSDT

def getBalance():
    balance = exchange.fetchBalance()['USDT']['free']
    print(str(balance))
    return str(balance)

def getDecimalAmounts(symbol):
    #response = requests.get("https://api.binance.com/api/v3/exchangeInfo?symbol="+symbol)
    #minQty = float(response.json()["symbols"][0]["filters"][2]["minQty"])
    amountDecimals = 2
    return amountDecimals
    


def getQuantity():
    if COMPOUND == True:
        balance = exchange.fetchBalance()['USDT']['free']
        quotePrice = getCurrentPrice()
        print(balance)
        print(quotePrice)
        quantityDollars = Decimal(balance)*Decimal((COMPOUND_WALLET_PERC/100))
        quoteQuantity = quantityDollars/quotePrice
        print("Quote quantity = " + str(quoteQuantity))
        print("Quantitydollars =" + str(quantityDollars))
        print("config quantity =" + str(QUANTITY))
        return round(quoteQuantity,2)
    else: return QUANTITY
