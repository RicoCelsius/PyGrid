import ccxt
import config
from decimal import *

exchange_class = getattr(ccxt, config.exchange)
exchange = exchange_class({
    'apiKey': config.api_key,
    'secret': config.api_key_secret,
    'enableRateLimit': True,
})
exchange.load_markets()
marketStructure = exchange.market(config.symbol)



def getFilters():
    return marketStructure['info']['filters']

def getQuote():
    return marketStructure['quote']

def getBasePrecision():
    return marketStructure['precision']['amount']

def getMinimalQuantity():
    minNotional = getFilters()[3]['minNotional']
    return Decimal(minNotional)

def getPricePrecision():
    return marketStructure['precision']['price']

minNotional = getMinimalQuantity()
basePrecision = getQuote()
pricePrecision = getPricePrecision()
quote = getQuote()
