from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

button_row = InlineKeyboardMarkup(row_width=1)
button = InlineKeyboardButton(
    text='Справка',
    callback_data='process_callback_help'
)
button_row.insert(button)
button = InlineKeyboardButton(
    text='Список категорий',
    callback_data='categories_'
)
button_row.insert(button)
button = InlineKeyboardButton(
    text='Список устройств',
    callback_data='devices_'
)
button_row.insert(button)

