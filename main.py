from aiogram import Dispatcher, types, Bot, executor
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from config import TOKEN_API
from bot.keyboards.keyboards import main_keyboard, cancel_keyboard
from bot.keyboards.InlineKeyboards import my_debots_ikb, change_debots_ikb, debt_editing_menu_ikb, my_debts_menu
from bot.states.states import MyDebtorsStatesGroup, ChangeDebtStatesGroup, ApproveDebt, DisputeDebt
from bot.db.sqlite import db_start, create_debt, get_user_debtors, get_all_debtors_login, get_recipient_debts, \
    check_user_debt, get_debt_amount_sql, update_user_debt, delete_a_debt, add_new_user, check_user, update_user_login, \
    get_non_approve_debts, get_all_non_approve_recipient_login, approve_debt, get_id_debt, create_dispute, \
    get_id_by_username

from bot.processors.text_processors import craete_text_format, create_recipient_debts_data, \
    create_recipient_non_approve_debts_data, create_status_debts_data


async def on_startup(_):
    await db_start()
    print('Запустился')

storage = MemoryStorage()

bot = Bot(TOKEN_API)
dp = Dispatcher(bot=bot,
                storage=storage)


start_text = """
<b>Привет! 
Я бот, который поможет тебе следить за тем, отдают ли тебе деньги должники, а заодно не даст тебе забыть о своих долгах!</b>
"""


help_text = """
<b>/start</b> - <em>запустить бота</em>
<b>/my_debtors</b> - <em>откроет меню для отслеживания и редактирования ваших должников</em>
<b>/my_debts</b> - <em>покажет ваши долги</em>
<b>/cancel</b> - <em>даёт возможность из любого действия выйти в главное меню</em>
"""


@dp.message_handler(commands=['help'])
async def help_cmd(mess: types.Message) -> None:
    await mess.answer(text=help_text,
                      parse_mode='HTML')


