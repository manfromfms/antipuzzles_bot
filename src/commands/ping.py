import telebot

def ping(message, bot=telebot.TeleBot(token="", validate_token=False)):
    """
    This is a ping command implementation that can be used as an example.
    """
    bot.reply_to(message, "Pong! 🏓")

    print('Command executed:', message)
