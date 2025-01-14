import telebot

def info(message, bot=telebot.TeleBot(token="", validate_token=False)):
    """
    This is an info command implementation. It should provide up-to-date information about this bot.
    """
    bot.reply_to(message, "I am an @antipuzzles_bot in early stages of development. "
                          "To support this bot or get further information visit a github repo: "
                          "https://github.com/manfromfms/antipuzzles_bot. Main developer is @NormChell_2889.")

    print('Command executed:', message)
