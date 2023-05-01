from aiogram import Dispatcher, types, Bot, executor
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from config import TOKEN_API
from bot.keyboards.keyboards import main_keyboard, cancel_keyboard
from bot.keyboards.InlineKeyboards import my_debots_ikb, change_debots_ikb, debt_editing_menu_ikb
from bot.states.states import MyDebtorsStatesGroup, ChangeDebtStatesGroup
from bot.db.sqlite import db_start, create_debt, get_user_debtors, get_all_debtors_login, get_recipient_debts, \
    check_user_debt, get_debt_amount_sql, update_user_debt, delete_a_debt

from bot.processors.text_processors import craete_text_format, create_recipient_debts_data


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
"""


@dp.message_handler(commands=['help'])
async def help_cmd(mess: types.Message) -> None:
    await mess.answer(text=help_text,
                      parse_mode='HTML')


@dp.message_handler(commands=['start'])
async def start_cmd(mess: types.Message) -> None:
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
    await mess.answer(text=await create_recipient_debts_data(await get_recipient_debts(mess.from_user.username)))


@dp.callback_query_handler(Text(equals=['cancel', 'change_debtors', 'all_debtors']))
async def callback_debtors_main(callback: types.CallbackQuery, state: FSMContext) -> None:
    if callback.data == 'cancel':
        await state.finish()
        await bot.delete_message(chat_id=callback.from_user.id,
                                 message_id=callback.message.message_id)
        await callback.message.answer(text='Вы вернулись в главное меню',
                                      reply_markup=main_keyboard())

    elif callback.data == 'all_debtors':
        text = await craete_text_format(await get_user_debtors(callback.from_user.id))
        if text == '':
            await callback.message.answer(text='У вас пока нет должников')
            await callback.answer()
        else:
            await callback.message.answer(text=text)
            await callback.answer()

    elif callback.data == 'change_debtors':
        await bot.delete_message(chat_id=callback.from_user.id,
                                 message_id=callback.message.message_id)
        await bot.send_photo(
            photo='https://kartinki.pibig.info/uploads/posts/2023-04/1681157639_kartinki-pibig-info-p-dolzhnik-kartinka-arti-vkontakte-2.jpg',
            reply_markup=change_debots_ikb(),
            chat_id=callback.from_user.id)

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
        await callback.message.answer(text='Долг успешно закрыт')
        await callback.answer()


@dp.message_handler(state=ChangeDebtStatesGroup.change_amount_to_increase)
async def increase_a_debt(mess: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['amount'] = int(mess.text)
        data['old_amount'] = await get_debt_amount_sql(user_login=data['login'],
                                                       id_recipient=mess.from_user.id)
        data['new_amount'] = data['old_amount'] + data['amount']
    await update_user_debt(data['login'], data['new_amount'], mess.from_user.id)
    await mess.answer('Долг был успешно увеличен')


@dp.message_handler(state=ChangeDebtStatesGroup.change_amount_to_decrease)
async def decrease_a_debt(mess: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['amount'] = int(mess.text)
        data['old_amount'] = await get_debt_amount_sql(user_login=data['login'],
                                                       id_recipient=mess.from_user.id)
        data['new_amount'] = data['old_amount'] - data['amount']
    if data['new_amount'] <= 0:
        await delete_a_debt(data['login'], mess.from_user.id)
        await mess.answer('Долг стал равен нулю (или меньше, поэтому был закрыт)')
    else:
        await update_user_debt(data['login'], data['new_amount'], mess.from_user.id)
        await mess.answer('Долг был успешно уменьшен')



@dp.message_handler(state=MyDebtorsStatesGroup.name_debtor)
async def get_name_debtor(mess: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name_debtor'] = mess.text
    await MyDebtorsStatesGroup.next()
    await mess.answer('Введите логин телеграмм должника без @')


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
    await mess.answer('Долг сохранён')
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp,
                           skip_updates=True,
                           on_startup=on_startup)