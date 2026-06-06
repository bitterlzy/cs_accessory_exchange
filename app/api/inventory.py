"""库存路由"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import InventoryItem, InventoryStatus, ItemDefinition
from app.schemas import CreateInventoryItemRequest, InventoryItemOut
from app.deps import get_current_user_id
from app.errors import NotFound, BadRequest, Forbidden

router = APIRouter(prefix="/api/inventory", tags=["库存"])


@router.get("", response_model=List[InventoryItemOut])
def list_inventory(
    status: str = None,
    category: str = None,
    search: str = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    获取当前用户的库存列表
    
    筛选条件:
    - status: 按库存状态筛选 (available/locked/traded/removed)
    - category: 按饰品品类筛选 (weapon/knife/gloves/sticker/agent)
    - search: 按饰品名称关键词搜索
    
    性能: 使用 joinedload 预加载 definition 关联，避免 N+1 查询
    """
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
    """
    添加饰品到当前用户的库存
    
    校验:
    - definition_id 必须存在于 item_definitions 数据字典
    
    创建后:
    - 状态默认为 available
    - 需重新查询以加载 definition 关联关系
    """
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
    db.refresh(item)

    # 重新查询以加载关联关系
    item = db.query(InventoryItem).options(
        joinedload(InventoryItem.definition)
    ).filter(InventoryItem.id == item.id).first()

    return InventoryItemOut.from_orm(item)


@router.delete("/{item_id}")
def delete_inventory_item(
    item_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    移除库存中的饰品
    
    约束:
    - 只能移除 available 状态的饰品（上架中或锁定中不可删除）
    - 只能删除自己的饰品
    
    实际操作为软删除: 将状态改为 removed 而非物理删除
    """
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
