import telebot

import os
from dotenv import load_dotenv

import src.commands.ping
import src.commands.info

load_dotenv()


def main():
    bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))


    @bot.message_handler(commands=['ping'])
    def ping(message):
        src.commands.ping.ping(message, bot)


    @bot.message_handler(commands=['info'])
    def info(message):
        src.commands.info.info(message, bot)


    bot.infinity_polling()

if __name__ == "__main__":
    main()
