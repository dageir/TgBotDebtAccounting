from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def my_debots_kb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Все мои должники', callback_data='all_debtors'),
         InlineKeyboardButton(text='Добавить/убрать должника', callback_data='change_debtors')],
        [InlineKeyboardButton(text='Назад', callback_data='cancel')]
    ], row_width=2)
    return ikb