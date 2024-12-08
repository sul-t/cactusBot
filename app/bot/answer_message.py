import logging, asyncio, sqlite3

from aiogram import Dispatcher, Bot, F
from aiogram.types import Message
from aiogram.filters import Command

from app.config import TOKEN


bot = Bot(token=TOKEN)
dp = Dispatcher()

connect = sqlite3.connect('./pipisa_db.db')
cursor = connect.cursor()


# @dp.message(Command('answer_message'))
# async def answer_message(message: Message):
#     chats = cursor.execute('select distinct chat_id from chats').fetchall()

#     for chat in chats:
#         try:
#             await bot.send_message(chat[0], 'Сегодня каждый пользователь имеет возможность еще раз вырастить пипису!')
#             await bot.send_message(chat[0], 'Учи английский язык с помощью бота - <a href="t.me/learn_en_bot">Learning English</a>', parse_mode='HTML')
#         except:
#             continue

@dp.message(Command('message_answer'))
async def answer_message(message: Message):
    chats = cursor.execute('select distinct chat_id from chats').fetchall()

    for chat in chats:
        try:
            await bot.send_message(chat[0], 'Вечером на канале @that_sultan будет опубликован промокод на 20см!\nКоличество активаций ограничено!')
        except:
            continue
    
    print('done')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.FileHandler('log.log'),
            logging.StreamHandler()
        ]
    )

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')

