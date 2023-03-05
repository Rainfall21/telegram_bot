import datetime
import os
from datetime import timedelta
import math
import requests

WEATHER_MAP_TOKEN = os.getenv('WEATHER_API')


def get_location(message):
    response = requests.get(
        f"http://api.openweathermap.org/geo/1.0/direct?q={message}&limit=5&appid={WEATHER_MAP_TOKEN}")
    data = response.json()
    return get_weather(lon=data[0]['lon'], lat=data[0]['lat'])


def get_weather(lon, lat):
    try:
        city_response = requests.get(
            f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={WEATHER_MAP_TOKEN}")
        city_data = city_response.json()
        city = city_data[0]["local_names"]['ru']
        code_to_emoji = {
            "Clear": "Ясно \U00002600",
            "Clouds": "Облачно \U00002601",
            "Rain": "Дождь \U00002614",
            "Drizzle": "Дождь \U00002614",
            "Thunderstorm": "Гроза \U000026A1",
            "Snow": "Снег \U0001F328",
            "Mist": "Туман \U0001F32B"
        }

        weather_response = requests.get(
            f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={WEATHER_MAP_TOKEN}&units=metric&cnt=5")
        weather_data = weather_response.json()
        temperature = weather_data['list'][0]['main']['temp']
        if temperature < 0:
            temperature = math.floor(temperature)
        elif temperature > 0:
            temperature = math.ceil(temperature)
        humidity = weather_data['list'][0]['main']['humidity']
        wind = weather_data['list'][0]['wind']['speed']
        sunrise = datetime.datetime.fromtimestamp(weather_data['city']['sunrise'])
        sunset = datetime.datetime.fromtimestamp(weather_data['city']['sunset'])
        weather_description = weather_data['list'][0]['weather'][0]['main']
        if weather_description in code_to_emoji:
            weather_emoji = code_to_emoji[weather_description]
        else:
            weather_emoji = "Что за погода за окном? НЕПОНЯТНО"

        umbrella = ""
        weather_slice = weather_data['list'][:4]
        for hour in weather_slice:
            condition = int(hour['weather'][0]['id'])
            if condition < 700:
                umbrella  = "Советую взять зонтик \U00002602"
        my_timezone = -3
        timezone = weather_data['city']['timezone']/3600 + my_timezone
        sunset = sunset + timedelta(hours=timezone)
        sunrise= sunrise + timedelta(hours=timezone)
        today = datetime.datetime.now() + timedelta(hours=timezone)
        message = (f'***{today.strftime("%H:%M %d-%m-%Y")}***\n'
                   f'Город: {city}\nТемпература: {temperature}С° {weather_emoji}\n'
                   f'Влажность: {humidity}%\nСкорость ветра: {wind} метров в секунду\n'
                   f'Восход солнца: {sunrise.strftime("%H:%M")}\nЗакат солнца: {sunset.strftime("%H:%M")}\n'
                   f'{umbrella}')
    except:
        message = "Проверь название города"

    return message
