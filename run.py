import asyncio
import logging, sqlite3

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from datetime import datetime, timedelta

from config import TOKEN
from app.hendlers import router



async def inactiv_users():
    cursor.execute('update users set length = max(length - 5, 0) where last_grow <= date(julianday() - 3)')
    connection.commit()

    users_info = cursor.execute('''
                                select max(chats.chat_id) as chat_id, users.first_name, users.length
                                from chats
                                inner join users
                                    on chats.user_id = users.user_id
                                where users.last_grow <= date(julianday() - 3) and users.length >= 0
                                group by chats.user_id
                            ''').fetchall()

    for info in users_info:
        print(info[0], info[1])
        await bot.send_message(info[0], f'{info[1]}, ты слишком долго не был активным, поэтому твоя пиписа начала уменьшаться!\nТеперь её длина равна: {info[2]}см!')



async def main():
    scheduler = AsyncIOScheduler()
    scheduler_time = datetime.now().strftime('%Y-%m-%d ') + '15:42:00'
    trigger = IntervalTrigger(days=1, start_date=scheduler_time)
    scheduler.add_job(inactiv_users, trigger=trigger)
    scheduler.start()

    dp.include_router(router)
    await dp.start_polling(bot)



bot = Bot(token=TOKEN)
dp = Dispatcher()

connection = sqlite3.connect('./pipisa_db.db')
cursor = connection.cursor()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, 
                        handlers=[
                            logging.FileHandler('log.log'),
                            logging.StreamHandler()
                        ])
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')