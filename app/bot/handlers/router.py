import re

from random import choice

from datetime import datetime

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.deep_linking import decode_payload, create_start_link

from app.game.dao import UserDAO, PromocodeDAO, UsesOfPromoDAO, BonusDAO
from app.game.schemas import UserModel, PromocodeModel, UsesOfPromoModel
from app.bot.keyboard.kbs import reply_keyboard
from app.database import connection
from app.bot.create_bot import bot
from app.config import settings

from sqlalchemy.ext.asyncio import AsyncSession



router = Router()



@router.message(CommandStart())
@connection()
async def start(message: Message, session: AsyncSession, **kwargs):
    welcome_text = (
        'Приветствую вас в мире "Пиписы"! 🌱✨\n'
        'Каждый день у вас есть возможность увеличивать свою «Пипису», используя команду /grow. Нажимайте её ежедневно, чтобы узнать, насколько твоя «Пиписа» выросла или уменьшилась – в диапазоне случайных чисел от -5 до +10 см 🎲\n\n'
        '<b>Описание команд:</b>\n'
        '🌟 /grow - Попытайте удачу и дайте шанс вышей пиписе вырасти\n'
        '🏆 /top - Узнайте, кто имеет самую большую пипису\n'
        '🤝 /ref - Приглашайте своих друзей по реферальной ссылке и получайте дополнительные сантиметры за каждого, кто присоединится!\n'
        '🎉 /promo - Вводите промокод и растите свою пипису быстрее. Промокоды публикуются на <a href=\'t.me/that_sultan\'>канале</a>\n'
        '🎁 /bonuses - Узнайте о бонусах, которые вы можете получить за ежедневное использование команды /grow!\n\n'
        'Не упустите шанс сделать свою "Пипису" самой большой! Удачи! 🍀'
    )

    try:
        # поиск реферальной ссылки
        match_res = re.match(r'^\/start[^ ]* (.*)', message.text)
        if match_res is None:
            await UserDAO.add_or_update_user(session=session, user_info=message.from_user, length=0)

            return await message.answer(welcome_text)


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
            
        
        current_user = await UserDAO.find_user(session=session, user_id=message.from_user.id)
        if current_user is not None:
            return await message.answer('Вы уже есть в базе!')  

        # обновление данных пользователей
        user = await UserDAO.add_or_update_user(session=session, user_info=message.from_user, length=5)
        await UserDAO.add_length_pipisa(session=session, user_id=invited_user, length=25)

        # возвращаем текст приветствия
        return await message.answer(
            f'{welcome_text}\n'
            f'<a href=\'t.me/{user.username}\'>{user.first_name}</a>, ваша пиписа выросла на <b>{user.length}см 😊</b>\n'
            f'Длина вашей пиписы равна <b>{user.length}см</b> 📏\n', disable_web_page_preview=True
        )
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

        list_top_users = 'Топ 30 пипис мира:\n'
        for user in ranked_users:
            list_top_users += f"{user['rank']}. {user['first_name']}: {user['length']}см\n"
        
        return await message.answer(list_top_users)
    except Exception as e:
        print(e)

        return await message.answer('Произошла ошибка при обработке вашего запроса. Пожалуйста сообщите об ошибке <a href=\'t.me/kickspink\'>разработчику</a>!')


@router.message(Command('bonuses'))
@connection()
async def bonuses(message: Message, session: AsyncSession, **kwargs):
    try:
        bonuses = await BonusDAO.get_bonuses(session=session)

        list_bonuses = 'Бонусы: 🎁\n'
        for bonus in bonuses:
            list_bonuses += f"День {bonus['min_streak']:2}: + {bonus['bonus_cm']:2}см 🌟, + {bonus['bonus_attempts']:2} попыток 🚀\n"

        return await message.answer(list_bonuses)
    except Exception as e:
        print(e)

        return await message.answer('Произошла ошибка при обработке вашего запроса. Пожалуйста сообщите об ошибке <a href=\'t.me/kickspink\'>разработчику</a>!')


