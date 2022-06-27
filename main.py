import os

import telebot

bot = telebot.TeleBot(os.environ['SALARYINFOREIGNCURRENCY_BOT'])


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(chat_id=message.chat.id, text='test')
