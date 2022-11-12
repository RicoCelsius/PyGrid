from decimal import *
exchange = 'binance'
api_key = ''
api_key_secret = '' #Please turn on IP whitelist for extra security..
symbol = 'LUNAUSDT'
dollarquantity = 0.4 #set COMPOUND to False if you want to use this.
compound = True #Set to True if you want to use a percentage of your wallet instead of an absolute number.
compound_wallet_perc = 1 #percentage of USDT in your wallet to use for creating buy orders. 
gridperc = 0.25
grids = 3
tg_token = ''
tg_chat_id = ''
tg_enabled = False #current command(s): /balance
auto_buy_bnb = True #automatically buys BNB if there's not enough left in your wallet
sub_account = ""
