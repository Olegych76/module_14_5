from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import re

from crud_functions import *

initiate_db()

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

# создаём первую клавиатуру
kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(KeyboardButton('Рассчитать'))
kb.insert(KeyboardButton('Информация'))
kb.add(KeyboardButton('Купить'))
kb.insert(KeyboardButton('Регистрация'))

class UserState(StatesGroup):
    # описываем необходимые нам состояния пользователя
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    # создаём инлайн клавиатуру
    kb2 = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
    kb2.add(button1)
    button2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
    kb2.insert(button2)
    await message.answer('Выберите опцию:', reply_markup=kb2)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    # выводим формулу Миффлина-Сан Жеора
    await call.message.answer('10 х вес (кг) + 6,25 х рост (в см) – 5 х возраст (г) + 5')
    await call.answer()


# ловим ключевое слово 'calories'
@dp.callback_query_handler(text='calories')
async def set_age(call):
    # Запрашиваем у пользователя возраст
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()
    await call.answer()


# ловим State.age
@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    # Получаем введенный возраст от пользователя
    age = message.text

    # Сохраняем введенный возраст в состоянии
    await state.update_data(age=age)

    # Запрашиваем у пользователя рост
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


# ловим State.growth
@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    # Получаем введенный рост от пользователя
    growth = message.text

    # Сохраняем введенный рост в состоянии
    await state.update_data(growth=growth)

    # Запрашиваем у пользователя вес
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


# ловим State.weight
@dp.message_handler(state=UserState.weight)
async def result_info(message, state):
    # Получаем введенный вес от пользователя
    weight = message.text

    # Получаем данные из состояния
    data = await state.get_data()
    age = data.get('age')
    growth = data.get('growth')

    # Выводим информацию
    result = 10 * int(weight) + 6.25 * int(growth) - 5 * int(age) + 5
    await message.answer(f'Ваша дневная норма калорий: {result}')

    # Сбрасываем состояние
    await state.finish()
    # Возвращаемся к меню с инлайн кнопками
    await main_menu(message)

# ловим команду /start
@dp.message_handler(commands=['start'])
async def start_message(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.'
                         'Если хочешь узнать свою суточную норму калорий, нажми кнопку "Рассчитать"',
                         reply_markup=kb)

# информация о боте
@dp.message_handler(text='Информация')
async def info_message(message):
    with open('img_5.png', 'rb') as img:
        await message.answer_photo(img, 'Лучшие БАДы - только у нас!', reply_markup=kb)

# купить
@dp.message_handler(text='Купить')
async def get_buying_list(message):
    # создаём инлайн клавиатуру для выбора продукта
    kb3 = InlineKeyboardMarkup(row_width=4)
    button1 = InlineKeyboardButton(text='Продукт 1', callback_data='product_buying')
    button2 = InlineKeyboardButton(text='Продукт 2', callback_data='product_buying')
    button3 = InlineKeyboardButton(text='Продукт 3', callback_data='product_buying')
    button4 = InlineKeyboardButton(text='Продукт 4', callback_data='product_buying')
    # добавляем все кнопки в одну строку
    kb3.add(button1, button2, button3, button4)

    products = get_all_products()

    for i in range(0, 4):
        with open(f'img_{i + 1}.png', 'rb') as img:
            await message.answer_photo(img, f'Название:{products[i][1]} | Описание:{products[i][2]} | Цена: {products[i][3]}')

    await message.answer('Выберите продукт для покупки:', reply_markup=kb3)

@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    # выводим сообщение о покупке
    await call.message.answer('Вы успешно приобрели продукт!', reply_markup=kb)
    await call.answer()

class RegistrationState(StatesGroup):
    # описываем необходимые нам состояния регистрации пользователя
    username = State()
    email = State()
    age = State()
    balance = State()

@dp.message_handler(text='Регистрация')
async def sing_up(message):
    await message.answer('Введите имя пользователя (только латинские символы):')
    await RegistrationState.username.set()

# ловим State.username
@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    # Обрабатываем введенное имя пользователя
    if not re.match(r'^[a-zA-Z]+$', message.text):
        await message.answer('Пожалуйста, используйте только латинские символы')
        return
    if is_included(message.text):
        await message.answer('Такой пользователь существует, введите другое имя')
        return
    else:
        await state.update_data(username=message.text)

    await message.answer('Введите свой e-mail:')
    await RegistrationState.email.set()

@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)

    await message.answer('Введите свой возраст:')
    await RegistrationState.age.set()

@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=message.text)

    data = await state.get_data()
    # добавляем новго пользователя в базу
    add_user(data.get('username'), data.get('email'), data.get('age'))
    # Сбрасываем состояние
    await state.finish()
    # Возвращаемся к основному меню
    await message.answer('Пользователь успешно зарегистрирован!', reply_markup=kb)


# ловим все (необработанные) сообшения
@dp.message_handler()
async def all_message(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
