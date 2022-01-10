import builtins
from binance.client import Client
from config import *
from binance.enums import *
from config import API_KEY,API_KEY_SECRET

client = Client(API_KEY, API_KEY_SECRET)

def getBalance():
    balance = client.get_asset_balance(asset='USDT')['free']
    return str(balance)