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

# Alipay 实名认证
    ALIPAY_APP_ID: Optional[str] = None
    ALIPAY_PRIVATE_KEY: Optional[str] = None
    ALIPAY_PUBLIC_KEY: Optional[str] = None
    ALIPAY_VERIFY_ENABLED: bool = False

# Steam Web API
    STEAM_API_KEY: Optional[str] = None
    STEAM_BOT_USERNAME: Optional[str] = None
    STEAM_BOT_PASSWORD: Optional[str] = None
    STEAM_BOT_SHARED_SECRET: Optional[str] = None
    STEAM_BOT_IDENTITY_SECRET: Optional[str] = None
    STEAM_TRADE_POLL_INTERVAL: int = 30
    STEAM_TRADE_TIMEOUT_MINUTES: int = 30
    STEAM_ESCROW_MAX_DAYS: int = 15

# BUFF 价格同步
    BUFF_COOKIE: Optional[str] = None
    BUFF_SYNC_INTERVAL_HOURS: int = 6

    # 配置
    MAX_ACCOUNTS_PER_IP: int = 3
    MAX_ACCOUNTS_PER_DEVICE: int = 2
    WITHDRAW_LIMIT_DAILY: int = 50000
    WITHDRAW_REVIEW_THRESHOLD: int = 5000
    WITHDRAW_DELAY_HOURS: int = 24


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
