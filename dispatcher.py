from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from env import API_TOKEN
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# @dp.channel_post_handler(regexp=r'/id')
# async def chanel_post(update : types.Message):
#     id = update.sender_chat.id
#     data = await update.answer(f"id: `{id}`", parse_mode=types.ParseMode.MARKDOWN)
#     print(data)
#
#     try:
#         await update.delete()
#         await bot.delete_message(chat_id=id, message_id=data.message_id)
#     except:
#         pass