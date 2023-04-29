from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton('/my_debtors'), KeyboardButton('/my_debts')]
    ], resize_keyboard=True
    )
    return kb
