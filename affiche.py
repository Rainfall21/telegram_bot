import datetime
import requests
import os


def get_affiche():
    header = {
        'X-API-KEY': os.getenv('AFFICHE_KET')
    }
    year = datetime.datetime.now().year
    month = datetime.datetime.now().strftime('%B')
    response = requests.get(f'https://kinopoiskapiunofficial.tech/api/v2.2/films/premieres?year={year}&month={month}', headers=header)
    data = response.json()
    films = {}
    premiere = [year]
    for item in data['items']:
        if item['year'] in premiere:
            films[item['nameRu']] = {
                'year': item['year'],
                'genre': [item['genre'] for item in item['genres']],
                'link': item['posterUrlPreview']
            }

    return films
