import io
from datetime import datetime, timedelta

import matplotlib.dates
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta

currency_by_date = {}


def get_rate_from_cache(currency_from, currency_to, date=None):
    return 1
    # if date is None: date = datetime.strftime(datetime.now(), "%Y-%m-%d")
    # value = currency_by_date.get(date, {}).get(currency_from, {}).get(currency_to)
    # if value is None:
    #     if currency_by_date.get(date) is None: currency_by_date[date] = {}
    #     if currency_by_date[date].get(currency_from) is None: currency_by_date[date][currency_from] = {}
    #     date_parts = date.split('-')
    #     value = Currency.get_rate(currency_from, currency_to, f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}")
    #     currency_by_date[date][currency_from][currency_to] = value
    #     currency_by_date_obj.save()
    # return value


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
