"""通知路由"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Notification
from app.schemas import NotificationOut, NotificationListResponse
from app.deps import get_current_user_id
from app.errors import NotFound, Forbidden

router = APIRouter(prefix="/api/notifications", tags=["通知"])


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    unread_only: bool = False,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    获取当前用户的通知列表
    
    参数:
    - unread_only: 是否只返回未读通知
    - page/limit: 分页参数（默认每页 20 条）
    
    返回:
    - notifications: 通知列表
    - total: 总通知数
    - unread_count: 未读通知数
    - page/limit: 分页信息
    """
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if unread_only:
        query = query.filter(Notification.is_read == False)

    total = query.count()
    unread_count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False,
    ).count()

    notifications = query.order_by(Notification.created_at.desc()) \
                         .offset((page - 1) * limit).limit(limit).all()

    return NotificationListResponse(
        notifications=[NotificationOut.from_orm(n) for n in notifications],
        total=total,
        unread_count=unread_count,
        page=page,
        limit=limit,
    )


@router.patch("/{notif_id}/read")
def mark_read(
    notif_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    标记单条通知为已读
    
    校验:
    - 通知必须属于当前用户，防止越权标记
    """
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if not notif:
        raise NotFound("通知不存在")
    if notif.user_id != user_id:
        raise Forbidden("无权操作")

    notif.is_read = True
    db.flush()
    return {"message": "标记已读"}


@router.post("/read-all")
def mark_all_read(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    将当前用户的所有未读通知标记为已读
    
    使用批量 UPDATE 避免逐条操作，
    适用于用户进入通知页面时的"全部已读"操作。
    """
    db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False,
    ).update({"is_read": True})
    db.flush()
    return {"message": "全部标记已读"}
