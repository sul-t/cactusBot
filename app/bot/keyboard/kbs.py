from aiogram.types import ReplyKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from app.config import settings



def reply_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()

    kb.button(text='MiniApp', web_app=WebAppInfo(url=settings.BASE_SITE))
    kb.adjust(1)

    return kb.as_markup(resize_keyboard=True)