from pytesseract import pytesseract
from PIL import Image
import os
from googletrans import Translator

tesseract_languages = {
    'Русский': 'rus',
    'Английский': 'eng',
    'Немецкий': 'deu',
    'Казахский': 'kaz',
    'Испанский': 'spa',
    'Французский': 'frm',
    'Итальянский': 'ita',
    'Сербский': 'srp',
}

translate_languages = {
    'Английский': 'en',
    'Французский': 'fr',
    'Немецкий': 'de',
    'Итальянский': 'it',
    'Казахский': 'kk',
    'Русский': 'ru',
    'Сербский': 'sr',
    'Испанский': 'es',
}


def get_text(origin_language, destiny_language):
    origin_lang = tesseract_languages[origin_language]
    path = r'/opt/homebrew/Cellar/tesseract/5.3.0_1/bin/tesseract'
    pytesseract.tesseract_cmd = path
    image = Image.open('photo.jpg')
    text = pytesseract.image_to_string(image, lang=origin_lang)
    try:
        os.remove('photo.jpg')
    except:
        pass
    return translate_text(text, origin_language, destiny_language)


def translate_text(text, origin_language, destiny_language):
    origin_lang = translate_languages[origin_language]
    destiny_lang = translate_languages[destiny_language]
    translator = Translator()
    translation = translator.translate(text=text, src=origin_lang, dest=destiny_lang)
    return translation.text
