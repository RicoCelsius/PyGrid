import builtins
from urllib import request
from binance.client import Client
from binance.enums import *
from config import API_KEY,API_KEY_SECRET,COMPOUND_WALLET_PERC,SYMBOL,COMPOUND,QUANTITY
from decimal import *
import json
import requests
import math
client = Client(API_KEY, API_KEY_SECRET)

def getBalance():
    balance = client.get_asset_balance(asset='USDT')['free']
    return str(balance)

def getDecimalAmounts(symbol):
    response = requests.get("https://api.binance.com/api/v3/exchangeInfo?symbol="+symbol)
    minQty = float(response.json()["symbols"][0]["filters"][2]["minQty"])
    amountDecimals = int(len(str(minQty).split('.')[-1]))
    return amountDecimals
    


def getQuantity():
    if COMPOUND == True:
        balance = Decimal(client.get_asset_balance(asset='USDT')['free'])
        quotePrice = Decimal(client.get_symbol_ticker(symbol=SYMBOL)["price"])
        print(balance)
        print(quotePrice)
        quantityDollars = Decimal(balance)*Decimal((COMPOUND_WALLET_PERC/100))
        quoteQuantity = quantityDollars/quotePrice
        print("Quote quantity = " + str(quoteQuantity))
        print("Quantitydollars =" + str(quantityDollars))
        print("config quantity =" + str(QUANTITY))
        return round(quoteQuantity,2)
    else: return QUANTITY
