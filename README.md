# PyGrid grid bot

Use at your own risk! I'm not a professional coder and I'm doing this project just for fun.


Installation steps:
1. Clone this repo
2. Use the command "pip3 install -r requirements.txt" to install the requirements.
3. Configure the config.py file to your liking.
4. Make sure you pay trading fees with BNB, else the bot will get stuck eventually.
5. Use the command "python3 run.py" to start the bot.

TG Commands:
/balance

Tips: 
- Use PM2 to manage the process.
- Use FTX exchange, you can get 0% maker fee when you are staking 25 FTT.



Bug reports will be appreciated.

Features:
- Trades assets in a grid-like manner. The grids are dynamic; this means there's no hassle with choosing a range!
- Automatically buys BNB to pay for trading fees if your BNB balance is < 0.1
- Telegram messages
- Compounding
- CCXT implementation



Upcoming features:
- Slow mode -> this means no extra buy orders will be created when price moves up and fills sell orders.
- Complete refactoring of code
- Decreasing amount of API calls since we get rate limited very easily.



Thanks!
