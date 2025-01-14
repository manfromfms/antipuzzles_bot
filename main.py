import telebot

import os
from dotenv import load_dotenv

import src.commands.ping as ping_command

load_dotenv()


def main():
    bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))


    @bot.message_handler(commands=['ping'])
    def ping(message):
        ping_command.ping(message, bot)


    bot.infinity_polling()

if __name__ == "__main__":
    main()
