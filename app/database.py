from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from functools import wraps

from app.config import database_url



engine = create_async_engine(url=database_url)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)



class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True



def connection(isolation_level=None):
    def decorator(method):
        @wraps(method)
        async def wrapper(*args, **kwargs):
            async with async_session_maker() as session:
                try:
                    if isolation_level:
                        await session.execute(text(f'SET TRANSACTION ISOLATION LEVEL {isolation_level}'))

                    return await method(*args, session=session, **kwargs)
                except Exception as e:
                    await session.rollback()

                    raise e
                finally:
                    await session.close()

        return wrapper
            
    return decorator
