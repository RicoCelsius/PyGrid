from telegram import Update, ForceReply, message
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from config import TG_TOKEN,TG_ENABLED
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

def startup(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
    

def main() -> None:
    """Start the bot."""
    updater = Updater(TG_TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("balance",balance))
    updater.start_polling()
    

    
    #updater.idle() commented out for threading







