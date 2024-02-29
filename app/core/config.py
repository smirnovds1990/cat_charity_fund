from pydantic import BaseSettings


class Settings(BaseSettings):
    app_title: str = 'Кошачий благотворительный фонд'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = 'SECRET'

    class Config:
        env_file = '.env'


settings = Settings()