@router.message(Command('ref'))
@connection()
async def ref(message: Message, session: AsyncSession, **kwargs):
    try:
        user = await UserDAO.add_or_update_user(session=session, user_info=message.from_user)
        link = await create_start_link(bot, str(user.user_id), encode=True)

        return await message.answer(f'Начинай ростить свою пипису! 🌱✨\nПолучай 25 см за каждого приведенного друга! 👥💥\nПрисоединяйся по ссылке и получи бонус в 5 см! 🎉😉\n{link}', disable_web_page_preview=False)
    except Exception as e:
        print(e)

        return await message.answer('Произошла ошибка при обработке вашего запроса. Пожалуйста сообщите об ошибке <a href=\'t.me/kickspink\'>разработчику</a>!')


@router.message(Command('promo'))
@connection()
async def promo(message: Message, session: AsyncSession, **kwargs):
    try:
        match_promo = re.match(r'^\/promo (\d+)', message.text)
        if match_promo is None:
            return await message.answer('Вызов команды должен выглядеть как /promo ПРОМОКОД')
        

        code = match_promo[1]

        promo_exists = await PromocodeDAO.find_promo(session=session, code_id=code)
        if promo_exists is None:
            return await message.answer('Данного промокода не существует')
        

        user_id = message.from_user.id

        uses_of_promo = await UsesOfPromoDAO.check_uses(session=session, user_id=user_id, code_id=code)
        if uses_of_promo is not None:
            return await message.answer('Вы уже использовали данный промокод')
        

        values = UsesOfPromoModel(
            user_id = user_id,
            code_id = code
        )
        user = await UsesOfPromoDAO.add_uses(session=session, values=values, length=promo_exists.length)

        return await message.answer(
            f'<a href=\'t.me/{user.username}\'>{user.first_name}</a>, ваша пиписа выросла на <b>{promo_exists.length}см 😊</b>\n'
            f'Длина вашей пиписы равна <b>{user.length}см</b> 📏\n', disable_web_page_preview=True
        )


    except Exception as e:
        print(e)
        
        return await message.answer('Произошла ошибка при обработке вашего запроса. Пожалуйста сообщите об ошибке <a href=\'t.me/kickspink\'>разработчику</a>!')
    

@router.message(Command('sending_message'))
@connection()
async def answer_message(message: Message, session: AsyncSession, **kwargs):
    user_id = message.from_user.id
    if user_id in settings.ADMIN_IDS:
        number_processed_users = 0
        inactiv_users = 0
        
        users = await UserDAO.all_users(session=session)

        for user in users:
            number_processed_users += 1

            try:
                if number_processed_users % 50 == 0:
                    print(number_processed_users)

                await bot.send_message(
                    user[0], 
                    'Дорогие друзья! 🎉\n\n'
                    'Поздравляю вас с Новым годом! 😊 Хочу выразить благодарность за ваше доверие и использование бота. В 25 году я постараюсь создать для вас нечто поистине грандиозное. ✨\n\n'
                    'Желаю вам крепкого здоровья 💪, успехов во всех начинаниях 🚀, достижения всех поставленных целей 🌟 и, конечно же, значительного роста вашей пиписы! 📈\n\n'
                    'Обновления:\n'
                    '1. Функция уменьшения "пиписы" за неактивность заменена на бонусы за ежедневное использование команды /grow. На 16-й день активного использования вы получите +15 см и 3 дополнительные попытки. 🎁\n'
                    '2. Все бонусы доступны по команде /bonuses. 🔍\n'
                    '3. Топ чатов временно недоступен, но вернётся позже. ⏳\n'
                    '4. Топ «пипис» мира расширен до 30 пользователей и доступен по команде /top 👥\n'
                    '5. Реферальная программа обновлена: за каждого приглашенного друга вы получаете 25 см вместо 1 см. 🤝\n'
                    '6. На днях на <a href=\'t.me/that_sultan\'>канале</a> будет опубликован промокод на сантимеры. 🎫\n\n'
                    'Спасибо за поддержку! Пусть 25 год принесёт радость и новые возможности! 🎄🎆', disable_web_page_preview=True
                )
            except:
                inactiv_users += 1
                if inactiv_users % 5 == 0:
                    print(inactiv_users)

                continue
        
        print(
            f'кол-во пользователей {number_processed_users}\n'
            f'кол-во неактивных пользователей {inactiv_users}'
            )