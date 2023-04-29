import sqlite3 as sq
from uuid import uuid4

async def db_start():
    global db, cur

    db = sq.connect('tg_bot_debts.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS all_debts (id_debt TEXT PRIMARY KEY , user_id_recipient TEXT, "
                "name_debtor TEXT, login_debtor TEXT, debt_amount INTEGER, date_return TEXT)")
    db.commit()
    print('DB start')


async def create_debt(user_id_recipient, name_debtor, login_debtor, debt_amount, date_return) -> None:
    cur.execute("INSERT INTO all_debts VALUES(?, ?, ?, ?, ?, ?)",
                (str(uuid4()), user_id_recipient, name_debtor, login_debtor, debt_amount, date_return))
    db.commit()


async def get_user_debtors(user_id: str) -> list:
    return cur.execute(f"SELECT * FROM all_debts WHERE user_id_recipient == {user_id}").fetchall()