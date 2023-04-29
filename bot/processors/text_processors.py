async def craete_text_format(text: list) -> str:

    st = ''

    for i in text:
        st += f'Имя должника: {i[2]}. Логин должника: @{i[3]}. ' \
              f'Сумма долга: {str(i[4])}. Плановая дата возврата: {i[5]}\n\n'
    return st