import os
import requests
from googletrans import Translator
from weather import get_location
from bs4 import BeautifulSoup
from weather import WEATHER_MAP_TOKEN

country_api = os.getenv('COUNTRY_API')
news_api = os.getenv('NEWS_API')
emoji_api = os.getenv('EMOJI_API')


def get_info(message):
    response = requests.get(f'https://api.dev.me/v1-list-countries?language=ru&x-api-key={country_api}')
    data = response.json()
    countries = {}
    for country in data['list']:
        countries[country['code']] = country['translations']['rus']['common']
    if message in countries.values():
        country_code = list(countries.keys())[list(countries.values()).index(message)]
        response = requests.get(f'https://api.dev.me/v1-get-country-details?code={country_code}&x-api-key={country_api}')
        data = response.json()
        capital = to_translate(''.join(data['capital']),src='en', dest='ru')
        currency_code = list(data['currencies'].keys())[0]
        languages = to_translate(list(data['languages'].values())[0],src='en', dest='ru')
        currency = f'{to_translate(list(data["currencies"].values())[0]["name"],src="en", dest="ru")}'
        currency_symbol = list(data["currencies"].values())[0]["symbol"]
        weather = get_location(capital).split('\n')
        population = f"{data['population']:,}"
        timezone = data['timezones'][0]
        city_sunrise = weather[5]
        city_sunset = weather[6]
        response = requests.get(f'https://api.dev.me/v1-get-currency-exchange-rate?from=rub&to={currency_code}&x-api-key={country_api}')
        data = response.json()
        exchange = data['exchangeRate']
        if exchange < 1:
            exchange = 1/exchange
            exchange_rate = f"1 {currency_symbol} = {'{:.2f}'.format(exchange)} ₽"
        else:
            exchange_rate = f"1 ₽ = {'{:.2f}'.format(exchange)} {currency_symbol} "
        news = get_news(capital)
        try:
            flag = get_flag(to_translate(message, src='ru', dest='en'))
        except:
            flag = ''
        places = f'https://www.turizm.ru/{to_translate(message, src="ru", dest="en")}/places/'
        msg = (f"Страна: {message} {flag}\n"
               f"Столица: {capital}\n"
               f"Язык: {languages}\n"
               f"Население: {population} человек\n"
               f"Валюта: {currency}/{currency_symbol}\n"
               f"Курс валют: {exchange_rate}\n"
               f"Временная зона: {timezone}\n"
               f"{city_sunrise}\n"
               f"{city_sunset}\n"
               f"Достопримечательности: {places}\n"
               f"Новости: \n"
               f"{news[0]['title']}\n"
               f"{news[0]['link']}\n"
               f"{news[1]['title']}\n"
               f"{news[1]['link']}"
               )
        return msg
    else:
        try:
            response = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={message}&limit=5&appid={WEATHER_MAP_TOKEN}')
            data = response.json()
            country_code = data[0]['country']
            response = requests.get(
                f'https://api.dev.me/v1-get-country-details?code={country_code}&x-api-key={country_api}')
            data = response.json()
            country = data['translations']['rus']['common']
            capital = to_translate(''.join(data['capital']), src='en', dest='ru')
            currency_code = list(data['currencies'].keys())[0]
            languages = to_translate(list(data['languages'].values())[0], src='en', dest='ru')
            currency = f'{to_translate(list(data["currencies"].values())[0]["name"], src="en", dest="ru")}'
            currency_symbol = list(data["currencies"].values())[0]["symbol"]
            weather = get_location(message).split('\n')
            population = f"{data['population']:,}"
            timezone = data['timezones'][0]
            city_sunrise = weather[5]
            city_sunset = weather[6]
            response = requests.get(
                f'https://api.dev.me/v1-get-currency-exchange-rate?from=rub&to={currency_code}&x-api-key={country_api}')
            data = response.json()
            exchange = data['exchangeRate']
            if exchange < 1:
                exchange = 1 / exchange
                exchange_rate = f"1 {currency_symbol} = {'{:.2f}'.format(exchange)} ₽"
            else:
                exchange_rate = f"1 ₽ = {'{:.2f}'.format(exchange)} {currency_symbol} "
            news = get_news(message)
            try:
                flag = get_flag(to_translate(country, src='ru', dest='en'))
            except:
                flag = ''
            places = f'https://www.turizm.ru/{to_translate(country, src="ru", dest="en")}/{to_translate(message, src="ru", dest="en")}/places/'
            msg = (f"Страна: {country} {flag}\n"
                   f"Столица: {capital}\n"
                   f"Язык: {languages}\n"
                   f"Население страны: {population} человек\n"
                   f"Валюта: {currency}/{currency_symbol}\n"
                   f"Курс валют: {exchange_rate}\n"
                   f"Временная зона: {timezone}\n"
                   f"{city_sunrise}\n"
                   f"{city_sunset}\n"
                   f"Достопримечательности: {places}\n"
                   f"Новости: \n"
                   f"{news[0]['title']}\n"
                   f"{news[0]['link']}\n"
                   f"{news[1]['title']}\n"
                   f"{news[1]['link']}"
                   )
            return msg
        except:
            return "Проверь название города или страны"


def to_translate(text, src, dest):
    translator = Translator()
    translation = translator.translate(text=text, src=src, dest=dest)
    return translation.text


def get_news(location):
    url = f"https://ria.ru/search/?query={location}"

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    titles = soup.find_all('a', class_="list-item__title color-font-hover-only")
    news = [
        {
            'title': titles[0].text,
            'link': titles[0]['href'],
        },
        {
            'title': titles[1].text,
            'link': titles[1]['href'],
        }
    ]
    return news


def get_flag(country):
    url = f'https://emoji-api.com/emojis/flag-{country.lower()}?access_key={emoji_api}'
    response = requests.get(url)
    data = response.json()
    return data[0]['character']

