from aiogram import Dispatcher, types, Bot, executor
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove

from config import TOKEN_API
from bot.keyboards.keyboards import main_keyboard
from bot.keyboards.InlineKeyboards import my_debots_kb

async def on_startup(_):
    # await db_start()
    print('Запустился')

# storage = MemoryStorage()

bot = Bot(TOKEN_API)
dp = Dispatcher(bot=bot)


start_text = """
<b>Привет! 
Я бот, который поможет тебе следить за тем, отдают ли тебе деньги должники, а заодно не даст тебе забыть о своих долгах!</b>
"""


help_text = """
<b>/start</b> - <em>запустить бота</em>
<b>/my_debtors</b> - <em>откроет меню для отслеживания и редактирования ваших должников</em>
<b>/start</b> - <em>покажет ваши долги</em>
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
                         reply_markup=my_debots_kb(),
                         chat_id=mess.chat.id)


@dp.callback_query_handler(Text(equals='all_debtors'))
async def callback_all_debtors(callback: types.CallbackQuery) -> None:
    await callback.answer(text='test')


@dp.callback_query_handler(Text(equals='cancel'))
async def callback_all_debtors(callback: types.CallbackQuery) -> None:
    await callback.answer(text='Вы вернулись в главное меню')



if __name__ == '__main__':
    executor.start_polling(dispatcher=dp,
                           skip_updates=True,
                           on_startup=on_startup)