import os

from weather import get_weather, get_location
from currency import currency_search
from affiche import get_affiche
from random_film import genres, get_genre_id
from travel import get_info
from photo_to_text import get_text, tesseract_languages,translate_text
from openai_bot import chatting
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


TG_TOKEN = os.getenv('TG_TOKEN')

bot = Bot(token=TG_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

CHAT_ID = os.getenv('MY_CHAT_ID')


class States(StatesGroup):
    weather_state = State()
    travel_state = State()
    what_to_translate = State()
    origin_language = State()
    destiny_language = State()
    movie_state = State()


@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    try:
        os.remove('photo.jpg')
    except:
        pass
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add(KeyboardButton(text='Погода'),
                 KeyboardButton(text="Курс валют"),
                 KeyboardButton(text='Кино'),
                 KeyboardButton(text='Путешественник'),
                 KeyboardButton(text='Переводчик'),
                 KeyboardButton(text='Пока'))
    await bot.send_sticker(chat_id=message.from_user.id, sticker='CAACAgIAAxkBAAEH-HFkARnV5wkdyT2V3o8qm43UMwOOdwACQQcAAlwCZQM3_GOaGamGFS4E')
    await message.reply(f"Чем могу помочь, {message.from_user.first_name}?\nЛибо просто введи любое собщение", reply_markup=keyboard)
    if message.chat.id != int(CHAT_ID):
        await bot.send_message(chat_id=CHAT_ID, text=f'Пользователь: {message.from_user.full_name} Отправил: {message.text}')


@dp.message_handler(Text(equals='Пока', ignore_case=True))
async def bye_bye(message: types.Message):
    await bot.send_sticker(chat_id=message.from_user.id, sticker='CAACAgIAAxkBAAEH-IpkASFPD2VEx0fdZ4iYnRMtxGqMiwACKwcAAlwCZQMbbrLeM5xCri4E')
    if message.chat.id != int(CHAT_ID):
        await bot.send_message(chat_id=CHAT_ID,
                           text=f'Пользователь: {message.from_user.full_name} Отправил: {message.text}')


@dp.message_handler(Text(equals='Назад', ignore_case=True), state='*')
async def back(message: types.Message, state: FSMContext):
    await start(message, state)


@dp.message_handler(Text(equals="Погода", ignore_case=True))
async def weather(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text='Город в котором я нахожусь', request_location=True),
            types.KeyboardButton(text='Назад')
        ]
        ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await bot.send_sticker(chat_id=message.from_user.id, sticker='CAACAgIAAxkBAAEH-GtkARgeUkrxtUW1fzpDhU6PkFJDcQACigcAAlwCZQN5zcXUs8hYyC4E')
    await message.reply(f'Погода какого города тебя интересует, {message.from_user.first_name}?', reply_markup=keyboard)
    await States.weather_state.set()
    if message.chat.id != int(CHAT_ID):
        await bot.send_message(chat_id=CHAT_ID,
                           text=f'Пользователь: {message.from_user.full_name} Отправил: {message.text}')


