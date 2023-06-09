import sqlite3 as sq
from pprint import pprint
from uuid import uuid4
from datetime import date


async def db_start():
    global db, cur

    db = sq.connect('tg_bot_debts.db')
    cur = db.cursor()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS all_debts (id_debt TEXT PRIMARY KEY , user_id_recipient TEXT, login_recipient TEXT,"
        "name_debtor TEXT, login_debtor TEXT, debt_amount INTEGER, date_return TEXT, approve BOOLEAN, active BOOLEAN)")

    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY , login TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS history_dispute (id_dispute TEXT PRIMARY KEY , id_debt TEXT, text_dispute TEXT, type TEXT,\
     id_recipient TEXT, id_debtor TEXT, date TEXT, active BOOLEAN)")

    db.commit()
    print('DB start')


async def create_debt(user_id_recipient, login_recipient, name_debtor, login_debtor, debt_amount, date_return) -> None:
    cur.execute("INSERT INTO all_debts VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (str(uuid4()), user_id_recipient, login_recipient, name_debtor, login_debtor, debt_amount, date_return,
                 False, True))
    db.commit()


async def get_user_debtors(user_id: str) -> list:
    return cur.execute(f"SELECT * FROM all_debts WHERE user_id_recipient == '{user_id}' AND active == True").fetchall()


async def get_all_debtors_login(user_id: str) -> list:
    debtors_login = cur.execute(
        f"SELECT login_debtor FROM all_debts WHERE user_id_recipient == '{user_id}' AND active == True").fetchall()
    login_list = []
    for login in debtors_login:
        login_list.append(login[0])
    return login_list


async def get_recipient_debts(user_login: str):
    return cur.execute(f"SELECT * FROM all_debts WHERE login_debtor == '{user_login}' AND active == True").fetchall()


async def check_user_debt(user_login: str, user_id_recipient: str) -> bool:
    now = cur.execute(
        f"SELECT id_debt FROM all_debts WHERE login_debtor == '{user_login}' AND user_id_recipient == '{user_id_recipient}' AND active == True").fetchone()
    if now == None:
        return False
    return True


async def get_debt_amount_sql(user_login: str, id_recipient: str) -> int:
    return cur.execute(
        f"SELECT debt_amount FROM all_debts WHERE login_debtor == '{user_login}' AND user_id_recipient ='{id_recipient}' AND active == True").fetchone()[
        0]


async def update_user_debt(user_login: str, new_debt_amount: int, id_recipient: str) -> None:
    cur.execute(
        f"UPDATE all_debts SET debt_amount = '{new_debt_amount}' WHERE login_debtor = '{user_login}' AND user_id_recipient ='{id_recipient}' AND active == True")
    db.commit()


async def close_a_debt(user_login: str, id_recipient: str) -> None:
    debt_id = cur.execute(f"SELECT id_debt FROM all_debts WHERE login_debtor = '{user_login}' AND user_id_recipient ='{id_recipient}' AND active == True").fetchone()
    if debt_id != []:
        cur.execute(
            f"UPDATE history_dispute SET active = False WHERE id_debt == '{debt_id[0]}' ")
    cur.execute(
        f"UPDATE all_debts SET active = False WHERE login_debtor = '{user_login}' AND user_id_recipient ='{id_recipient}' AND active == True")


    db.commit()


async def check_user(user_id: str) -> tuple:
    return cur.execute(f"SELECT * FROM users WHERE user_id == '{user_id}'").fetchone()


async def add_new_user(user_id: str, user_login: str) -> None:
    cur.execute("INSERT INTO users VALUES(?, ?)", (user_id, user_login))
    db.commit()


async def update_user_login(user_id: str, user_login: str) -> None:
    cur.execute(f"UPDATE users SET login = '{user_login}' WHERE user_id = '{user_id}'")
    db.commit()


async def get_non_approve_debts(user_login: str) -> list:
    return cur.execute(
        f"SELECT * FROM all_debts WHERE login_debtor == '{user_login}' AND active == True AND approve == False").fetchall()


async def get_all_non_approve_recipient_login(user_login: str) -> list:
    debtors_login = cur.execute(
        f"SELECT login_recipient FROM all_debts WHERE login_debtor == '{user_login}' AND active == True AND approve == False").fetchall()
    login_list = []
    for login in debtors_login:
        login_list.append(login[0])
    return login_list


async def approve_debt(login_debt: str, login_recipient: str) -> None:
    cur.execute(
        f"UPDATE all_debts SET approve = True WHERE login_debtor = '{login_debt}' AND login_recipient = '{login_recipient}' AND active == True")
    db.commit()


async def create_dispute(id_debt: str, text: str, type: str, id_recipient: str, id_debtor: str) -> None:
    #Доработать время, сейчас всегда выводит время 00:00:00
    cur.execute("INSERT INTO history_dispute VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                (str(uuid4()), id_debt, text, type, id_recipient, id_debtor,
                 str(date.today().strftime('%Y-%m-%d %H:%M:%S')).replace('-', '.'), True))
    db.commit()


async def get_id_debt(login_r: str, login_debtor: str) -> str:
    return cur.execute(f"SELECT id_debt FROM all_debts WHERE login_recipient == '{login_r}' "
                       f"AND login_debtor == '{login_debtor}' "
                       f"AND active == True AND approve == False").fetchone()[0]


async def get_id_by_username(login: str) -> str:
    user_id = cur.execute(f"SELECT user_id FROM users WHERE login == '{login}' ").fetchone()
    if user_id == None:
        return ''
    return user_id[0]



async def get_dispute_by_debtor(debtor_id: str) -> list:
    return cur.execute(f"SELECT * FROM history_dispute WHERE id_debtor == '{debtor_id}' AND active == True").fetchall()


async def get_dispute_by_recipient(recipient_id: str) -> list:
    return cur.execute(f"SELECT * FROM history_dispute WHERE id_recipient == '{recipient_id}' AND active == True").fetchall()


async def get_name_debtor_in_dispute(debtor_id: str) -> list:
    hd_data = cur.execute(f"SELECT id_recipient FROM history_dispute WHERE id_debtor == '{debtor_id}' AND active == True").fetchall()
    recipients = [x[0] for x in hd_data]
    users = {}
    user_data = cur.execute(f"SELECT user_id, login FROM users").fetchall()
    for x, y in user_data:
        users[x] = y
    login_debtors = set()
    for r in recipients:
        login_debtors.add(users[r])
    return list(set(login_debtors))


async def get_full_history_dispute(debtor_id: str, recipient_id: str) -> dict:
    hd_data = cur.execute(
        f"SELECT text_dispute, type, date FROM history_dispute WHERE "
        f"id_debtor == '{debtor_id}' AND id_recipient == '{recipient_id}' AND active == True").fetchall()
    data = {}
    for i in range(len(hd_data)):
        data[i] = {
            'text': hd_data[i][0],
            'type': hd_data[i][1],
            'date': hd_data[i][2]
        }
    return data


async def get_all_dispute_data(user_login: str, debtor_id: str) -> dict:
    id_rec = cur.execute(f"SELECT user_id FROM users WHERE login == '{user_login}' ").fetchone()[0]
    hd_data = cur.execute(f"SELECT id_dispute, id_debt, id_recipient, id_debtor FROM history_dispute "
                          f"WHERE id_debtor == '{debtor_id}' AND id_recipient == '{id_rec}' AND active == True").fetchone()
    data = {
        'id_dispute': hd_data[0],
        'id_debt': hd_data[1],
        'id_recipient': hd_data[2],
        'id_debtor': hd_data[3]
    }
    return data

