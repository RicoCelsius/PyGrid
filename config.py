from decimal import *

from dotenv import load_dotenv
import os #provides ways to access the Operating System and allows us to read the environment variables
load_dotenv()
api_key=os.getenv("API_KEY")
api_key_secret=os.getenv("API_KEY_SECRET")
tg_token=os.getenv("TG_TOKEN")
tg_chat_id=os.getenv("TG_CHAT_ID")

exchange = 'binance'
symbol = "BTC/BUSD"
post_order_only=False
dollarquantity = 12 #set COMPOUND to False if you want to use this.
apr_target_mode = False #either apr_target or normal
target_apr = 50
buy_protection=False
max_bought_before_cooldown=5
compound = False #Set to True if you want to use a percentage of your wallet instead of an absolute number.
compound_wallet_perc = 1 #percentage of USDT in your wallet to use for creating buy orders. 
gridperc = 0.01
grids = 4

tg_enabled = True #current command(s): /balance
auto_buy_bnb = False #automatically buys BNB if there's not enough left in your wallet
sub_account = ""


mysql_enabled=False
mysql_host=""
mysql_database=""
mysql_username=""
mysql_password=""
