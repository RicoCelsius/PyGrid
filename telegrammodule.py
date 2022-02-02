from telegram import Update, ForceReply, message
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from config import TG_TOKEN,TG_ENABLED,TG_CHAT_ID,GRIDS
import threading
import time
import binancedata



def balance(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /balance is issued."""
    user = update.effective_user
    update.message.reply_text(
        f'Your balance is {binancedata.getBalance()} USDT'
    )


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )

def sendMessage(tekst) -> None:
    if TG_ENABLED == True:
        updater = Updater(token=TG_TOKEN, use_context=True)
        updater.bot.send_message(chat_id=TG_CHAT_ID,text=tekst)



def main() -> None:
    """Start the bot."""
    if TG_ENABLED == True:
        updater = Updater(token=TG_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("balance",balance))
        updater.start_polling()
        updater.bot.send_message(chat_id=TG_CHAT_ID,text=f'Bot started succesfully! Bot created {GRIDS} buy orders!')
        #updater.idle() #commented out for threading





