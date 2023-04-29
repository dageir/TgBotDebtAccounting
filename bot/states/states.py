from aiogram.dispatcher.filters.state import StatesGroup, State

class MyDebtorsStatesGroup(StatesGroup):
    name_debtor = State()
    login_debtor = State()
    debt_amount = State()
    date_return = State()