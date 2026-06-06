"""FastAPI 应用入口"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import engine, Base
from app.models import *  # noqa: 确保模型注册
from app.api import (
    auth, users, kyc, inventory,
    listings, offers, trades, notifications, steam,
)
from app.socketio_server import socket_app
from app.errors import AppError

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(inventory.router)
app.include_router(listings.router)
app.include_router(offers.router)
app.include_router(trades.router)
app.include_router(notifications.router)
app.include_router(kyc.router)
app.include_router(steam.router)


@app.on_event("startup")
async def startup():
    """启动时创建数据库表"""
    Base.metadata.create_all(bind=engine)
    print(f"[CS-Trade] Database tables synced")


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail.get("error", str(exc))},
    )


@app.get("/api/health")
def health():
    return {"status": "ok", "timestamp": __import__("datetime").datetime.utcnow().isoformat()}


# 挂载 Socket.IO
app.mount("/ws", socket_app)
