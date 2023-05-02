from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def my_debots_ikb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Все мои должники', callback_data='all_debtors'),
         InlineKeyboardButton(text='Изменить должников', callback_data='change_debtors')],
        [InlineKeyboardButton(text='Статус долгов', callback_data='status_debts')],
        [InlineKeyboardButton(text='В главное меню', callback_data='cancel')]
    ], row_width=2)
    return ikb


def change_debots_ikb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Добавить нового должника', callback_data='new_debtor')],
         [InlineKeyboardButton(text='Изменить долг существующего', callback_data='change_a_debtor')],
        [InlineKeyboardButton(text='В главное меню', callback_data='cancel')]
    ], row_width=2)
    return ikb


def debt_editing_menu_ikb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Увеличить сумму долга', callback_data='increase_amount')],
        [InlineKeyboardButton(text='Уменьшить сумму долга', callback_data='decrease_amount')],
        [InlineKeyboardButton(text='Закрыть долг', callback_data='close_debt')],
        [InlineKeyboardButton(text='В главное меню', callback_data='cancel')]
    ], row_width=2)
    return ikb


def my_debts_menu() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Список всех долгов', callback_data='all_my_debts')],
        [InlineKeyboardButton(text='Подтвердить долг', callback_data='approve_debt'), InlineKeyboardButton(text='Оспорить долг', callback_data='dispute_debt')],
        [InlineKeyboardButton(text='История споров', callback_data='history_dispute')],
        [InlineKeyboardButton(text='В главное меню', callback_data='cancel')]
    ], row_width=2)
    return ikb