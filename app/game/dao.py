from pydantic import BaseModel

from random import randint, choice

from datetime import datetime

from sqlalchemy import select, desc, func, Integer, update
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base
from app.game.models import User, Promocode, UsesOfPromo
from app.game.schemas import UserModel

from aiogram.types import User as tgUser



class UserDAO(Base):
    __tablename__ = 'user_dao'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    model = User

    @classmethod
    async def find_user(cls, session: AsyncSession, user_id: int):
        try:
            query = select(cls.model).where(cls.model.user_id == user_id)
            result = await session.execute(query)
            record = result.scalar_one_or_none()

            return record
        except SQLAlchemyError as e:
            raise e
        
    @classmethod
    async def add_user(cls, session: AsyncSession, values: BaseModel):
        values_dict = values.model_dump(exclude_unset=True)
        new_instance = cls.model(**values_dict)
        session.add(new_instance)

        try:
            await session.commit()
        except AssertionError as e:
            await session.rollback()
            
            raise e

        return new_instance
    
    @classmethod
    async def add_or_update_user(cls, session: AsyncSession, from_user: tgUser, length: int = 0):
        user = await session.get(cls.model, from_user.id)
        if user:
            changes_count = 0

            if user.username == from_user.username:
                user.username == from_user.username
                changes_count += 1

            if user.first_name == from_user.first_name:
                user.first_name == from_user.first_name
                changes_count += 1
            
            if changes_count != 0:
                session.commit()

            return user

        
        values = UserModel(
            user_id = from_user.id,
            username = from_user.username,
            first_name = from_user.first_name,
            length = length,
            last_grow = 0
        )

        return await UserDAO.add_user(session=session, values=values)

    @classmethod
    async def get_top_users(cls, session: AsyncSession, limit: int = 100):
        try:
            query = (
                select(cls.model.first_name, cls.model.length)
                .order_by(desc(cls.model.length))
                .limit(limit)
            )

            result = await session.execute(query)
            records = result.fetchall()

            ranked_records = [
                {"rank": index + 1, "first_name": record.first_name, "length": record.length}
                for index, record in enumerate(records)
            ]

            return ranked_records
        except SQLAlchemyError as e:
            print(e)
            raise e
    
    # увеличение/уменьшение кактуса
    @classmethod
    async def add_length_cactus(cls, session: AsyncSession, user_id: int, length: int):
        try:
            user = await session.get(cls.model, user_id)

            user.length += length
            user.last_grow = datetime.now().date()
            await session.commit()

            return user
        except AssertionError as e:
            await session.rollback()

            raise print(e)
            

class PromocodeDAO(Base):
    __tablename__ = 'promocode_dao'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    model = Promocode

class UsesOfPromoDAO(Base):
    __tablename__ = 'uses_of_promo_dao'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    model = UsesOfPromo



