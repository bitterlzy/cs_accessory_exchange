"""BUFF.163.com 饰品数据爬虫与同步服务

提供与 BUFF 平台对接的功能:
1. 从 BUFF API 获取 CS2 饰品列表（支持分页）
2. 获取饰品实时价格（买入/卖出）
3. 同步价格数据到 item_prices 表
4. 补充 item_definitions 表缺失的饰品

使用方式:
    from services.buff_scraper import BUFFScraper
    scraper = BUFFScraper(cookie="your_buff_cookie")
    items = await scraper.fetch_goods_list(page=1)

注意事项:
- 需要有效的 BUFF 登录 Cookie（从浏览器提取）
- Cookie 会过期，需要定期更新
- 请合理控制请求频率，避免触发反爬

API 端点:
- GET https://buff.163.com/api/market/goods?game=csgo&page_num=N&page_size=80
- GET https://buff.163.com/api/market/goods/{goods_id}/price?game=csgo
"""

import json
import time
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

# BUFF API 配置
BUFF_API_BASE = "https://buff.163.com/api"
BUFF_GOODS_LIST = BUFF_API_BASE + "/market/goods"
BUFF_GOODS_PRICE = BUFF_API_BASE + "/market/goods/{}/price"
BUFF_GOODS_DETAIL = BUFF_API_BASE + "/market/goods/{}"

# 请求头
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Origin": "https://buff.163.com",
    "Referer": "https://buff.163.com/market/csgo",
}


