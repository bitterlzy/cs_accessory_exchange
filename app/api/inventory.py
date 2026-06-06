"""库存路由"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import InventoryItem, InventoryStatus, ItemDefinition
from app.schemas import CreateInventoryItemRequest, InventoryItemOut
from app.deps import get_current_user_id
from app.errors import NotFound, BadRequest, Forbidden

router = APIRouter(prefix="/api/inventory", tags=["库存"])


@router.get("", response_model=list[InventoryItemOut])
def list_inventory(
    status: str = None,
    category: str = None,
    search: str = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """获取我的库存列表"""
    query = db.query(InventoryItem).options(joinedload(InventoryItem.definition))
    query = query.filter(InventoryItem.owner_id == user_id)

    if status:
        query = query.filter(InventoryItem.status == status)
    if category:
        query = query.join(ItemDefinition).filter(ItemDefinition.category == category)
    if search:
        query = query.join(ItemDefinition).filter(ItemDefinition.name.contains(search))

    items = query.order_by(InventoryItem.created_at.desc()).all()
    return [InventoryItemOut.from_orm(i) for i in items]


@router.post("", response_model=InventoryItemOut, status_code=201)
def create_inventory_item(
    req: CreateInventoryItemRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """添加饰品到库存"""
    # 验证装备字典存在
    definition = db.query(ItemDefinition).filter(ItemDefinition.id == req.definition_id).first()
    if not definition:
        raise NotFound("装备不存在于数据字典中")

    item = InventoryItem(
        owner_id=user_id,
        definition_id=req.definition_id,
        quality=req.quality,
        float_value=req.float_value,
        pattern=req.pattern,
        stat_trak=req.stat_trak,
        souvenir=req.souvenir,
        description=req.description,
        image_url=req.image_url,
    )
    db.add(item)
    db.flush()
    db.refresh(item, ["definition"])

    return InventoryItemOut.from_orm(item)


@router.delete("/{item_id}")
def delete_inventory_item(
    item_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """删除（移除）库存饰品"""
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise NotFound("饰品不存在")
    if item.owner_id != user_id:
        raise Forbidden("无权操作此饰品")
    if item.status != InventoryStatus.available:
        raise BadRequest("饰品当前状态不允许删除")

    item.status = InventoryStatus.removed
    db.flush()

    return {"message": "饰品已移除"}
