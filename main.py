from aiogram import Dispatcher, types, Bot, executor
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from config import TOKEN_API
from bot.keyboards.keyboards import main_keyboard, cancel_keyboard
from bot.keyboards.InlineKeyboards import my_debots_ikb, change_debots_ikb
from bot.states.states import MyDebtorsStatesGroup
from bot.db.sqlite import db_start, create_debt, get_user_debtors, get_all_debtors_login, get_recipient_debts

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
async def callback_debtors_main(callback: types.CallbackQuery) -> None:

    if callback.data == 'cancel':
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
    if callback.data == 'new_debtor':
        await MyDebtorsStatesGroup.name_debtor.set()
        await bot.delete_message(chat_id=callback.from_user.id,
                                 message_id=callback.message.message_id)
        await callback.message.answer(text='Введите имя должника',
                                      reply_markup=cancel_keyboard())
    else:
        await callback.answer(text='Будет доступно позже')


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