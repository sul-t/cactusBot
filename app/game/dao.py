from pydantic import BaseModel

from random import randint, choice

from datetime import datetime

from sqlalchemy import select, desc, func, Integer, update
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base
from app.game.models import User, Promocode, UsesOfPromo, Bonus
from app.game.schemas import UserModel, BonusModel
from app.game.schemas import UserDataRequest, UserDataRequest

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
            print(e)
        
    @classmethod
    async def add_user(cls, session: AsyncSession, values: BaseModel):
        values_dict = values.model_dump(exclude_unset=True)
        new_instance = cls.model(**values_dict)
        session.add(new_instance)

        try:
            await session.commit()
        except AssertionError as e:
            await session.rollback()
            
            print(e)

        return new_instance
    
    @classmethod
    async def add_or_update_user(cls, session: AsyncSession, user_info: UserDataRequest, length: int = 0):
        user = await session.get(cls.model, user_info.id)

        if user:
            changes_count = 0

            if user.username == user_info.username:
                user.username == user_info.username
                changes_count += 1

            if user.first_name == user_info.first_name:
                user.first_name == user_info.first_name
                changes_count += 1
            
            if changes_count != 0:
                session.commit()

            return user

        
        values = UserModel(
            user_id = user_info.id,
            username = user_info.username,
            first_name = user_info.first_name,
            length = length,
            last_grow = 0,
            bonus_attempts = 0,
            grow_streak = 0
        )

        return await UserDAO.add_user(session=session, values=values)

    @classmethod
    async def get_top_users(cls, session: AsyncSession, user_id: int, limit: int = 100):
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
    
    # увеличение/уменьшение кактуса
    @classmethod
    async def add_length_cactus(cls, session: AsyncSession, user_id: int, length: int):
        try:
            user = await session.get(cls.model, user_id)

            if datetime.now().date().day == user.last_grow.day:
                user.bonus_attempts -= 1
                user.length += length

                bonuses = BonusModel(
                    bonus_cm = 0,
                    bonus_attempts = user.bonus_attempts
                )
            else:
                if (datetime.now().date().day - user.last_grow.day) > 1:
                    user.grow_streak = 0

                user.grow_streak += 1

                if user.grow_streak > 16:
                    bonuses = await session.get(Bonus, 16)
                else:
                    bonuses = await session.get(Bonus, user.grow_streak)

                user.length += length + bonuses.bonus_cm
                user.last_grow = datetime.now().date()
                user.bonus_attempts += bonuses.bonus_attempts

            await session.commit()

            return user, bonuses
        except AssertionError as e:
            await session.rollback()
            
            print(e)
            

class PromocodeDAO(Base):
    __tablename__ = 'promocode_dao'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    model = Promocode

class UsesOfPromoDAO(Base):
    __tablename__ = 'uses_of_promo_dao'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    model = UsesOfPromo

class BonusDAO(Base):
    __tablename__ = 'bonus_dao'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    model = Bonus

    @classmethod
    async def get_bonuses(cls, session: AsyncSession):
        try:
            # bonuses = await session.get(cls.model)
            query = (
                select(cls.model.min_streak, cls.model.bonus_cm, cls.model.bonus_attempts)
            )

            result = await session.execute(query)
            records = result.fetchall()

            bonus_records = [
                {"min_streak": bonus.min_streak, "bonus_cm": bonus.bonus_cm, "bonus_attempts": bonus.bonus_attempts}
                for bonus in records
            ]

            return bonus_records
        except SQLAlchemyError as e:
            print(e)
