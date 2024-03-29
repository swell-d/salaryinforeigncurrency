import codecs
import time

import telebot
from telebot import types

import WorkWithJSON
from core import get_salary_text, get_graf, get_cbrf_text

with codecs.open("api.key", 'r', 'utf-8') as file:
    key = file.read().strip()
bot = telebot.TeleBot(key)

ALL_CURRENCIES = ['AUD', 'AZN', 'GBP', 'AMD', 'BYN', 'BGN', 'BRL', 'HUF', 'VND', 'HKD', 'GEL', 'DKK', 'AED', 'USD',
                  'EUR', 'EGP', 'INR', 'IDR', 'KZT', 'CAD', 'QAR', 'KGS', 'CNY', 'MDL', 'NZD', 'NOK', 'PLN', 'RON',
                  'XDR', 'SGD', 'TJS', 'THB', 'TRY', 'TMT', 'UZS', 'UAH', 'CZK', 'SEK', 'CHF', 'RSD', 'ZAR', 'KRW',
                  'JPY', 'RUB']
CURRENCIES = ['RUB', 'UAH', 'BYN',
              'USD', 'EUR', 'GBP',
              'SEK', 'TRY', 'THB']

start_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
start_menu_items = [types.KeyboardButton(each) for each in CURRENCIES]
start_menu_markup.row(*CURRENCIES[0:3])
start_menu_markup.row(*CURRENCIES[3:6])
start_menu_markup.row(*CURRENCIES[6:9])

add_currency_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
add_currency_items = [types.KeyboardButton(each) for each in CURRENCIES + ['Продолжить']]
add_currency_markup.row(*CURRENCIES[0:3])
add_currency_markup.row(*CURRENCIES[3:6])
add_currency_markup.row(*CURRENCIES[6:9])
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

db_filename = 'db.json'
db = WorkWithJSON.load_dict_from_json(db_filename)


def user_is_new(message):
    id = str(message.chat.id)
    return db.get(id) is None


@bot.message_handler(commands=['start'])
def start_command(message):
    text = 'Привет! Этот бот умеет конвертировать твою текущую зарплату в другие валюты и присылать тебе регулярные ' \
           'уведомления о её изменениях в популярных валютах мира, а ещё - строить графики'
    bot.send_message(chat_id=message.chat.id, text=text)
    bot.send_message(chat_id=211522613, text="Новый пользователь", reply_markup=renew_menu_markup)
    text = 'Выбери валюту своей текущей зарплаты. Воспользуйся кнопками или отправь трёхбуквенный код валюты'
    bot.send_message(chat_id=message.chat.id, text=text, reply_markup=start_menu_markup)

    id = str(message.chat.id)
    val = {'state': 0}
    db[id] = val
    WorkWithJSON.save_dict_to_json(db, db_filename)


def send_float_error(message):
    text = """Неверный формат. Попробуй ещё раз. Введи сумму, например 50000"""
    bot.send_message(chat_id=message.chat.id, text=text)
    return False


def check_float(message):
    try:
        value = float(message.text.replace(',', '.').replace(' ', '').strip())
        if value <= 0: return send_float_error(message)
        return value
    except:
        return send_float_error(message)


