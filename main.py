import logging
import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Импорт переменных
from owenClient import OwenApi
from settings import API_TOKEN
from keyboard import button_row
from settings import logger
from settings import URL_TO_GET_DATA

logger.info('Программа запущена, начинаем инициализацию')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

api = OwenApi(URL_TO_GET_DATA)
categories_list = api.getCategories()
devices_list = api.getListDevices()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    mess = 'Добро пожаловать.\n\nЯ бот для работы с owencloud api \n'
    mess += '/help Для справки'
    await message.answer(mess )


@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    """
    Вызов справки по работе с ботом
    :param message:
    :return:
    """
    logger.debug('Вызов общей справки', message.from_user.id)
    answer_messege = ''

    answer_messege += "Справка по работе с ботом\n"
    await message.answer(answer_messege, reply_markup=button_row)


def one_button(id, type, name):
    return {
        "id": id,
        "type": type,
        "name": name
    }

def fill_device(id):
    list = []
    for device in devices_list:
        if id in device['categories']:
            list.append(one_button(device["id"], 'd', device['name']))
    return list


def format_buttons(button_list, columns=2):
    builder_category = InlineKeyboardMarkup(row_width=columns)
    for i in range(len(button_list)):
        if button_list[i]['type'] == 'c':
            button1 = InlineKeyboardButton(
                text=f"Категория",
                callback_data=f'empty',
            )
            button2 = InlineKeyboardButton(
                text=button_list[i]['name'],
                callback_data=f'categories_{button_list[i]["id"]}',
            )
        else:
            button1 = InlineKeyboardButton(
                text=f"Устройство",
                callback_data=f'empty',
            )
            button2 = InlineKeyboardButton(
                text=button_list[i]['name'],
                callback_data=f'devices_{button_list[i]["id"]}'
            )
        if columns == 2:
            builder_category.insert(button1)
        builder_category.insert(button2)
    return builder_category


def show_categories(id=None):
    button_list = []
    answer_messege = 'Выберите категорию'

    if id is not None:
        for category in categories_list:
            if category["id"] == id:
                answer_messege = f"Категория: {category['name']}"
                for device in fill_device(category["id"]):
                    button_list.append(device)

    for category in categories_list:
        if id is None or id == category["parent_id"]:
            button_list.append(one_button(category["id"], 'c', category['name']))
            for device in fill_device(category["id"]):
                button_list.append(device)

    return answer_messege, format_buttons(button_list)


def show_devices():
    button_list = []
    answer_messege = 'Выберите устройство'

    for device in devices_list:
        button_list.append(one_button(device["id"], 'd', device['name']))

    return answer_messege, format_buttons(button_list, 1)


def parse_message(text):
    """
    Возвращает:
    0 - не известная команда
    1 - категория
    2 - устройство

    :param text:
    :return:
    """
    splited_text = text.split()
    if len(splited_text) > 0:
        if splited_text[0].find("/categories") >= 0:
            return 1
        if splited_text[0].find("/devices") >= 0:
            return 2
    return 0


def categories(text):
    text = text.split('_')
    id = None
    if len(text) > 1 and text[1] != '':
        id = int(text[1])

    answer_messege, builder = show_categories(id)
    return answer_messege, builder
    # pass


def show_device_param(id):
    device_param, params_keys, name = api.getDeviceParam(id)
    try:
        timestamp = device_param[0]['values'][0]['d']
        dt = datetime.datetime.fromtimestamp(timestamp)
        formatted_dt = dt.strftime("%H:%M:%S %d.%m.%Y")
    except:
        formatted_dt = ''
    answer_messege = f'для устройства {name} в {formatted_dt} получены следующие значения: \n\n'
    for param in device_param:
        answer_messege += f"{params_keys[param['id']]['name']}:  {param['values'][0]['f']} \n"
    return answer_messege


def devices(text):
    text = text.split('_')
    id = None
    if len(text) > 1 and text[1] != '':
        id = int(text[1])
        answer_messege = show_device_param(id)
        builder = None
    else:
        answer_messege, builder = show_devices()
    return answer_messege, builder


@dp.message_handler()
async def cmd_common(message: types.Message):
    rez = parse_message(message.text)
    answer_messege = ''
    if rez == 0:
        send_help(message)
    if rez == 1:
        answer_messege, builder = categories(message.text)
        await message.answer(answer_messege, reply_markup=builder)
    if rez == 2:
        answer_messege, builder = devices(message.text)
        await message.answer(answer_messege, reply_markup=builder)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('categories_'))
async def process_callback_categories(callback_query: types.CallbackQuery):
    answer_messege, builder = categories(callback_query.data)
    await callback_query.message.answer(answer_messege, reply_markup=builder)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('devices_'))
async def process_callback_categories(callback_query: types.CallbackQuery):
    answer_messege, builder = devices(callback_query.data)
    await callback_query.message.answer(answer_messege, reply_markup=builder, parse_mode='HTML')


@dp.callback_query_handler(lambda c: c.data == "process_callback_help")
async def process_callback_help(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Справка по работе с ботом", reply_markup=button_row)


logger.info('Запущен главный цикл')
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
