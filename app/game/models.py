from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, ForeignKey

from datetime import date

from app.database import Base



class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str | None]
    first_name: Mapped[str | None]
    length: Mapped[int]
    last_grow: Mapped[date]
    bonus_attempts: Mapped[int]
    grow_streak: Mapped[int]

    def to_dict(self):
        return {
            "id": self.user_id,
            "username": self.username,
            "first_name": self.first_name,
            "length": self.length,
            "last_grow": self.last_grow,
            "bonus_attempts": self.bonus_attempts,
            "grow_streak": self.grow_streak
        }

class Promocode(Base):
    __tablename__ = 'promocodes'

    code_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uses_left: Mapped[int]
    length: Mapped[int]

class UsesOfPromo(Base):
    __tablename__ = 'uses_of_promo'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))
    code_id: Mapped[int] = mapped_column(ForeignKey('promocodes.code_id'))

class Bonus(Base):
    __tablename__ = 'bonuses'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    min_streak: Mapped[int]
    bonus_cm: Mapped[int]
    bonus_attempts: Mapped[int]
