from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from sqlalchemy.ext.asyncio import AsyncSession

from aiogram.utils.web_app import check_webapp_signature, parse_webapp_init_data

from random import choice

from datetime import datetime, date

from app.game.dao import UserDAO
from app.database import get_session
from app.game.schemas import UserDataRequest
from app.config import settings




router = APIRouter(prefix='', tags=['ИГРА'])



@router.get('/')
async def set_user_data(initData: str, session: AsyncSession = Depends(get_session)):
    try:
        valid = check_webapp_signature(settings.BOT_TOKEN, initData)
        if not valid:
            return {'message': 'invalid data'}
        
        
        data = parse_webapp_init_data(initData)

        values = UserDataRequest(
            id = data.user.id,
            username = data.user.username,
            first_name = data.user.first_name
        )
        
        user = await UserDAO.add_or_update_user(session=session, user_info=values)

        return user.to_dict()
    except Exception as e:
        print(e)
        return {'error': 'inform the administrator about the error'}

@router.put('/')
async def update_user(initData: str, session: AsyncSession = Depends(get_session)):
    try:
        valid = check_webapp_signature(settings.BOT_TOKEN, initData)
        if not valid:
            return {'message': 'invalid data'}
        
        
        data = parse_webapp_init_data(initData)

        user = await UserDAO.find_user(session=session, user_id=data.user.id)

        if user.last_grow >= datetime.now().date():
            return user, None


        random_length = choice([i for i in range(-5, 10) if i not in [0]])  

        user = await UserDAO.add_length_cactus(session=session, user_id=data.user.id, length=random_length)

        return user.to_dict(), random_length
    except Exception as e:
        print(e)
        return {'error': 'inform the administrator about the error'}