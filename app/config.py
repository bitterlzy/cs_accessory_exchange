from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "CS饰品交换平台"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 3000

    # Database
    DATABASE_URL: str = "mysql+pymysql://root:li991208@localhost:3306/cs_trade_db?charset=utf8mb4"

    # JWT
    JWT_SECRET: str = "cs-trade-jwt-secret-dev-2026"
    JWT_REFRESH_SECRET: str = "cs-trade-refresh-secret-dev-2026"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_MINUTES: int = 60         # 1h
    JWT_REFRESH_EXPIRES_DAYS: int = 7     # 7d

    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    # Redis (optional)
    REDIS_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
