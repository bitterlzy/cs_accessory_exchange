"""交换请求路由 (Listings)"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import (
    Listing, ListingStatus, ListingTracking, TrackingStatus,
    InventoryItem, InventoryStatus, ItemDefinition,
)
from app.schemas import CreateListingRequest, ListingOut, ListingListResponse
from app.deps import get_current_user_id
from app.errors import NotFound, BadRequest, Forbidden

router = APIRouter(prefix="/api/listings", tags=["交换请求"])


@router.get("", response_model=ListingListResponse)
def list_listings(
    category: str = None,
    quality: str = None,
    search: str = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    浏览所有活跃的交换请求
    
    参数:
    - category: 按期望品类筛选
    - quality: 按期望品质筛选
    - search: 按饰品名称搜索
    - page/limit: 分页
    
    只返回 status=active 的请求，已关闭的请求不展示。
    预加载 seller 和 offered_item.definition 避免 N+1。
    """
    query = db.query(Listing).options(
        joinedload(Listing.seller),
        joinedload(Listing.offered_item).joinedload(InventoryItem.definition),
    )
    query = query.filter(Listing.status == ListingStatus.active)

    if category:
        query = query.filter(Listing.want_category == category)
    if quality and quality != "any":
        query = query.filter(Listing.want_quality == quality)
    if search:
        query = query.join(InventoryItem).join(ItemDefinition).filter(
            ItemDefinition.name.contains(search)
        )

    total = query.count()
    listings = query.order_by(Listing.created_at.desc()) \
                     .offset((page - 1) * limit).limit(limit).all()

    return ListingListResponse(
        listings=[ListingOut.from_orm(l) for l in listings],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/my", response_model=list[ListingOut])
def my_listings(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    获取当前用户发布的所有交换请求
    
    返回所有状态的请求（active/closed/cancelled），
    方便用户管理自己的发布记录。
    """
    listings = db.query(Listing).options(
        joinedload(Listing.seller),
        joinedload(Listing.offered_item).joinedload(InventoryItem.definition),
    ).filter(Listing.seller_id == user_id) \
     .order_by(Listing.created_at.desc()).all()
    return [ListingOut.from_orm(l) for l in listings]


@router.post("", response_model=ListingOut, status_code=201)
def create_listing(
    req: CreateListingRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    发布新的交换请求
    
    流程:
    1. 验证物品属于当前用户且状态为 available
    2. 锁定物品 (status -> locked)
    3. 创建 Listing 记录
    4. 写入 listing_tracking 统计表
    5. 返回完整的请求信息（含卖家、物品详情）
    
    约束:
    - 不能上架别人的物品
    - 已锁定的物品不能重复上架
    """
    item = db.query(InventoryItem).filter(InventoryItem.id == req.offered_item_id).first()
    if not item:
        raise NotFound("饰品不存在")
    if item.owner_id != user_id:
        raise Forbidden("无权操作此饰品")
    if item.status != InventoryStatus.available:
        raise BadRequest("饰品当前状态不允许上架")

    # 锁定物品
    item.status = InventoryStatus.locked

    # 创建 Listing
    listing = Listing(
        seller_id=user_id,
        offered_item_id=req.offered_item_id,
        want_description=req.want_description,
        want_category=req.want_category,
        want_specific_definition_id=req.want_specific_definition_id,
        want_quality=req.want_quality or "any",
    )
    db.add(listing)
    db.flush()

    # 写入上架跟踪
    tracking = ListingTracking(
        definition_id=item.definition_id,
        user_id=user_id,
        listing_id=listing.id,
    )
    db.add(tracking)
    db.flush()
    db.refresh(listing)

    # 重新查询以加载关联关系
    listing = db.query(Listing).options(
        joinedload(Listing.seller),
        joinedload(Listing.offered_item).joinedload(InventoryItem.definition),
    ).filter(Listing.id == listing.id).first()

    return ListingOut.from_orm(listing)


@router.patch("/{listing_id}/close")
def close_listing(
    listing_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    关闭自己发布的交换请求
    
    操作:
    - 请求状态设为 cancelled
    - tracking 状态设为 inactive
    - 物品解锁回 available
    
    关闭后该请求不再出现在公开列表中。
    """
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise NotFound("交换请求不存在")
    if listing.seller_id != user_id:
        raise Forbidden("无权操作")

    listing.status = ListingStatus.cancelled

    # 更新跟踪记录
    db.query(ListingTracking).filter(
        ListingTracking.listing_id == listing_id
    ).update({"status": TrackingStatus.inactive})

    # 解锁物品
    db.query(InventoryItem).filter(
        InventoryItem.id == listing.offered_item_id
    ).update({"status": InventoryStatus.available})

    db.flush()
    return {"message": "交换请求已关闭"}
