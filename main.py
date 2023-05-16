from aiogram import Dispatcher, types, Bot, executor
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from bot.states import states
from config import TOKEN_API
from bot.keyboards import keyboards
from bot.keyboards import InlineKeyboards
from bot.db import sqlite
from bot.processors import text_processors


from bot.processors import main_processors


async def on_startup(_):
    await sqlite.db_start()
    print('Запустился')

storage = MemoryStorage()

bot = Bot(TOKEN_API)
dp = Dispatcher(bot=bot,
                storage=storage)


start_text = """
<b>Привет! 
Я бот, который поможет тебе следить за тем, отдают ли тебе деньги должники, 
а заодно не даст тебе забыть о своих долгах!</b>
"""


help_text = """
<b>/start</b> - <em>запустить бота</em>

<b>/my_debtors</b> - <em>откроет меню для отслеживания и редактирования ваших должников</em>

<b>/my_debts</b> - <em>откроет меню для работы с вашими долгами</em>

<b>/history_dispute</b> - <em>отобразит историю ваших споров</em>

<b>/cancel</b> - <em>даёт возможность из любого действия выйти в главное меню</em>
"""


@dp.message_handler(commands=['help'])
async def help_cmd(mess: types.Message) -> None:
    await mess.answer(text=help_text,
                      parse_mode='HTML')


