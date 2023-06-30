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


logger.info('Программа запущена, начинаем инициализацию')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

api = OwenApi()
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
    mess = ''

    mess += "Справка по работе с ботом\n"
    await message.answer(mess, reply_markup=button_row)


def one_button(id, type, name):
    return {
        "id": id,
        "type": type,
        "name": name
    }

def fill_device(id):
    list = []
    for i in devices_list:
        if id in i['categories']:
            list.append(one_button(i["id"], 'd', i['name']))
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
    mess = 'Выберите категорию'

    if id is not None:
        for i in categories_list:
            if i["id"] == id:
                mess = f"Категория: {i['name']}"
                for j in fill_device(i["id"]):
                    button_list.append(j)

    for i in categories_list:
        if id is None or id == i["parent_id"]:
            button_list.append(one_button(i["id"], 'c', i['name']))
            for j in fill_device(i["id"]):
                button_list.append(j)

    return mess, format_buttons(button_list)


def show_devices():
    button_list = []
    mess = 'Выберите устройство'

    for i in devices_list:
        button_list.append(one_button(i["id"], 'd', i['name']))

    return mess, format_buttons(button_list, 1)


def parse_message(text):
    """
    Возвращает:
    0 - не известная команда
    1 - категория
    2 - устройство

    :param text:
    :return:
    """
    mess = text.split()
    if len(mess) > 0:
        if mess[0].find("/categories") >= 0:
            return 1
        if mess[0].find("/devices") >= 0:
            return 2
    return 0


def categories(text):
    text = text.split('_')
    id = None
    if len(text) > 1 and text[1] != '':
        id = int(text[1])

    mess, builder = show_categories(id)
    return mess, builder
    # pass


def show_device_param(id):
    device_param, params_keys, name = api.getDeviceParam(id)
    try:
        timestamp = device_param[0]['values'][0]['d']
        dt = datetime.datetime.fromtimestamp(timestamp)
        formatted_dt = dt.strftime("%H:%M:%S %d.%m.%Y")
    except:
        formatted_dt = ''
    mess = f'для устройства {name} в {formatted_dt} получены следующие значения: \n\n'
    for param in device_param:
        mess += f"{params_keys[param['id']]['name']}:  {param['values'][0]['f']} \n"
    return mess


def devices(text):
    text = text.split('_')
    id = None
    if len(text) > 1 and text[1] != '':
        id = int(text[1])
        mess = show_device_param(id)
        builder = None
    else:
        mess, builder = show_devices()
    return mess, builder


@dp.message_handler()
async def cmd_common(message: types.Message):
    rez = parse_message(message.text)
    mess = ''
    if rez == 0:
        send_help(message)
    if rez == 1:
        mess, builder = categories(message.text)
        await message.answer(mess, reply_markup=builder)
    if rez == 2:
        mess, builder = devices(message.text)
        await message.answer(mess, reply_markup=builder)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('categories_'))
async def process_callback_categories(callback_query: types.CallbackQuery):
    mess, builder = categories(callback_query.data)
    await callback_query.message.answer(mess, reply_markup=builder)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('devices_'))
async def process_callback_categories(callback_query: types.CallbackQuery):
    mess, builder = devices(callback_query.data)
    await callback_query.message.answer(mess, reply_markup=builder, parse_mode='HTML')


@dp.callback_query_handler(lambda c: c.data == "process_callback_help")
async def process_callback_help(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Справка по работе с ботом", reply_markup=button_row)


logger.info('Запущен главный цикл')
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
