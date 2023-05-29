import os
import time
from datetime import datetime

import telebot
from telebot import types

import WorkWithJSON
from core import get_salary_text

bot = telebot.TeleBot(os.environ['SALARYINFOREIGNCURRENCY_BOT'])
db_filename = 'db.json'
db = WorkWithJSON.load_dict_from_json(db_filename)

renew_menu = ['Проверить', 'Курс ЦБ', 'Графики',
              'Справка', 'Сбросить']
renew_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
renew_menu_items = [types.KeyboardButton(each) for each in renew_menu]
renew_menu_markup.row(*renew_menu_items[0:3])
renew_menu_markup.row(*renew_menu_items[3:5])


def send_salary(message_chat_id, val):
    text = get_salary_text(val)
    bot.send_message(chat_id=int(message_chat_id), text=text, reply_markup=renew_menu_markup)


if __name__ == '__main__':
    start_time = time.time()
    sum, count, error = 0, 0, 0

    for id in db.keys():
        if not id.isdigit():
            continue
        sum += 1
        val = db.get(id)
        if not isinstance(val, dict): continue
        if val.get('state') != 255: continue
        if (val.get('frequency') == 0) \
                or (val.get('frequency') == 1 and datetime.today().isoweekday() == 1) \
                or (val.get('frequency') == 2 and datetime.today().day == 1):
            try:
                send_salary(id, val)
                count += 1
            except:
                error += 1

    text = f"""Оповещено {count} из {sum} человек за {time.time() - start_time:.1f}c, {error} ошибок"""
    bot.send_message(chat_id=211522613, text=text, reply_markup=renew_menu_markup)
