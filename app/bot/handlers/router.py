import re

from random import choice

from datetime import datetime

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.deep_linking import decode_payload, create_deep_link

from app.game.dao import UserDAO, PromocodeDAO, UsesOfPromoDAO, BonusDAO
from app.game.schemas import UserModel, PromocodeModel, UsesOfPromoModel
from app.bot.keyboard.kbs import reply_keyboard
from app.database import connection

from sqlalchemy.ext.asyncio import AsyncSession



router = Router()



@router.message(CommandStart())
@connection()
async def start(message: Message, session: AsyncSession, **kwargs):
    welcome_text = (
        'Текст приветствия!'
    )

    try:
        # поиск реферальной ссылки
        match_res = re.match(r'^\/start[^ ]* (.*)', message.text)
        if match_res is None:
            await UserDAO.add_or_update_user(session=session, user_info=message.from_user, length=0)

            return await message.answer(welcome_text, reply_markup=reply_keyboard())


        # декодирование реферальной ссылки
        encoded_invite = match_res[1]
        try:
            invited_user = decode_payload(encoded_invite)
        except Exception as e:
            return await message.answer('Некорректная рефферальная ссылка!\nПопросите друга отправить вам ее снова, либо нажмите /start')                
        

        # поиск пригласившего пользователя
        user_invited_info = await UserDAO.find_user(session=session, user_id=invited_user)
        if user_invited_info is None:
            return await message.answer('Некорректная рефферальная ссылка!\nПопросите друга отправить вам ее снова, либо нажмите /start')                
            

        # обновление данных пользователей
        await UserDAO.add_or_update_user(session=session, user_info=message.from_user, length=5)
        await UserDAO.add_length_cactus(session=session, user_id=invited_user, length=25)

        # возвращаем текст приветствия
        return await message.answer(welcome_text, reply_markup=reply_keyboard())
    except Exception as e:
        print(e)

        return await message.answer('Произошла ошибка при обработке вашего запроса. Пожалуйста сообщите об ошибке <a href=\'t.me/kickspink\'>разработчику</a>!')



@router.message(Command('grow'))
@connection()
async def grow_cactuc(message: Message, session: AsyncSession, **kwargs):
    try: 
        # обновление данных пользователя
        user = await UserDAO.add_or_update_user(session=session, user_info=message.from_user, length=0)

        # проверка на доп попытки и последнее прожатие
        if (user.bonus_attempts == 0) and (user.last_grow == datetime.now().date()):
            return await message.answer(
                f'<a href=\'t.me/{user.username}\'>{user.first_name}</a>, у вас нет попыток 😢. Возвращайтесь завтра 🌅\n'
                f'Длина вашей пиписы равна <b>{user.length}см</b> 📏\n'
                f'Ваш grow streak <b>{user.grow_streak}</b> ✨', disable_web_page_preview=True
            )
    

        # генерация рандомного значения в заданном диапазане исключая ноль
        random_length = choice([i for i in range(-5, 10) if i not in [0]])
        user, bonuses = await UserDAO.add_length_cactus(session=session, user_id=user.user_id, length=random_length)

        bonus_text = ''
        if bonuses.bonus_cm > 0:
            bonus_text = f'Начисленно <b>{bonuses.bonus_cm} бонусных см 💫</b>'

        print(bonus_text)

        if random_length > 0:
            return await message.answer(
                f'<a href=\'t.me/{user.username}\'>{user.first_name}</a>, ваша пиписа выросла на <b>{random_length}см 😊</b>. {bonus_text}\n'
                f'Длина вашей пиписы равна <b>{user.length}см</b> 📏\n'
                f'Осталось <b>{user.bonus_attempts}</b> попыток для использования команды /grow 🌿\n'
                f'Ваш grow streak <b>{user.grow_streak}</b> ✨', disable_web_page_preview=True
            )
        else:
            return await message.answer(
                f'<a href=\'t.me/{user.username}\'>{user.first_name}</a>, ваша пиписа сократилась на <b>{random_length}см 😔</b>. {bonus_text}\n'
                f'Длина вашей пиписы равна <b>{user.length}см</b> 📏\n'
                f'Осталось <b>{user.bonus_attempts}</b> попыток для использования команды /grow 🌿\n'
                f'Ваш grow streak <b>{user.grow_streak}</b> ✨', disable_web_page_preview=True
            )
    except Exception as e:
        print(e)

        return await message.answer('Произошла ошибка при обработке вашего запроса. Пожалуйста сообщите об ошибке <a href=\'t.me/kickspink\'>разработчику</a>!')



@router.message(Command('top'))
@connection()
async def top_users(message: Message, session: AsyncSession, **kwargs):
    try:
        ranked_users = await UserDAO.get_top_users(session=session, user_id=message.from_user.id)

        list_top_users = 'Топ 100 пипис мира:\n'
        for user in ranked_users:
            list_top_users += f'{user['rank']}. {user['first_name']}: {user['length']}см\n'
        
        return await message.answer(list_top_users)
    except Exception as e:
        print(e)

        return await message.answer('Произошла ошибка при обработке вашего запроса. Пожалуйста сообщите об ошибке <a href=\'t.me/kickspink\'>разработчику</a>!')



@router.message(Command('bonuses'))
async def bonuses(message: Message, session: AsyncSession, **kwargs):
    bonuses = await BonusDAO.get_bonuses(session=session)
    return print(bonuses)
