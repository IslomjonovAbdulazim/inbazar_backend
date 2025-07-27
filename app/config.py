from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 43200  # 30 days

    # Telegram Bot
    telegram_bot_token: str
    telegram_bot_username: str

    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_bucket: str = "clothing-images"

    # Admin
    admin_telegram_id: str

    # App
    app_name: str = "Clothing Shop API"
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()