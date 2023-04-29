async def craete_text_format(text: list) -> str:

    st = ''

    for i in text:
        st += f'Имя должника: {i[3]}. Логин должника: @{i[4]}. ' \
              f'Сумма долга: {str(i[5])}. Плановая дата возврата: {i[6]}\n\n'
    return st

async def create_recipient_debts_data(text: list) -> str:
    if text == []:
        st = 'Вы никому не должны!'

    else:
        st = 'Вы должны:\n\n'
        for i in text:
            st += f'@{i[2]} - {str(i[5])} рублей. Отдать надо до {i[6]}\n'

    return st