class BUFFScraper:
    """BUFF 平台数据抓取客户端"""

    def __init__(self, cookie: str = None, use_proxy: bool = False, request_interval: float = 1.0):
        self.cookie = cookie
        self.use_proxy = use_proxy
        self.request_interval = request_interval
        self.last_request_time = 0.0
        self.headers = DEFAULT_HEADERS.copy()
        if cookie:
            self.headers["Cookie"] = cookie

    def _rate_limit(self):
        """请求频率控制"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_interval:
            time.sleep(self.request_interval - elapsed)
        self.last_request_time = time.time()

    def _request(self, url: str, params: dict = None) -> Optional[dict]:
        """发送 HTTP 请求到 BUFF API

        注意: 当前环境网络受限，此方法为 stub 实现。
        在正式环境中，应使用 httpx 或 aiohttp 发送实际请求。

        返回 BUFF API 响应的 JSON 数据。
        """
        self._rate_limit()

        # TODO: 在实际部署环境中替换为真实的 HTTP 请求
        # async with httpx.AsyncClient() as client:
        #     resp = await client.get(url, headers=self.headers, params=params)
        #     return resp.json()

        logger.warning("BUFF API 调用需要有效的 Cookie 和网络连接")
        return None

    # ---- 物品列表 ----

    def fetch_goods_list(self, page: int = 1, page_size: int = 80,
                         category: str = None, search: str = None) -> Optional[dict]:
        """获取 BUFF 市场的 CS2 饰品列表

        参数:
            page: 页码（从 1 开始）
            page_size: 每页数量（最大 80）
            category: 品类筛选
            search: 关键词搜索

        返回:
            BUFF API 返回的商品列表 JSON
        """
        params = {"game": "csgo", "page_num": page, "page_size": page_size}
        if category:
            params["category"] = category
        if search:
            params["search"] = search

        return self._request(BUFF_GOODS_LIST, params)

    def fetch_all_goods(self, max_pages: int = 50) -> List[dict]:
        """获取所有 CS2 饰品（分页遍历）

        从第一页开始逐页获取，直到返回空或达到 max_pages。
        每页间隔 request_interval 秒以防被限流。
        """
        all_goods = []
        for page in range(1, max_pages + 1):
            data = self.fetch_goods_list(page=page)
            if not data or "data" not in data:
                break
            items = data["data"].get("items", [])
            if not items:
                break
            all_goods.extend(items)
            logger.info(f"Fetched page {page}: {len(items)} items")
        return all_goods

    # ---- 价格查询 ----

    def fetch_goods_price(self, goods_id: int) -> Optional[dict]:
        """获取单个饰品的价格信息（买入/卖出价）"""
        return self._request(BUFF_GOODS_PRICE.format(goods_id), {"game": "csgo"})

    def fetch_goods_detail(self, goods_id: int) -> Optional[dict]:
        """获取饰品详细信息"""
        return self._request(BUFF_GOODS_DETAIL.format(goods_id))

    # ---- 数据同步 ----

    def sync_to_database(self, db_session, goods_list: List[dict]) -> int:
        """将 BUFF 商品数据同步到 item_definitions 表

        参数:
            db_session: SQLAlchemy 数据库会话
            goods_list: BUFF API 返回的商品列表

        返回:
            新增的物品数量
        """
        from app.models import ItemDefinition
        from app.models import ItemCategory, ItemRarity

        count = 0
        for goods in goods_list:
            market_hash = goods.get("market_hash_name", "")
            if not market_hash:
                continue

            exists = db_session.query(ItemDefinition).filter(
                ItemDefinition.market_hash_name == market_hash
            ).first()
            if exists and exists.buff_id:
                continue  # 已同步过

            category = self._map_category(goods.get("category", ""))
            rarity = self._map_rarity(goods.get("rarity", ""))
            weapon_type = goods.get("wear_category", "") or goods.get("type", "")

            if exists:
                exists.buff_id = goods.get("id")
                exists.rarity_color = goods.get("rarity_color")
                exists.image_url = goods.get("image_url")
            else:
                item = ItemDefinition(
                    name=market_hash,
                    category=category,
                    weapon_type=weapon_type,
                    rarity=rarity,
                    market_hash_name=market_hash,
                    buff_id=goods.get("id"),
                    buff_goods_id=goods.get("original_id"),
                    image_url=goods.get("image_url"),
                    is_tradable=True,
                )
                db_session.add(item)
                count += 1

        db_session.flush()
        return count

    def sync_prices(self, db_session, goods_ids: List[int]) -> int:
        """同步饰品价格到 item_prices 表"""
        from app.models import ItemPrice, PriceSource
        from app.models import ItemDefinition, ItemQuality

        count = 0
        for gid in goods_ids:
            price_data = self.fetch_goods_price(gid)
            if not price_data or "data" not in price_data:
                continue

            items = price_data["data"].get("items", [])
            for item in items:
                # 解析品质
                quality_str = item.get("wear", "").upper()
                try:
                    quality = ItemQuality(quality_str)
                except ValueError:
                    continue

                price = ItemPrice(
                    definition_id=gid,
                    quality=quality,
                    stat_trak=False,
                    source=PriceSource.buff,
                    price_min=item.get("sell_min_price"),
                    price_max=item.get("sell_max_price"),
                    price_avg=item.get("sell_reference_price"),
                    volume_24h=item.get("volume_24h", 0),
                    fetched_at=datetime.utcnow(),
                )
                db_session.add(price)
                count += 1

        db_session.flush()
        return count

    # ---- 辅助方法 ----

    def _map_category(self, buff_category: str) -> str:
        """将 BUFF 品类映射到系统内部品类"""
        mapping = {
            "weapon": "weapon", "knife": "knife", "glove": "gloves",
            "sticker": "sticker", "agent": "agent", "case": "case",
            "key": "key", "music": "other", "pin": "other",
            "graffiti": "other", "patch": "other", "tool": "other",
        }
        return mapping.get(buff_category.lower(), "other")

    def _map_rarity(self, buff_rarity: str) -> str:
        """将 BUFF 稀有度映射到系统内部"""
        mapping = {
            "consumer": "consumer", "industrial": "industrial",
            "mil-spec": "mil_spec", "mil_spec": "mil_spec",
            "restricted": "restricted", "classified": "classified",
            "covert": "covert", "special": "special",
            "exceedingly_rare": "exceedingly_rare",
        }
        return mapping.get(buff_rarity.lower(), "other")
