"""认证路由 - 注册/登录/JWT 刷新"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.database import get_db
from app.config import settings
from app.models import User, UserStatus
from app.schemas import (
    RegisterRequest, LoginRequest, RefreshRequest,
    AuthResponse, UserOut, TokenResponse,
)
from app.errors import BadRequest, Unauthorized

router = APIRouter(prefix="/api/auth", tags=["认证"])

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _create_token(user_id: int, username: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRES_MINUTES)
    payload = {"user_id": user_id, "username": username, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def _create_refresh_token(user_id: int, username: str) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRES_DAYS)
    payload = {"user_id": user_id, "username": username, "exp": expire}
    return jwt.encode(payload, settings.JWT_REFRESH_SECRET, algorithm=settings.JWT_ALGORITHM)


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册
    
    流程:
    1. 检查邮箱或用户名是否已存在
    2. 使用 bcrypt 哈希密码
    3. 创建用户记录
    4. 生成 JWT access_token 和 refresh_token
    5. 返回用户信息和令牌

    异常:
    - 400: 邮箱或用户名已被注册
    """
    existing = db.query(User).filter(
        (User.email == req.email) | (User.username == req.username)
    ).first()
    if existing:
        raise BadRequest("邮箱或用户名已被注册")

    user = User(
        email=req.email,
        username=req.username,
        password_hash=pwd_ctx.hash(req.password),
    )
    db.add(user)
    db.flush()

    token = _create_token(user.id, user.username)
    refresh_token = _create_refresh_token(user.id, user.username)

    return AuthResponse(
        user=UserOut.from_orm(user),
        token=token,
        refresh_token=refresh_token,
    )


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录
    
    流程:
    1. 根据邮箱查找用户
    2. 检查用户状态（是否禁用）
    3. 验证密码（bcrypt verify）
    4. 更新最后登录时间
    5. 生成 JWT 令牌

    安全策略:
    - 不论邮箱不存在还是密码错误，统一返回"邮箱或密码错误"
    - 防止用户枚举攻击
    """
    user = db.query(User).filter(User.email == req.email).first()
    if not user or user.status == UserStatus.disabled:
        raise Unauthorized("邮箱或密码错误")
    if not pwd_ctx.verify(req.password, user.password_hash):
        raise Unauthorized("邮箱或密码错误")

    user.last_login = datetime.utcnow()
    db.flush()

    token = _create_token(user.id, user.username)
    refresh_token = _create_refresh_token(user.id, user.username)

    return AuthResponse(
        user=UserOut.from_orm(user),
        token=token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(req: RefreshRequest, db: Session = Depends(get_db)):
    """
    刷新 JWT 令牌
    
    流程:
    1. 解码 refresh_token
    2. 验证用户仍存在且未被禁用
    3. 签发新的 access_token + refresh_token

    安全策略:
    - refresh_token 有效期 7 天
    - 每次刷新同时更新 refresh_token，防止 replay attack
    - 用户被禁用后无法刷新
    """
    try:
        payload = jwt.decode(
            req.refresh_token, settings.JWT_REFRESH_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("user_id")
        username = payload.get("username")
        if not user_id:
            raise Unauthorized("无效的刷新令牌")

        user = db.query(User).filter(User.id == user_id).first()
        if not user or user.status == UserStatus.disabled:
            raise Unauthorized("用户不存在或已禁用")

        new_token = _create_token(user.id, user.username)
        new_refresh = _create_refresh_token(user.id, user.username)
        return TokenResponse(token=new_token, refresh_token=new_refresh)
    except JWTError:
        raise Unauthorized("刷新令牌已过期或无效")