@bot.message_handler(content_types=["text"])
def new_text(message):
    id = str(message.chat.id)
    if user_is_new(message) or message.text == 'Сбросить':
        start_command(message)
        return

    val = db.get(id)
    if message.text == 'Справка':
        text = """Для вопросов и предложений: @swell_d
Для расчёта используются официальные курсы ЦБ РФ. Обновление курсов происходит в полночь по Москве
Код бота в открытом доступе: https://github.com/swell-d/salaryinforeigncurrency"""
        bot.send_message(chat_id=message.chat.id, text=text, reply_markup=renew_menu_markup)

    elif message.text == 'Курс ЦБ':
        send_cbrf(message.chat.id, val)

    elif val['state'] == 0 and message.text in ALL_CURRENCIES:
        val['currency'] = message.text
        text = """Введи сумму"""
        bot.send_message(chat_id=message.chat.id, text=text)
        val['state'] = 1
        db[id] = val
        WorkWithJSON.save_dict_to_json(db, db_filename)

    elif val['state'] == 0 and message.text not in ALL_CURRENCIES:
        text = """Выбери валюту своей текущей зарплаты. Воспользуйся кнопками или отправь трёхбуквенный код валюты"""
        bot.send_message(chat_id=message.chat.id, text=text, reply_markup=start_menu_markup)

    elif val['state'] == 1:
        value = check_float(message)
        if not value: return
        val['salary'] = value
        text = """Выбери частоту уведомлений"""
        bot.send_message(chat_id=message.chat.id, text=text, reply_markup=frequency_markup)
        val['state'] = 2
        db[id] = val
        WorkWithJSON.save_dict_to_json(db, db_filename)

    elif val['state'] == 2 and message.text in frequency:
        val['frequency'] = frequency.index(message.text)
        text = "Выбери интересующие тебя валюты, уведомления по которым ты хотел бы получать, а затем нажми " \
               "'Продолжить'. Воспользуйся кнопками или отправь трёхбуквенный код валюты"
        bot.send_message(chat_id=message.chat.id, text=text, reply_markup=add_currency_markup)
        val['state'] = 3
        db[id] = val
        WorkWithJSON.save_dict_to_json(db, db_filename)

    elif val['state'] == 2 and message.text not in frequency:
        text = """Выбери частоту уведомлений. Воспользуйся кнопками"""
        bot.send_message(chat_id=message.chat.id, text=text, reply_markup=frequency_markup)

    elif val['state'] == 3 and message.text in ['Продолжить']:
        if val.get('list_of_currencies') is None:
            val['list_of_currencies'] = CURRENCIES
        val['state'] = 255
        db[id] = val
        WorkWithJSON.save_dict_to_json(db, db_filename)
        send_salary(id, val)

    elif val['state'] == 3 and message.text in ALL_CURRENCIES:
        if val.get('list_of_currencies') is None:
            val['list_of_currencies'] = []
        if message.text not in val['list_of_currencies']:
            val['list_of_currencies'] += [message.text]
            db[id] = val
            WorkWithJSON.save_dict_to_json(db, db_filename)

    elif val['state'] == 3 and message.text not in ALL_CURRENCIES + ['Продолжить']:
        text = """Выбери интересующие тебя валюты. Воспользуйся кнопками или отправь трёхбуквенный код валюты"""
        bot.send_message(chat_id=message.chat.id, text=text, reply_markup=add_currency_markup)

    elif val['state'] == 255 and message.text == 'Проверить':
        send_salary(id, val)

    elif val['state'] == 255 and message.text == 'Графики':
        send_grafs(id, val)

    else:
        text = """Неизвестная команда"""
        bot.send_message(chat_id=message.chat.id, text=text, reply_markup=renew_menu_markup)
        bot.send_message(chat_id=211522613, text=f"{message.chat.id} -> {message.text}", reply_markup=renew_menu_markup)


def send_salary(message_chat_id, params):
    text = get_salary_text(params)
    bot.send_message(chat_id=int(message_chat_id), text=text, reply_markup=renew_menu_markup)


def send_cbrf(message_chat_id, params):
    text = get_cbrf_text(params)
    bot.send_message(chat_id=int(message_chat_id), text=text, reply_markup=renew_menu_markup)


def send_grafs(message_chat_id, params):
    salary = params.get('salary', 0)
    currency_from = params.get('currency', 'RUB')
    for currency_to in params.get('list_of_currencies', CURRENCIES):
        if currency_to == currency_from: continue
        graf = get_graf(currency_from, currency_to, salary)
        bot.send_photo(chat_id=int(message_chat_id), photo=graf, reply_markup=renew_menu_markup)


if __name__ == "__main__":
    while True:
        try:
            bot.polling()
        except:
            time.sleep(60)
