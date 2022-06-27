import os
import time

import redis
import telebot
from telebot import types

bot = telebot.TeleBot(os.environ['SALARYINFOREIGNCURRENCY_BOT'])

CURRENCIES = ['RUB', 'UAH', 'BYN',
              'USD', 'EUR', 'GBP']

start_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
start_menu_items = [types.KeyboardButton(each) for each in CURRENCIES]
start_menu_markup.row(*CURRENCIES[0:3])
start_menu_markup.row(*CURRENCIES[3:6])

add_currency_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
add_currency_items = [types.KeyboardButton(each) for each in CURRENCIES + ['Продолжить']]
add_currency_markup.row(*CURRENCIES[0:3])
add_currency_markup.row(*CURRENCIES[3:6])
add_currency_markup.row('Продолжить')

frequency = ['Ежедневно', 'Еженедельно',
             'Ежемесячно', 'Один раз']  # Не менять порядок
frequency_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
frequency_items = [types.KeyboardButton(each) for each in frequency]
frequency_markup.row(*frequency[0:2])
frequency_markup.row(*frequency[2:4])

renew_menu = ['Проверить', 'Курс ЦБ', 'Графики',
              'Справка', 'Сбросить']
renew_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
renew_menu_items = [types.KeyboardButton(each) for each in renew_menu]
renew_menu_markup.row(*renew_menu_items[0:3])
renew_menu_markup.row(*renew_menu_items[3:5])

db = redis.from_url(os.environ.get("REDIS_URL"))


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(chat_id=message.chat.id, text='test')


if __name__ == '__main__':
    while True:
        try:
            bot.polling()
        except:
            time.sleep(60)