@dp.message_handler(commands=['start'])
async def start_cmd(mess: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['check_user'] = await check_user(mess.from_user.id)
    if await check_user(mess.from_user.id) == None:
        await add_new_user(mess.from_user.id, mess.from_user.username)
    elif data['check_user'][1] != mess.from_user.username:
        await update_user_login(user_id=mess.from_user.id,
                                user_login=mess.from_user.username)
    await state.finish()

    await mess.answer(text=start_text,
                      parse_mode='HTML',
                      reply_markup=main_keyboard())


@dp.message_handler(commands=['my_debtors'])
async def my_debtors_cmd(mess: types.Message) -> None:
    await mess.delete()
    await mess.answer(text='Выберите опцию',
                      reply_markup=ReplyKeyboardRemove())
    await bot.send_photo(photo='https://png.pngtree.com/png-clipart/20200322/ourlarge/pngtree-empty-wallet-illustration-png-image_2163566.jpg',
                         reply_markup=my_debots_ikb(),
                         chat_id=mess.chat.id)


@dp.message_handler(commands=['my_debts'])
async def my_debtors_cmd(mess: types.Message) -> None:
    await mess.delete()
    await bot.send_photo(chat_id=mess.chat.id,
                         photo='https://sun9-55.userapi.com/impg/c856020/v856020277/1730a3/rpXwBOU1GVc.jpg?size=604x604&quality=96&sign=0a49fd48f0705e1b6c23140db699de46&type=album',
                         reply_markup=my_debts_menu())


@dp.callback_query_handler(Text(equals=['cancel', 'change_debtors', 'all_debtors', 'status_debts']))
async def callback_debtors_main(callback: types.CallbackQuery, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['data'] = await get_user_debtors(callback.from_user.id)
        data['text'] = await craete_text_format(await get_user_debtors(callback.from_user.id))

    if callback.data == 'cancel':
        await state.finish()
        await bot.delete_message(chat_id=callback.from_user.id,
                                 message_id=callback.message.message_id)
        await callback.message.answer(text='Вы вернулись в главное меню',
                                      reply_markup=main_keyboard())
    elif callback.data == 'all_debtors':
        if data['text'] == '':
            await callback.message.answer(text='У вас пока нет должников')
            await callback.answer()
        else:
            await callback.message.answer(text=data['text'])
            await callback.answer()
    elif callback.data == 'change_debtors':
        await state.finish()
        await bot.delete_message(chat_id=callback.from_user.id,
                                 message_id=callback.message.message_id)
        await bot.send_photo(
            photo='https://kartinki.pibig.info/uploads/posts/2023-04/1681157639_kartinki-pibig-info-p-dolzhnik-kartinka-arti-vkontakte-2.jpg',
            reply_markup=change_debots_ikb(),
            chat_id=callback.from_user.id)
    elif callback.data == 'status_debts':
        await callback.message.answer(text=await create_status_debts_data(text=data['data']))
        await state.finish()
        await callback.answer()

@dp.message_handler(commands=['cancel'], state='*')
async def cansel_cmd(mess: types.Message, state: FSMContext):
    await state.finish()
    await bot.delete_message(chat_id=mess.from_user.id,
                             message_id=mess.message_id)
    await mess.answer(text='Вы вернулись в главное меню',
                      reply_markup=main_keyboard())



@dp.callback_query_handler(Text(equals=['new_debtor', 'change_a_debtor']))
async def add_change_debtor(callback: types.CallbackQuery) -> None:
    await bot.delete_message(chat_id=callback.from_user.id,
                             message_id=callback.message.message_id)
    if callback.data == 'new_debtor':
        await MyDebtorsStatesGroup.name_debtor.set()
        await callback.message.answer(text='Введите имя должника',
                                      reply_markup=cancel_keyboard())
    else:
        await ChangeDebtStatesGroup.login.set()
        await callback.message.answer(text='Введите логин должника',
                                      reply_markup=cancel_keyboard())
        await callback.answer()


@dp.message_handler(state=ChangeDebtStatesGroup.login)
async def debt_editing_menu(mess: types.Message, state: FSMContext) -> None:
    if await check_user_debt(mess.text, mess.from_user.id) == True:
        async with state.proxy() as data:
            data['login'] = mess.text
        await bot.send_photo(
            photo='https://kartinki.pibig.info/uploads/posts/2023-04/1681157639_kartinki-pibig-info-p-dolzhnik-kartinka-arti-vkontakte-2.jpg',
            reply_markup=debt_editing_menu_ikb(),
            chat_id=mess.from_user.id)
    else:
        await mess.answer(text='Такого должника не существует, проверьте корректность введённых данных')


@dp.callback_query_handler(Text(equals=['increase_amount', 'decrease_amount', 'close_debt']), state=ChangeDebtStatesGroup.login)
async def var_change_debt(callback: types.CallbackQuery,state: FSMContext) -> None:
    async with state.proxy() as data:
        pass
    await bot.delete_message(chat_id=callback.from_user.id,
                             message_id=callback.message.message_id)
    if callback.data == 'increase_amount':
        await ChangeDebtStatesGroup.change_amount_to_increase.set()
        await callback.message.answer(text='Введите сумму, на которую надо увеличить долг')
        await callback.answer()
    elif callback.data == 'decrease_amount':
        await ChangeDebtStatesGroup.change_amount_to_decrease.set()
        await callback.message.answer(text='Введите сумму, на которую надо уменьшить долг')
        await callback.answer()
    else:
        await delete_a_debt(data['login'], callback.from_user.id)
        await callback.message.answer(text='Долг успешно закрыт',
                                      reply_markup=my_debots_ikb())
        await callback.answer()
        await state.finish()


@dp.message_handler(lambda mess: not mess.text.isdigit(), state=[ChangeDebtStatesGroup.change_amount_to_increase,ChangeDebtStatesGroup.change_amount_to_decrease])
async def non_integer_amount(mess: types.Message) -> None:
    await mess.answer(text='Введите число!')


@dp.message_handler(state=ChangeDebtStatesGroup.change_amount_to_increase)
async def increase_a_debt(mess: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['amount'] = int(mess.text)
        data['old_amount'] = await get_debt_amount_sql(user_login=data['login'],
                                                       id_recipient=mess.from_user.id)
        data['new_amount'] = data['old_amount'] + data['amount']
    await update_user_debt(data['login'], data['new_amount'], mess.from_user.id)
    await mess.answer(text='Долг был успешно увеличен',
                      reply_markup=my_debots_ikb())
    await state.finish()


@dp.message_handler(state=ChangeDebtStatesGroup.change_amount_to_decrease)
async def decrease_a_debt(mess: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['amount'] = int(mess.text)
        data['old_amount'] = await get_debt_amount_sql(user_login=data['login'],
                                                       id_recipient=mess.from_user.id)
        data['new_amount'] = data['old_amount'] - data['amount']
    if data['new_amount'] <= 0:
        await delete_a_debt(data['login'], mess.from_user.id)
        await mess.answer(text='Долг стал равен нулю (или меньше), поэтому был закрыт',
                          reply_markup=my_debots_ikb())
    else:
        await update_user_debt(data['login'], data['new_amount'], mess.from_user.id)
        await mess.answer(text='Долг был успешно уменьшен',
                          reply_markup=my_debots_ikb())
    await state.finish()


@dp.message_handler(state=MyDebtorsStatesGroup.name_debtor)
async def get_name_debtor(mess: types.Message, state: FSMContext):
    if mess.text.isalpha():
        async with state.proxy() as data:
            data['name_debtor'] = mess.text
        await MyDebtorsStatesGroup.next()
        await mess.answer('Введите логин телеграмм должника без @')
    else:
        await mess.answer(text='Введите корректное имя!')


@dp.message_handler(state=MyDebtorsStatesGroup.login_debtor)
async def get_login_debtor(mess: types.Message, state: FSMContext):
    if mess.text in await get_all_debtors_login(mess.from_user.id):
        await mess.answer('Данный должник уже существует, отредактируйте текущий долг',
                          reply_markup=change_debots_ikb())
        await state.finish()
    else:
        async with state.proxy() as data:
            data['login_debtor'] = mess.text
        await MyDebtorsStatesGroup.next()
        await mess.answer('Введите сумму долга')


@dp.message_handler(lambda mess: not mess.text.isdigit(), state=MyDebtorsStatesGroup.debt_amount)
async def get_debt_amount(mess: types.Message):
    await mess.answer('Введите число!')


@dp.message_handler(state=MyDebtorsStatesGroup.debt_amount)
async def get_debt_amount(mess: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['debt_amount'] = mess.text
    await MyDebtorsStatesGroup.next()
    await mess.answer('Введите плановую дату возврата долга')


@dp.message_handler(state=MyDebtorsStatesGroup.date_return)
async def get_date_return(mess: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['date_return'] = mess.text
    await create_debt(mess.from_user.id, mess.from_user.username, data['name_debtor'], data['login_debtor'],
                      data['debt_amount'], data['date_return'])
    await mess.answer(text='Долг сохранён',
                      reply_markup=my_debots_ikb())
    await state.finish()


@dp.callback_query_handler(Text(equals=['all_my_debts', 'approve_debt', 'dispute_debt', 'history_dispute']))
async def my_debts_ikb_menu(callback: types.CallbackQuery, state: FSMContext) -> None:
    if callback.data == 'all_my_debts':
        await callback.message.answer(text=await create_recipient_debts_data(await get_recipient_debts(callback.from_user.username)))
        await callback.answer()
    elif callback.data == 'approve_debt':
        async with state.proxy() as data:
            data['check'] = await get_non_approve_debts(callback.from_user.username)
        if data['check'] == []:
            await callback.message.answer(text=await create_recipient_non_approve_debts_data(data['check']))
            await state.finish()
            await callback.answer()
        else:
            await bot.delete_message(chat_id=callback.from_user.id,
                                     message_id=callback.message.message_id)
            await callback.message.answer(text=await create_recipient_non_approve_debts_data(data['check']))
            await callback.message.answer(text='Введите логин того, чей долг хотите подтвердить',
                                      reply_markup=cancel_keyboard())
            await ApproveDebt.login_recipient.set()
            await callback.answer()
    elif callback.data == 'dispute_debt':
        async with state.proxy() as data:
            data['check'] = await get_non_approve_debts(callback.from_user.username)
        if data['check'] == []:
            await callback.message.answer(text=await create_recipient_non_approve_debts_data(data['check']))
        else:
            await callback.message.answer(text=await create_recipient_non_approve_debts_data(data['check']))
            await callback.message.answer(text='<b>Введите логин того (без @), чей долг хотите оспорить </b><em>('
                                               'можно оспорить только тот долг, который вы ещё не подтвердили)</em>',
                                          parse_mode='HTML',
                                          reply_markup=cancel_keyboard())
            await bot.delete_message(chat_id=callback.from_user.id,
                                     message_id=callback.message.message_id)
            await DisputeDebt.login_recipient.set()
    elif callback.data == 'history_dispute':
        await callback.answer(text='Будет доступно позже')


@dp.message_handler(state=DisputeDebt.login_recipient)
async def get_login_recipient_for_dispute(mess: types.Message, state: FSMContext) -> None:
    if mess.text in await get_all_non_approve_recipient_login(mess.from_user.username):
        async with state.proxy() as data:
            data['login_r'] = mess.text
            data['id_debt'] = await get_id_debt(login_r=data['login_r'], login_debtor=mess.from_user.username)
        await DisputeDebt.text.set()
        await mess.answer('Введите комментарий к спору (почему вы не согласны с данным долгом)')
    else:
        await mess.answer('Долгов по данному логину нет, проверьте ещё раз список долгов')
        await mess.answer(text=await create_recipient_non_approve_debts_data(
            await get_non_approve_debts(mess.from_user.username)))


@dp.message_handler(state=DisputeDebt.text)
async def get_text_for_dispute(mess: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['text'] = mess.text
        data['id_recipient'] = await get_id_by_username(login=data['login_r'])
    await create_dispute(id_debt=data['id_debt'], text=data['text'], type='debtor',
                         id_recipient=data['id_recipient'], id_debtor=mess.from_user.id)
    await state.finish()
    await mess.answer(text='Спор был успешно создан, можете проверить его в меню всех споров',
                      reply_markup=main_keyboard())



@dp.message_handler(state=ApproveDebt.login_recipient)
async def get_login_to_approve(mess: types.Message, state: FSMContext) -> None:
    if mess.text in await get_all_non_approve_recipient_login(mess.from_user.username):
        async with state.proxy() as data:
            data['login_r'] = mess.text
        await ApproveDebt.approve.set()
        await mess.answer('Вы уверены, что хотите подтвердить долг? \nДанное действие нельзя будет отменить \nНапишите "Да" или "Нет"')
    else:
        await mess.answer('Долгов по данному логину нет, проверьте ещё раз список долгов')
        await mess.answer(text=await create_recipient_non_approve_debts_data(
            await get_non_approve_debts(mess.from_user.username)))


@dp.message_handler(state=ApproveDebt.approve)
async def get_approve_on_debt(mess: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        pass
    if mess.text == 'Да':
        await approve_debt(login_debt=mess.from_user.username,
                           login_recipient=data['login_r'])
        await state.finish()
        await mess.answer(text='Долг успешно подтверждён',
                          reply_markup=main_keyboard())
    elif mess.text == 'Нет':
        await state.finish()
        await mess.answer(text='Долг не был подтверждён',
                          reply_markup=main_keyboard())
    else:
        await mess.answer('Напишите "Да" или "Нет"!')


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp,
                           skip_updates=True,
                           on_startup=on_startup)