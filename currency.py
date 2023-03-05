import requests
import datetime
import xml.etree.ElementTree as ET


def currency_search():
    currency_dict = {}
    countries = {
        'R01035': {'emoji': '🇬🇧', 'sign': '£'},
        'R01090B': {'emoji': '🇧🇾', 'sign': 'Br'},
        "R01210": {'emoji': '🇬🇪', 'sign': '₾'},
        "R01230": {'emoji': '🇦🇪', 'sign': '	.د.إ'},
        "R01235": {'emoji': '🇺🇸', 'sign': '$'},
        "R01239": {'emoji': '🇪🇺', 'sign': '€'},
        "R01335": {'emoji': '🇰🇿', 'sign': '₸'},
        "R01375": {'emoji': '🇨🇳', 'sign': '¥'},
        "R01675": {'emoji': '🇹🇭', 'sign': '฿'},
        "R01700J": {'emoji': '🇹🇷', 'sign': '₺'},
        "R01720": {'emoji': '🇺🇦', 'sign': '₴'},
        "R01805F": {'emoji': '🇷🇸', 'sign': 'RSD'}

    }
    response = requests.get(f'http://www.cbr.ru/scripts/XML_daily.asp?date_req={datetime.datetime.now().strftime("%d-%m-%Y")}')
    root = ET.fromstring(response.content)
    for child in root:
        if child.attrib.values().mapping['ID'] in countries.keys():
            currency_dict[child.attrib.values().mapping['ID']] = {'Валюта': child[1].text,
                                                                  'Название': child[3].text,
                                                                  'Курс': child[4].text,
                                                                  'Номинал': child[2].text,
                                                                  }
    msg = ""
    for item in currency_dict:
        price = currency_dict[item]['Курс']
        price = price.replace(',','.')
        price = '{:.2f}'.format(float(price)/float(currency_dict[item]['Номинал']))
        msg += f"{countries[item]['emoji']}{currency_dict[item]['Название']}, Курс: 1{countries[item]['sign']} = {price}₽\n"

    return f"Курс валют на {datetime.datetime.now().strftime('%d-%m-%Y')}\n" + msg