@dp.message_handler(commands=['start'])
async def start_cmd(mess: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['check_user'] = await sqlite.check_user(mess.from_user.id)
    if await sqlite.check_user(mess.from_user.id) == None:
        await sqlite.add_new_user(mess.from_user.id, mess.from_user.username)
    elif data['check_user'][1] != mess.from_user.username:
        await sqlite.update_user_login(user_id=mess.from_user.id,
                                user_login=mess.from_user.username)
    await state.finish()

    await mess.answer(text=start_text,
                      parse_mode='HTML',
                      reply_markup=keyboards.main_keyboard())




@dp.message_handler(commands=['my_debtors'])
async def my_debtors_cmd(mess: types.Message) -> None:
    await mess.delete()
    await mess.answer(text='Выберите опцию',
                      reply_markup=ReplyKeyboardRemove())
    await bot.send_photo(photo='https://png.pngtree.com/png-clipart/20200322/ourlarge/pngtree-empty-wallet-illustration-png-image_2163566.jpg',
                         reply_markup=InlineKeyboards.my_debots_ikb(),
                         chat_id=mess.chat.id)


@dp.message_handler(commands=['my_debts'])
async def my_debtors_cmd(mess: types.Message) -> None:
    await mess.delete()
    await mess.answer(text='Выберите опцию',
                      reply_markup=ReplyKeyboardRemove())
    await bot.send_photo(chat_id=mess.chat.id,
                         photo='https://sun9-55.userapi.com/impg/c856020/v856020277/1730a3/rpXwBOU1GVc.jpg?size=604x604&quality=96&sign=0a49fd48f0705e1b6c23140db699de46&type=album',
                         reply_markup=InlineKeyboards.my_debts_menu())


@dp.message_handler(commands=['history_dispute'])
async def history_dispute_cmd(mess: types.Message) -> None:
    await mess.delete()
    await mess.answer(text='Выберите, с кем хотите просмотреть спор',
                      reply_markup=ReplyKeyboardRemove())
    await bot.send_photo(photo='https://4brain.ru/blog/wp-content/uploads/2020/05/v-spore-rozhdaetsya-istina.jpg',
                         reply_markup=InlineKeyboards.history_dispute_menu(),
                         chat_id=mess.chat.id)


@dp.callback_query_handler(Text(equals=['cancel', 'change_debtors', 'all_debtors', 'status_debts']))
async def callback_debtors_main(callback: types.CallbackQuery, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['data'] = await sqlite.get_user_debtors(callback.from_user.id)
        data['text'] = await text_processors.create_text_format(await sqlite.get_user_debtors(callback.from_user.id))

    if callback.data == 'cancel':
        await state.finish()
        await main_processors.delete_mess(callback=callback, type='callback')
        await callback.message.answer(text='Вы вернулись в главное меню',
                                      reply_markup=keyboards.main_keyboard())
    elif callback.data == 'all_debtors':
        if data['text'] == '':
            await callback.message.answer(text='У вас пока нет должников')
            await callback.answer()
        else:
            await callback.message.answer(text=data['text'])
            await callback.answer()
    elif callback.data == 'change_debtors':
        await state.finish()
        await main_processors.delete_mess(callback=callback, type='callback')
        await bot.send_photo(
            photo='https://kartinki.pibig.info/uploads/posts/2023-04/1681157639_kartinki-pibig-info-p-dolzhnik-kartinka-arti-vkontakte-2.jpg',
            reply_markup=InlineKeyboards.change_debots_ikb(),
            chat_id=callback.from_user.id)
    elif callback.data == 'status_debts':
        await callback.message.answer(text=await text_processors.create_status_debts_data(text=data['data']))
        await state.finish()
        await callback.answer()


@dp.message_handler(commands=['cancel'], state='*')
async def cansel_cmd(mess: types.Message, state: FSMContext):
    await state.finish()
    await main_processors.delete_mess(callback=mess)
    await mess.answer(text='Вы вернулись в главное меню',
                      reply_markup=keyboards.main_keyboard())


@dp.callback_query_handler(Text(equals=['new_debtor', 'change_a_debtor']))
async def add_change_debtor(callback: types.CallbackQuery) -> None:
    await main_processors.delete_mess(callback=callback, type='callback')
    if callback.data == 'new_debtor':
        await states.MyDebtorsStatesGroup.name_debtor.set()
        await callback.message.answer(text='Введите имя должника',
                                      reply_markup=keyboards.cancel_keyboard())
    else:
        await states.ChangeDebtStatesGroup.login.set()
        await callback.message.answer(text='Введите логин должника',
                                      reply_markup=keyboards.cancel_keyboard())
        await callback.answer()


@dp.message_handler(state=states.ChangeDebtStatesGroup.login)
async def debt_editing_menu(mess: types.Message, state: FSMContext) -> None:
    if await sqlite.check_user_debt(mess.text, mess.from_user.id) == True:
        async with state.proxy() as data:
            data['login'] = mess.text
        await bot.send_photo(
            photo='https://kartinki.pibig.info/uploads/posts/2023-04/1681157639_kartinki-pibig-info-p-dolzhnik-kartinka-arti-vkontakte-2.jpg',
            reply_markup=InlineKeyboards.debt_editing_menu_ikb(),
            chat_id=mess.from_user.id)
    else:
        await mess.answer(text='Такого должника не существует, проверьте корректность введённых данных')


@dp.callback_query_handler(Text(equals=['increase_amount', 'decrease_amount', 'close_debt']), state=states.ChangeDebtStatesGroup.login)
async def var_change_debt(callback: types.CallbackQuery,state: FSMContext) -> None:
    async with state.proxy() as data:
        pass
    await main_processors.delete_mess(callback=callback, type='callback')
    if callback.data == 'increase_amount':
        await states.ChangeDebtStatesGroup.change_amount_to_increase.set()
        await callback.message.answer(text='Введите сумму, на которую надо увеличить долг')
        await callback.answer()
    elif callback.data == 'decrease_amount':
        await states.ChangeDebtStatesGroup.change_amount_to_decrease.set()
        await callback.message.answer(text='Введите сумму, на которую надо уменьшить долг')
        await callback.answer()
    else:
        await sqlite.close_a_debt(data['login'], callback.from_user.id)
        await callback.message.answer(text='Долг успешно закрыт',
                                      reply_markup=InlineKeyboards.my_debots_ikb())
        await callback.answer()
        await state.finish()


@dp.message_handler(lambda mess: not mess.text.isdigit(), state=[states.ChangeDebtStatesGroup.change_amount_to_increase,states.ChangeDebtStatesGroup.change_amount_to_decrease])
async def non_integer_amount(mess: types.Message) -> None:
    await mess.answer(text='Введите число!')


@dp.message_handler(state=states.ChangeDebtStatesGroup.change_amount_to_increase)
async def increase_a_debt(mess: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['amount'] = int(mess.text)
        data['old_amount'] = await sqlite.get_debt_amount_sql(user_login=data['login'],
                                                       id_recipient=mess.from_user.id)
        data['new_amount'] = data['old_amount'] + data['amount']
    await sqlite.update_user_debt(data['login'], data['new_amount'], mess.from_user.id)
    await mess.answer(text='Долг был успешно увеличен',
                      reply_markup=InlineKeyboards.my_debots_ikb())
    await state.finish()


@dp.message_handler(state=states.ChangeDebtStatesGroup.change_amount_to_decrease)
async def decrease_a_debt(mess: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['amount'] = int(mess.text)
        data['old_amount'] = await sqlite.get_debt_amount_sql(user_login=data['login'],
                                                       id_recipient=mess.from_user.id)
        data['new_amount'] = data['old_amount'] - data['amount']
    if data['new_amount'] <= 0:
        await sqlite.close_a_debt(data['login'], mess.from_user.id)
        await mess.answer(text='Долг стал равен нулю (или меньше), поэтому был закрыт',
                          reply_markup=InlineKeyboards.my_debots_ikb())
    else:
        await sqlite.update_user_debt(data['login'], data['new_amount'], mess.from_user.id)
        await mess.answer(text='Долг был успешно уменьшен',
                          reply_markup=InlineKeyboards.my_debots_ikb())
    await state.finish()


@dp.message_handler(state=states.MyDebtorsStatesGroup.name_debtor)
async def get_name_debtor(mess: types.Message, state: FSMContext):
    if mess.text.isalpha():
        async with state.proxy() as data:
            data['name_debtor'] = mess.text
        await states.MyDebtorsStatesGroup.next()
        await mess.answer('Введите логин телеграмм должника без @')
    else:
        await mess.answer(text='Введите корректное имя!')


@dp.message_handler(state=states.MyDebtorsStatesGroup.login_debtor)
async def get_login_debtor(mess: types.Message, state: FSMContext):
    if mess.text in await sqlite.get_all_debtors_login(mess.from_user.id):
        await mess.answer('Данный должник уже существует, отредактируйте текущий долг',
                          reply_markup=InlineKeyboards.change_debots_ikb())
        await state.finish()
    else:
        async with state.proxy() as data:
            data['login_debtor'] = mess.text
        await states.MyDebtorsStatesGroup.next()
        await mess.answer('Введите сумму долга')


@dp.message_handler(lambda mess: not mess.text.isdigit(),
                    state=states.MyDebtorsStatesGroup.debt_amount)
async def get_debt_amount(mess: types.Message):
    await mess.answer('Введите число!')


@dp.message_handler(state=states.MyDebtorsStatesGroup.debt_amount)
async def get_debt_amount(mess: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['debt_amount'] = mess.text
    await states.MyDebtorsStatesGroup.next()
    await mess.answer('Введите плановую дату возврата долга')


@dp.message_handler(state=states.MyDebtorsStatesGroup.date_return)
async def get_date_return(mess: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['date_return'] = mess.text
    await sqlite.create_debt(mess.from_user.id, mess.from_user.username, data['name_debtor'], data['login_debtor'],
                      data['debt_amount'], data['date_return'])
    await mess.answer(text='Долг сохранён',
                      reply_markup=InlineKeyboards.my_debots_ikb())
    await state.finish()


@dp.callback_query_handler(Text(equals=['all_my_debts', 'approve_debt', 'dispute_debt', 'history_dispute']))
async def my_debts_ikb_menu(callback: types.CallbackQuery, state: FSMContext) -> None:
    if callback.data == 'all_my_debts':
        await callback.message.answer(text=await text_processors.create_recipient_debts_data(
            await sqlite.get_recipient_debts(callback.from_user.username)))
        await callback.answer()
    elif callback.data == 'approve_debt':
        async with state.proxy() as data:
            data['check'] = await sqlite.get_non_approve_debts(callback.from_user.username)
        if data['check'] == []:
            await callback.message.answer(text=await text_processors.create_recipient_non_approve_debts_data(data['check']))
            await state.finish()
            await callback.answer()
        else:
            await main_processors.delete_mess(callback=callback, type='callback')
            await callback.message.answer(text=await text_processors.create_recipient_non_approve_debts_data(data['check']))
            await callback.message.answer(text='Введите логин того, чей долг хотите подтвердить',
                                      reply_markup=keyboards.cancel_keyboard())
            await states.ApproveDebt.login_recipient.set()
            await callback.answer()
    elif callback.data == 'dispute_debt':
        async with state.proxy() as data:
            data['check'] = await sqlite.get_non_approve_debts(callback.from_user.username)
        if data['check'] == []:
            await callback.message.answer(text=await text_processors.create_recipient_non_approve_debts_data(data['check']))
            await callback.answer()
        else:
            await callback.message.answer(text=await text_processors.create_recipient_non_approve_debts_data(data['check']))
            await callback.message.answer(text='<b>Введите логин того (без @), чей долг хотите оспорить </b><em>('
                                               'можно оспорить только тот долг, который вы ещё не подтвердили)</em>',
                                          parse_mode='HTML',
                                          reply_markup=keyboards.cancel_keyboard())
            await main_processors.delete_mess(callback=callback, type='callback')
            await states.DisputeDebt.login_recipient.set()
    elif callback.data == 'history_dispute':
        await callback.answer(text='Будет доступно позже')


@dp.message_handler(state=states.DisputeDebt.login_recipient)
async def get_login_recipient_for_dispute(mess: types.Message, state: FSMContext) -> None:
    if mess.text in await sqlite.get_all_non_approve_recipient_login(mess.from_user.username):
        async with state.proxy() as data:
            data['login_r'] = mess.text
            data['id_debt'] = await sqlite.get_id_debt(login_r=data['login_r'], login_debtor=mess.from_user.username)
        await states.DisputeDebt.text.set()
        await mess.answer('Введите комментарий к спору (почему вы не согласны с данным долгом)')
    else:
        await mess.answer('Долгов по данному логину нет, проверьте ещё раз список долгов')
        await mess.answer(text=await text_processors.create_recipient_non_approve_debts_data(
            await sqlite.get_non_approve_debts(mess.from_user.username)))


@dp.message_handler(state=states.DisputeDebt.text)
async def get_text_for_dispute(mess: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['text'] = mess.text
        data['id_recipient'] = await sqlite.get_id_by_username(login=data['login_r'])
    await sqlite.create_dispute(id_debt=data['id_debt'], text=data['text'], type='debtor',
                         id_recipient=data['id_recipient'], id_debtor=mess.from_user.id)
    await state.finish()
    await mess.answer(text='Спор был успешно создан, можете проверить его в меню всех споров',
                      reply_markup=keyboards.main_keyboard())


@dp.message_handler(state=states.ApproveDebt.login_recipient)
async def get_login_to_approve(mess: types.Message, state: FSMContext) -> None:
    if mess.text.startswith('@'):
        await mess.answer('Введите логин без "@"')
    else:
        if mess.text in await sqlite.get_all_non_approve_recipient_login(mess.from_user.username):
            async with state.proxy() as data:
                data['login_r'] = mess.text
            await states.ApproveDebt.approve.set()
            await mess.answer('Вы уверены, что хотите подтвердить долг? \nДанное действие нельзя будет отменить \nНапишите "Да" или "Нет"')
        else:
            await mess.answer('Долгов по данному логину нет, проверьте ещё раз список долгов')
            await mess.answer(text=await text_processors.create_recipient_non_approve_debts_data(
                await sqlite.get_non_approve_debts(mess.from_user.username)))


@dp.message_handler(state=states.ApproveDebt.approve)
async def get_approve_on_debt(mess: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        pass
    if mess.text == 'Да':
        await sqlite.approve_debt(login_debt=mess.from_user.username,
                           login_recipient=data['login_r'])
        await state.finish()
        await mess.answer(text='Долг успешно подтверждён',
                          reply_markup=keyboards.main_keyboard())
    elif mess.text == 'Нет':
        await state.finish()
        await mess.answer(text='Долг не был подтверждён',
                          reply_markup=keyboards.main_keyboard())
    else:
        await mess.answer('Напишите "Да" или "Нет"!')


@dp.callback_query_handler(Text(equals=['dispute_my_debts', 'dispute_with_debtors']))
async def history_dispute_ikb_menu(callback: types.CallbackQuery, state: FSMContext) -> None:
    if callback.data == 'dispute_my_debts':
        async with state.proxy() as data:
            data['rec'] = await sqlite.get_name_debtor_in_dispute(callback.from_user.id)
        if data['rec'] == []:
            await callback.message.answer(text='Вы не открывали споров')
        else:
            await callback.message.answer(text='Введите логин того, с кем у вас открыт сейчас спор',
                                          reply_markup=keyboards.cancel_keyboard())
            await callback.message.answer(text=await text_processors.create_all_rec_dispute_data(data['rec']))
            await main_processors.delete_mess(callback=callback, type='callback')
            await states.HistoryDispute.login.set()
        await callback.answer()
    elif callback.data == 'dispute_with_debtors':
        await callback.answer('Будет доступно позже')


@dp.message_handler(state=states.HistoryDispute.login)
async def dispute_my_debts(mess: types.Message, state:FSMContext) -> None:
    async with state.proxy() as data:
        data['login_r'] = mess.text
        data['id_rec'] = await sqlite.get_id_by_username(data['login_r'])
    if data['login_r'] not in data['rec']:
        await mess.answer('У вас нет открытого спора с этим пользователем, введите повторно')
        await mess.answer(text=await text_processors.create_all_rec_dispute_data(data['rec']))
    else:
        async with state.proxy() as data:
            data['all_dispute'] = await sqlite.get_all_dispute_data(data['login_r'], mess.from_user.id)
        await states.HistoryDispute.dispute_menu.set()
        await mess.answer(text='Выберите опцию',
                          reply_markup=ReplyKeyboardRemove())
        await bot.send_photo(photo='https://4brain.ru/blog/wp-content/uploads/2020/05/v-spore-rozhdaetsya-istina.jpg',
                             reply_markup=InlineKeyboards.dispute_menu(),
                             chat_id=mess.chat.id)



@dp.callback_query_handler(Text(equals=['mess_histoty', 'new_mess', 'approve_debt_by_dispute']),
                           state=states.HistoryDispute.dispute_menu)
async def dispute_menu(callback: types.CallbackQuery, state:FSMContext) -> None:
    async with state.proxy() as data:
        pass
    if callback.data == 'mess_histoty':
        await callback.message.answer(text=await text_processors.create_history_dispute(
            data=await sqlite.get_full_history_dispute(debtor_id=callback.from_user.id,
                                                       recipient_id=data['id_rec']),
            login_r=data['login_r'],
            login_d=callback.from_user.username
        ),
                          parse_mode='HTML')
        await callback.answer()
    elif callback.data == 'new_mess':
        await callback.message.answer('Напишите текст нового сообщения')
        await states.HistoryDispute.new_mess.set()
    elif callback.data == 'approve_debt_by_dispute':
        await callback.answer('Будет доступно позже')


@dp.message_handler(state=states.HistoryDispute.new_mess)
async def new_mess_in_dispute(mess: types.Message, state:FSMContext) -> None:
    async with state.proxy() as data:
        pass
    await sqlite.create_dispute(id_debt=data['all_dispute']['id_debt'], text=mess.text, type='debtor',
                                id_recipient=data['id_rec'], id_debtor=mess.from_user.id)
    await state.finish()
    await mess.answer(text='Спор дополнен',
                      reply_markup=keyboards.main_keyboard())


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp,
                           skip_updates=True,
                           on_startup=on_startup)