import requests
import random
import os

genres = {
    1: "триллер",
    2: "драма",
    3: "криминал",
    4: "мелодрама",
    5: "детектив",
    6: "фантастика",
    7: "приключения",
    8: "биография",
    10: "вестерн",
    11: "боевик",
    12: "фэнтези",
    13: "комедия",
    14: "военный",
    15: "история",
    17: "ужасы",
    18: "мультфильм",
    19: "семейный",
    21: "спорт",
    22: "документальный",
}


def get_genre_id(genre):
    return get_random_film(list(genres.keys())[list(genres.values()).index(genre)])


def get_random_film(id):
    header = {
        'X-API-KEY': os.getenv('KPU')
    }
    header_kp = {
        'X-API-kEY': os.getenv('KP')
    }
    response = requests.get(f'https://kinopoiskapiunofficial.tech/api/v2.2/films?genres={id}&order=RATING&type=FILM&ratingFrom=7&ratingTo=10&yearFrom=1000&yearTo=3000&page=1', headers=header)
    data = response.json()
    items = data['items']
    index = random.randint(0, 20)
    kp_id = items[index]['kinopoiskId']
    response = requests.get(f'https://api.kinopoisk.dev/v1/movie/{kp_id}', headers=header_kp)
    data = response.json()
    film = {
        'name': data['name'],
        'year': data['year'],
        'rating': data['rating']['imdb'],
        'description': data['description'],
        'poster': data['poster']['url']
    }
    return film
