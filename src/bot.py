# @dzmitrysk_bot

import config
from datetime import datetime, timedelta
import requests
import telebot


bot = telebot.TeleBot(config.token)


@bot.message_handler(content_types=['text'])
def message_repeater(message):
    bot.send_message(message.chat.id, get_exchange_rates(), parse_mode='html')


def get_exchange_rates():
    CURRENCIES = {'USD', 'EUR', 'RUB', 'UAH', 'PLN'}
    date_today = datetime.now().strftime('%Y-%m-%d')
    date_yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    parameters = {"periodicity": "0", "ondate": date_today}
    rates_today = requests.get('https://www.nbrb.by/api/exrates/rates', params=parameters)

    parameters["ondate"] = date_yesterday
    rates_yesterday = requests.get('https://www.nbrb.by/api/exrates/rates', params=parameters)

    info_today = [item for item in rates_today.json() if item['Cur_Abbreviation'] in CURRENCIES]
    info_yesterday = [item for item in rates_yesterday.json() if item['Cur_Abbreviation'] in CURRENCIES]

    rates_diff = {}
    for item in info_today:
        currency = {'scale': item['Cur_Scale'], 'today': float(item['Cur_OfficialRate']), 'yesterday': 0.0, 'grow': ''}
        rates_diff[item['Cur_Abbreviation']] = currency

    for item in info_yesterday:
        rates_diff[item['Cur_Abbreviation']]['yesterday'] = float(item['Cur_OfficialRate'])

    for curr in rates_diff.keys():
        rates_diff[curr]['grow'] = f"{['+', ''][rates_diff[curr]['today'] < rates_diff[curr]['yesterday']]}" \
                                   f"{round(rates_diff[curr]['today'] - rates_diff[curr]['yesterday'], 4)}"

    exchange_rates = [f'<b>Курсы валют по НБРБ на сегодня ({date_today}):</b>\n',]
    for curr, info in rates_diff.items():
        exchange_rates.append(f"<code>{info['scale']:>3} {curr:>3} = {info['today']:<} ({info['grow']:<1}) BYN</code>")

    return '\n'.join(exchange_rates)


if __name__ == '__main__':
    bot.infinity_polling()
