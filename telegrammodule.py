from telegram.ext import Updater
from telegram.ext import CallbackContext
#from telegrammodule import Update
from telegram.ext import CommandHandler
from config import TG_TOKEN,TG_ENABLED
from run import getlatesttradetime

if(TG_ENABLED == True):
    updater = Updater(token=TG_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=getlatesttradetime)

start_handler = CommandHandler('tradetime', start)
dispatcher.add_handler(start_handler)