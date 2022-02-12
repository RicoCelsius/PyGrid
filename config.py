from decimal import *
EXCHANGE = 'binance'
TRADING_FEE = 0.1
PAY_FEE_BNB = False
API_KEY = ''
API_KEY_SECRET = '' #Please turn on IP whitelist for extra security.
SYMBOL = 'LUNAUSDT'
QUANTITY = 0.4 #set COMPOUND to False if you want to use this.
COMPOUND = True #Set to True if you want to use a percentage of your wallet instead of an absolute number.
COMPOUND_WALLET_PERC = 1 #percentage of USDT in your wallet to use for creating buy orders. 
GRIDPERC = 0.25
GRIDS = 3
TG_TOKEN = ''
TG_CHAT_ID = ''
TG_ENABLED = False #current command(s): /balance
AUTO_BUY_BNB = True #automatically buys BNB if there's not enough left in your wallet
