from telegram.ext import Updater, CommandHandler


def botmain():
    
    updater = Updater(token='390691367:AAFKlE_3_3nGReOJz4b0nKuHe7qeVQfm3eI', use_context=True)
    dispatcher = updater.dispatcher
    
    add_handler = CommandHandler('add', add_time)
    dispatcher.add_handler(add_handler)
    
    try:
        updater.start_polling()
    except KeyboardInterrupt:
        print("Keyboard Interrupt, stop bot")
        updater.stop()
    
def add_time(update, context):
    print(update, context.args)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Thanks!")

if __name__ == "__main__":
    botmain()