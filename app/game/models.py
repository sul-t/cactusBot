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

class Promocode(Base):
    __tablename__ = 'promocodes'

    code_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uses_left: Mapped[int]
    length: Mapped[int]

class UsesOfPromo(Base):
    __tablename__ = 'uses_of_promo'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))
    code_id: Mapped[int] = mapped_column(ForeignKey('promocodes.code_id'))


