from main import bot


async def delete_mess(callback, type=None):
    if type == 'callback':
        try:
            await bot.delete_message(chat_id=callback.from_user.id,
                                 message_id=callback.message.message_id)
        except:
            pass
    else:
        try:
            await bot.delete_message(chat_id=callback.from_user.id,
                                     message_id=callback.message_id)
        except:
            pass