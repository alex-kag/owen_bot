from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

# =========================================================================

# button_help = KeyboardButton('/help')
# button_categories = KeyboardButton('/categories')
# button_devices = KeyboardButton('/devices')

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

# Затравка на будущее
# inline_btn_1 = InlineKeyboardButton('Первая кнопка!', callback_data='button1')
# inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)


# =========================================================================
