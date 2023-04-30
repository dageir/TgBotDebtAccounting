import sqlite3 as sq
from uuid import uuid4

async def db_start():
    global db, cur

    db = sq.connect('tg_bot_debts.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS all_debts (id_debt TEXT PRIMARY KEY , user_id_recipient TEXT, login_recipient TEXT,"
                "name_debtor TEXT, login_debtor TEXT, debt_amount INTEGER, date_return TEXT)")
    db.commit()
    print('DB start')


async def create_debt(user_id_recipient, login_recipient, name_debtor, login_debtor, debt_amount, date_return) -> None:
    cur.execute("INSERT INTO all_debts VALUES(?, ?, ?, ?, ?, ?, ?)",
                (str(uuid4()), user_id_recipient, login_recipient,  name_debtor, login_debtor, debt_amount, date_return))
    db.commit()


async def get_user_debtors(user_id: str) -> list:
    return cur.execute(f"SELECT * FROM all_debts WHERE user_id_recipient == {user_id}").fetchall()


async def get_all_debtors_login(user_id: str) -> list:
    debtors_login = cur.execute(f'SELECT login_debtor FROM all_debts WHERE user_id_recipient == {user_id}').fetchall()
    login_list = []
    for login in debtors_login:
        login_list.append(login[0])
    return login_list


async def get_recipient_debts(user_login: str):
    return cur.execute(f"SELECT * FROM all_debts WHERE login_debtor == '{user_login}'").fetchall()


async def check_user_debt(user_login: str, user_id_recipient: str) -> bool:
    now = cur.execute(f"SELECT id_debt FROM all_debts WHERE login_debtor == '{user_login}' AND user_id_recipient == '{user_id_recipient}'").fetchone()
    if now == None:
        return False
    return True


async def update_user_debt(user_login: str, new_debt_amount: int):
    cur.execute(f"UPDATE all_debts SET debt_amount = debt_amount + '{new_debt_amount}' WHERE login_debtor = '{user_login}'")
    db.commit()