@dp.message_handler(Text(equals="Переводчик", ignore_case=True))
async def translator(message: types.Message, state: FSMContext):
    kb = [
        [
            types.KeyboardButton(text='Назад')
        ]
        ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await bot.send_sticker(chat_id=message.from_user.id, sticker='CAACAgIAAxkBAAEH-IxkASHG65njFxcLzUQMuUsoNP2s0gACWhUAAu9g0Ut69TFc_JRHAS4E')
    await message.reply(f'Загрузи фото или текст, {message.from_user.first_name}', reply_markup=keyboard)
    await state.set_state(States.what_to_translate)
    if message.chat.id != int(CHAT_ID):
        await bot.send_message(chat_id=CHAT_ID,
                           text=f'Пользователь: {message.from_user.full_name} Отправил: {message.text}')


@dp.message_handler(state=States.what_to_translate, content_types=types.ContentTypes.ANY)
async def get_origin_language(message: types.ContentTypes.ANY, state=FSMContext):
    await state.update_data(to_be_translated=message.content_type)
    if message.text == 'Назад':
        await start(message, state)
    else:
        if message.content_type == "photo":
            await message.photo[-1].download('photo.jpg')
            async with state.proxy() as data:
                data['what_to_translate'] = message.content_type
        keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
        for language in tesseract_languages.keys():
            kb = InlineKeyboardButton(language, callback_data=language)
            keyboard.add(kb)
        async with state.proxy() as data:
            data['what_to_translate'] = message.content_type
            data['translate'] = message.text
            data['message'] = message
        await message.reply('Какой это язык?', reply_markup=keyboard)
        await state.set_state(States.origin_language)
        if message.chat.id != int(CHAT_ID):
            await bot.send_message(chat_id=CHAT_ID,
                               text=f'Пользователь: {message.from_user.full_name} Отправил: {message.text}')


@dp.callback_query_handler(lambda call: call.data in tesseract_languages.keys(), state=States.origin_language)
async def get_destiny_language(callback_query: types.CallbackQuery, state=FSMContext):
    await state.update_data(origin_language=callback_query.message.text)
    if callback_query.message.text == 'Назад':
        async with state.proxy() as data:
            message = data['message']
            await start(message, state)
    else:
        async with state.proxy() as data:
            data['origin_language'] = callback_query.data
        keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
        for language in tesseract_languages.keys():
            kb = InlineKeyboardButton(language, callback_data=language)
            keyboard.add(kb)
        await callback_query.message.reply('На какой язык перевести?', reply_markup=keyboard)
        await state.set_state(States.destiny_language)
        if callback_query.message.chat.id != int(CHAT_ID):
            await bot.send_message(chat_id=CHAT_ID,
                               text=f'Пользователь: {callback_query.message.from_user.full_name} Отправил: {callback_query.message.text}')


@dp.callback_query_handler(lambda call: call.data in tesseract_languages.keys(),state=States.destiny_language)
async def converter(callback_query: types.CallbackQuery, state=FSMContext):
    await state.update_data(destiny_language=callback_query.message.text)
    if callback_query.message.text == 'Назад':
        async with state.proxy() as data:
            message = data['message']
            await start(message, state)
    else:
        async with state.proxy() as data:
            data['destiny_language'] = callback_query.data
            what_to_translate = data['what_to_translate']
            origin_language = data['origin_language']
            destiny_language = data['destiny_language']
            to_translate = data['translate']
            message = data['message']

            if what_to_translate == 'photo':
                await callback_query.message.reply(get_text(origin_language, destiny_language))
                if callback_query.message.chat.id != int(CHAT_ID):
                    await bot.send_message(chat_id=CHAT_ID,
                                       text=f'Пользователь: {message.from_user.full_name} Отправил: {message.text}')
            if what_to_translate == 'text':
                await callback_query.message.reply(translate_text(to_translate, origin_language, destiny_language))
                if callback_query.message.chat.id != int(CHAT_ID):
                    await bot.send_message(chat_id=CHAT_ID,
                                       text=f'Пользователь: {message.from_user.full_name} Отправил: {message.text}')
            await start(message, state)


@dp.message_handler(Text(equals="Кино", ignore_case=True))
async def cinema(message: types.Message, state: FSMContext):
    await bot.send_sticker(chat_id=message.from_user.id, sticker='CAACAgIAAxkBAAEH-IBkAR3koUw5BAK6U3bgY0Gs1U_UAQACKRUAAviLwEupQBIzh-Q46C4E')
    kb = [
        [
            types.KeyboardButton(text='Афиша'),
            types.KeyboardButton(text='Случайный фильм'),
            types.KeyboardButton(text='Назад')
        ]
        ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.reply(f'Что именно тебя интересует, {message.from_user.first_name}?', reply_markup=keyboard)
    await state.set_state(States.movie_state)
    if message.chat.id != int(CHAT_ID):
        await bot.send_message(chat_id=CHAT_ID,
                           text=f'Пользователь: {message.from_user.full_name} Отправил: {message.text}')


@dp.message_handler(Text(equals='Случайный фильм', ignore_case=True), state=States.movie_state)
async def random_film(message: types.Message):
    film_genres = genres
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    for genre in film_genres.values():
        kb = InlineKeyboardButton(genre, callback_data=genre)
        keyboard.add(kb)
    await message.reply(f'Выбери жанр', reply_markup=keyboard)
    if message.chat.id != int(CHAT_ID):
        await bot.send_message(chat_id=CHAT_ID,
                           text=f'Пользователь: {message.from_user.full_name} Отправил: {message.text}')


@dp.callback_query_handler(lambda call: call.data in genres.values(), state=States.movie_state)
async def print_movie(callback_query: types.CallbackQuery, state: FSMContext):
    film = get_genre_id(callback_query.data)
    msg = f"Название: {film['name']}\nГод выпуска: {film['year']}\nРейтинг Imdb: {film['rating']}\nОписание: {film['description']}"
    await callback_query.message.reply_photo(film['poster'], msg)
    await start(callback_query.message, state)


@dp.message_handler(Text(equals='Афиша', ignore_case=True), state=States.movie_state)
async def movies(message: types.Message, state: FSMContext):
    films = get_affiche()
    for film in films:
        msg = f"{film} {films[film]['year']} {' '.join(films[film]['genre'])}"
        await message.reply_photo(films[film]['link'], msg)
    await start(message, state)
    if message.chat.id != int(CHAT_ID):
        await bot.send_message(chat_id=CHAT_ID,
                               text=f'Пользователь: {message.from_user.full_name} Отправил: {message.text}')


@dp.message_handler(Text(equals="Курс валют", ignore_case=True))
async def currency(message: types.Message):
    await bot.send_sticker(chat_id=message.from_user.id, sticker='CAACAgIAAxkBAAEH-HhkARpyoEQ0nfDH5T1C1u6hdl_uHAACFxIAApxi-UvT1057BWXc9C4E')
    await message.reply(currency_search())
    if message.chat.id != int(CHAT_ID):
        await bot.send_message(chat_id=CHAT_ID,
                           text=f'Пользователь: {message.from_user.full_name} Отправил: {message.text}')


@dp.message_handler(state=States.weather_state, content_types=[*types.ContentTypes.LOCATION, *types.ContentTypes.TEXT])
async def location(message: types.Message, state: FSMContext):
    await bot.send_sticker(chat_id=message.from_user.id, sticker='CAACAgIAAxkBAAEH-HpkARsCH5miVU6DEPtZA03k9TyiuwACuLcBAAFji0YM3WBNodaZx1wuBA')
    if message.content_type == "location":
        await state.update_data(location=message.location)
        await message.reply(get_weather(lat=message.location.latitude, lon=message.location.longitude))
        await start(message, state)
        if message.chat.id != int(CHAT_ID):
            await bot.send_message(chat_id=CHAT_ID,
                               text=f'Пользователь: {message.from_user.full_name} Отправил: {message.location}')
    else:
        await state.update_data(location=message.text)
        await message.reply(get_location(message.text))
        await start(message, state)
        if message.chat.id != int(CHAT_ID):
            await bot.send_message(chat_id=CHAT_ID,
                               text=f'Пользователь: {message.from_user.full_name} Отправил: {message.text}')


@dp.message_handler(Text(equals="путешественник", ignore_case=True))
async def find_city(message: types.Message):
    await bot.send_sticker(chat_id=message.from_user.id, sticker='CAACAgIAAxkBAAEH-IJkAR5CGWK1YlL2k_t6x5GovJ1AzgACJxgAApd54UvWARYS3sXfTy4E')
    await States.travel_state.set()
    kb = [
        [
            types.KeyboardButton(text='Назад')
        ]
        ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.reply(f"{message.from_user.first_name}, введи город или страну.\nДостопримечательности доступны не для всех городов и стран", reply_markup=keyboard)
    if message.chat.id != int(CHAT_ID):
        await bot.send_message(chat_id=CHAT_ID,
                           text=f'Пользователь: {message.from_user.full_name} Отправил: {message.text}')


@dp.message_handler(state=States.travel_state)
async def traveller(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    info = get_info(message.text)
    await message.reply(info)
    await start(message, state)
    if message.chat.id != int(CHAT_ID):
        await bot.send_message(chat_id=CHAT_ID,
                           text=f'Пользователь: {message.from_user.full_name} Отправил: {message.text}')


@dp.message_handler(content_types=['text'])
async def chat(message: types.Message):
    text = chatting(message.text)
    await message.answer(text)
    if message.chat.id != int(CHAT_ID):
        await bot.send_message(chat_id=CHAT_ID,
                           text=f'Пользователь: {message.from_user.full_name} Отправил: {message.text}\n'
                                f'Бот ответил: {text}')


if __name__ == "__main__":
    executor.start_polling(dp)
