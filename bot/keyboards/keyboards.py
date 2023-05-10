from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton('/my_debtors'), KeyboardButton('/my_debts')],
        [KeyboardButton('/history_dispute')]
    ], resize_keyboard=True
    )
    return kb

def cancel_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton('/cancel')]
    ], resize_keyboard=True
    )
    return kb