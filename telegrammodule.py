from telegram import Update, ForceReply, message
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from config import tg_token,tg_enabled,tg_chat_id,grids
import threading
import time







def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )

def sendMessage(tekst) -> None:
    if tg_enabled == True:
        updater = Updater(token=tg_token, use_context=True)
        updater.bot.send_message(chat_id=tg_chat_id,text=tekst)



def main() -> None:
    """Start the bot."""
    if tg_enabled == True:
        updater = Updater(token=tg_token, use_context=True)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", start))
        updater.start_polling()
        updater.bot.send_message(chat_id=tg_chat_id,text=f'Bot started succesfully! Bot created {grids} buy orders!')
        #updater.idle() #commented out for threading





