import io
import json
import os
import re
from datetime import datetime, timedelta

import matplotlib.dates
import matplotlib.pyplot as plt
import redis
import requests
from dateutil.relativedelta import relativedelta

db = redis.from_url(os.environ.get("REDIS_URL"))

if db.exists('currency_by_date'):
    currency_by_date = json.loads(db.get('currency_by_date'))
else:
    currency_by_date = {}


def get_rate(cur_from, cur_to, date=datetime.strftime(datetime.now(), "%d/%m/%Y")):
    if db.exists(date) == 0:
        response = requests.get(f"http://www.cbr.ru/scripts/XML_daily.asp", {"date_req": date})
        if response.status_code != 200: raise ConnectionError
        response_content = response.text
        db.set(date, response_content)
    else:
        response_content = str(db.get(date))

    if cur_from == "RUB":
        n1, v1 = 1, 1
    else:
        cur_from_p = re.compile(
            r"<CharCode>" + cur_from + r"</CharCode><Nominal>(\d+)</Nominal><Name>.+?</Name><Value>([\d,]+?)</Value>")
        cur_from_data = re.search(cur_from_p, response_content)
        n1 = float(cur_from_data.group(1))
        v1 = float(cur_from_data.group(2).replace(",", "."))

    if cur_to == "RUB":
        n2, v2 = 1, 1
    else:
        cur_to_p = re.compile(
            r"<CharCode>" + cur_to + r"</CharCode><Nominal>(\d+)</Nominal><Name>.+?</Name><Value>([\d,]+?)</Value>")
        cur_to_data = re.search(cur_to_p, response_content)
        n2 = float(cur_to_data.group(1))
        v2 = float(cur_to_data.group(2).replace(",", "."))

    result = round(v1 / n1 / v2 * n2, 4)
    if not result: raise ConnectionError
    return result


def get_rate_from_cache(currency_from, currency_to, date=None):
    if date is None: date = datetime.strftime(datetime.now(), "%Y-%m-%d")
    value = currency_by_date.get(date, {}).get(currency_from, {}).get(currency_to)
    if value is None:
        if currency_by_date.get(date) is None: currency_by_date[date] = {}
        if currency_by_date[date].get(currency_from) is None: currency_by_date[date][currency_from] = {}
        date_parts = date.split('-')
        value = get_rate(currency_from, currency_to, f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}")
        currency_by_date[date][currency_from][currency_to] = value
    return value


def get_time_delta(notification_frequency):
    if notification_frequency == 0:
        return timedelta(days=-1)
    elif notification_frequency == 1:
        return timedelta(days=-7)
    elif notification_frequency == 2:
        return relativedelta(months=-1)
    else:
        return timedelta(days=0)


def get_salary_line(currency_from, currency_to, salary, notif_freq):
    today = salary * get_rate_from_cache(currency_from, currency_to)
    previous = salary * get_rate_from_cache(currency_from,
                                            currency_to,
                                            datetime.strftime(datetime.now() + get_time_delta(notif_freq), "%Y-%m-%d"))
    delta = today - previous
    return f'{currency_to}: {today :.2f}' + (f'    {"+" if delta > 0 else ""}{delta :.2f}' if delta != 0 else '') + '\n'


def get_currency_line(currency_from):
    today = get_rate_from_cache(currency_from, 'RUB')
    previous = get_rate_from_cache(currency_from,
                                   'RUB',
                                   datetime.strftime(datetime.now() + timedelta(days=-1), "%Y-%m-%d"))
    delta = today - previous
    return f'{currency_from}: {today :.4f}' + (
        f'    {"+" if delta > 0 else ""}{delta :.4f}' if delta != 0 else '') + '\n'


def get_salary_text(params):
    date = datetime.strftime(datetime.now(), "%Y-%m-%d")
    salary = params.get('salary', 0)
    currency_from = params.get('currency', 'RUB')
    notification_frequency = params.get('frequency', 3)
    currencies = ['RUB', 'UAH', 'BYN', 'USD', 'EUR', 'GBP']
    text = f'Ваша зарплата на {date}:\n'
    for currency_to in params.get('list_of_currencies', currencies):
        text += get_salary_line(currency_from, currency_to, salary, notification_frequency)
    return text.strip()


def get_cbrf_text(params):
    date = datetime.strftime(datetime.now(), "%Y-%m-%d")
    currencies = ['UAH', 'BYN', 'USD', 'EUR', 'GBP']
    text = f"Курс ЦБ РФ на {date}:\n"
    for currency_from in params.get('list_of_currencies', currencies):
        if currency_from == 'RUB': continue
        text += get_currency_line(currency_from)
    return text.strip()


def get_graf(currency_from, currency_to, salary):
    dates = get_dates()
    salaries = []
    for day in dates:
        salaries.append(salary * get_rate_from_cache(currency_from, currency_to, day))
    db.set('currency_by_date', json.dumps(currency_by_date))

    _, ax = plt.subplots(1, 1)
    plt.title(f"{salary:.2f} {currency_from} -> {currency_to}")
    ax.plot(dates, salaries)
    ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
    plt.xticks(rotation=20)
    ax.grid(True)

    imgByteArr = io.BytesIO()
    plt.savefig(imgByteArr)
    return imgByteArr.getvalue()


def get_dates():
    dates = []
    day = datetime.now() + timedelta(days=-365)
    while True:
        dates.append(datetime.strftime(day, "%Y-%m-%d"))
        day += timedelta(days=1)
        if day > datetime.now(): return dates


if __name__ == '__main__':
    pass
