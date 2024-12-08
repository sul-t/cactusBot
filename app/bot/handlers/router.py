import re

from random import choice

from datetime import datetime

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.deep_linking import decode_payload, create_deep_link

from app.game.dao import UserDAO, PromocodeDAO, UsesOfPromoDAO
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
        match_res = re.match(r'^\/start[^ ]* (.*)', message.text)
        if match_res is None:
            await UserDAO.add_or_update_user(session=session, from_user=message.from_user, length=0)

            return await message.answer(welcome_text, reply_markup=reply_keyboard())


        encoded_invite = match_res[1]
        try:
            invited_user = decode_payload(encoded_invite)
        except Exception as e:
            return await message.answer('Некорректная рефферальная ссылка!\nПопросите друга отправить вам ее снова, либо нажмите /start')                


        user_invited_info = await UserDAO.find_user(session=session, user_id=invited_user)
        if user_invited_info is None:
            return await message.answer('Некорректная рефферальная ссылка!\nПопросите друга отправить вам ее снова, либо нажмите /start')                
            

        await UserDAO.add_or_update_user(session=session, from_user=message.from_user, length=5)
        await UserDAO.add_length_cactus(session=session, user_id=invited_user, length=25)

        await message.answer(welcome_text, reply_markup=reply_keyboard())
    except Exception as e:
        print(e)
        await message.answer('Произошла ошибка при обработке вашего запроса. Пожалуйста сообщите об ошибке <a href=\'t.me/kickspink\'>разработчику</a>!')


@router.message(Command('grow'))
@connection()
async def grow_cactuc(message: Message, session: AsyncSession, **kwargs):
    try: 
        user = await UserDAO.add_or_update_user(session=session, from_user=message.from_user, length=0)

        if user.last_grow == datetime.now().date():
            return await message.answer(f'Вы уже играли сегодня.\nРазмер вашего кактуса: {user.length}см')
    
        
        random_length = choice([i for i in range(-5, 10) if i not in [0]])
        user = await UserDAO.add_length_cactus(session=session, user_id=user.user_id, length=random_length)
        
        if random_length > 0:
            return await message.answer(f'Ваш кактус увеличился на: {random_length}см\nТеперь его длина состовляет: {user.length}')
        else:
            return await message.answer(f'Ваш кактус уменьшился на: {random_length}см\nТеперь его длина состовляет: {user.length}')
    except Exception as e:
        print(e)
        await message.answer('Произошла ошибка при обработке вашего запроса. Пожалуйста сообщите об ошибке <a href=\'t.me/kickspink\'>разработчику</a>!')
