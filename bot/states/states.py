from aiogram.dispatcher.filters.state import StatesGroup, State

class MyDebtorsStatesGroup(StatesGroup):
    name_debtor = State()
    login_debtor = State()
    debt_amount = State()
    date_return = State()


class ChangeDebtStatesGroup(StatesGroup):
    login = State()
    change_amount_to_increase = State()
    change_amount_to_decrease = State()


class ApproveDebt(StatesGroup):
    login_recipient = State()
    approve = State()


class DisputeDebt(StatesGroup):
    login_recipient = State()
    text = State()


class HistoryDispute(StatesGroup):
    login = State()
    dispute_menu = State()
    new_mess = State()