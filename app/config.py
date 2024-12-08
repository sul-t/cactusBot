import os

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: List[int]
    DB_URL: str = 'sqlite+aiosqlite:///data/db.sqlite3'
    BASE_SITE: str

    model_config = SettingsConfigDict(
        env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )

    def get_webhook_url(self) -> str:
        return f'{self.BASE_SITE}/webhook'
    


settings = Settings()
database_url = settings.DB_URL