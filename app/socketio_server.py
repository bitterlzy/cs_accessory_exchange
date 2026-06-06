"""Socket.IO 实时推送服务"""
import socketio
from app.config import settings

# Socket.IO 服务端 (与 FastAPI 共享端口)
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.CORS_ORIGINS,
    ping_interval=25,
    ping_timeout=20,
)

# ASGI 包装
socket_app = socketio.ASGIApp(sio)


@sio.event
async def connect(sid, environ, auth):
    """客户端连接 - 需要 JWT token"""
    token = auth.get("token") if auth else None
    if not token:
        raise ConnectionRefusedError("Authentication required")

    from jose import jwt, JWTError
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise ConnectionRefusedError("Invalid token")

        # 存入 sid -> user_id 映射
        await sio.save_session(sid, {"user_id": user_id, "username": payload.get("username", "")})

        # 加入个人房间
        sio.enter_room(sid, f"user:{user_id}")

        # 广播在线状态
        await sio.emit("user_online", {"user_id": user_id, "online": True})
        print(f"[WS] User {user_id} connected")
    except JWTError:
        raise ConnectionRefusedError("Token expired or invalid")


@sio.event
async def disconnect(sid):
    session = await sio.get_session(sid)
    if session and "user_id" in session:
        user_id = session["user_id"]
        sio.leave_room(sid, f"user:{user_id}")
        await sio.emit("user_online", {"user_id": user_id, "online": False})
        print(f"[WS] User {user_id} disconnected")


async def send_offer_update(offer_id: int, user_ids: list, event_type: str, **extra):
    """向指定用户推送交换提议状态变更"""
    for uid in user_ids:
        await sio.emit(
            "offer_update",
            {"type": event_type, "offer_id": offer_id, **extra},
            room=f"user:{uid}",
        )


async def send_notification(user_id: int, notif_data: dict):
    """向指定用户推送通知"""
    await sio.emit("notification", notif_data, room=f"user:{user_id}")
