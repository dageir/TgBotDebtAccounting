async def craete_text_format(text: list) -> str:
    st = ''
    for i in text:
        st += f'Имя должника: {i[3]}. Логин должника: @{i[4]}. ' \
              f'Сумма долга: {str(i[5])}. Плановая дата возврата: {i[6]}\n\n'
    return st

async def create_recipient_debts_data(text: list) -> str:
    if text == []:
        return 'Вы никому не должны!'
    st = 'Вы должны:\n\n'
    for i in text:
        st += f'@{i[2]} - {str(i[5])} рублей. Отдать надо до {i[6]}\n'
    return st

async def create_recipient_non_approve_debts_data(text: list) -> str:
    if text == []:
        return 'У вас нет неподтверждённых долгов!'
    st = 'Долги, которые ожидают подтверждения:\n\n'
    for i in text:
        st += f'@{i[2]} - {str(i[5])} рублей. Срок отдачи - {i[6]}\n'
    return st


async def create_status_debts_data(text: list) -> str:
    if text == []:
        return 'У вас нет должников!'
    st_0 = ''
    st_1 = ''

    for t in text:
        if t[7] == 0:
            st_0 +=f'@{t[2]} - {str(t[5])} рублей. Срок отдачи - {t[6]}\n'
        else:
            st_1 += f'@{t[2]} - {str(t[5])} рублей. Срок отдачи - {t[6]}\n'
    if st_0 == '':
        end_st = f'Подтверждённые долги:\n\n{st_1}'
    elif st_1 == '':
        end_st = f'Долги, ожидающие подтверждения:\n\n{st_0}'
    else:
        end_st = f'Долги, ожидающие подтверждения:\n\n{st_0}\n\nПодтверждённые долги:\n\n{st_1}'
    return end_st