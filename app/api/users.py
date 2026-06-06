"""用户路由"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserOut
from app.deps import get_current_user_id
from app.errors import NotFound

router = APIRouter(prefix="/api/users", tags=["用户"])


@router.get("/me", response_model=UserOut)
def get_me(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """获取当前用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFound("用户不存在")
    return UserOut.from_orm(user)


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """查看用户公开资料"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFound("用户不存在")
    return UserOut.from_orm(user)
