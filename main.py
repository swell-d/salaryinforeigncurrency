import os
import time

import telebot

bot = telebot.TeleBot(os.environ['SALARYINFOREIGNCURRENCY_BOT'])


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(chat_id=message.chat.id, text='test')


if __name__ == '__main__':
    while True:
        try:
            bot.polling()
        except:
            time.sleep(60)
