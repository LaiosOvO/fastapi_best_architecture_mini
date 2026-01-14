"""
位置 CRUD 操作

演示 PostGIS 空间查询：
- 附近搜索（ST_DWithin）
- 距离计算（ST_Distance）
- 范围查询（ST_Within）
- 空间索引使用
"""
from typing import Any

from geoalchemy2.functions import ST_Distance, ST_DWithin, ST_MakePoint, ST_SetSRID, ST_X, ST_Y
from geoalchemy2.types import Geography
from sqlalchemy import Select, func, select, type_coerce
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.demo.model.location import Location
from backend.app.demo.schema.location import CreateLocationParam, UpdateLocationParam


class CRUDLocation(CRUDPlus[Location]):
    """位置数据库操作类"""

    async def get(self, db: AsyncSession, location_id: int) -> Location | None:
        """获取位置详情"""
        return await self.select_model(db, location_id)

    async def get_by_name(self, db: AsyncSession, name: str) -> Location | None:
        """通过名称获取位置"""
        return await self.select_model_by_column(db, name=name)

    async def get_select(
        self,
        category: str | None = None,
        status: int | None = None,
    ) -> Select:
        """获取位置列表查询表达式"""
        filters = {}
        if category:
            filters['category'] = category
        if status is not None:
            filters['status'] = status

        return await self.select_order('id', 'desc', **filters)

    async def create(self, db: AsyncSession, obj: CreateLocationParam) -> Location:
        """
        创建位置

        使用 ST_SetSRID(ST_MakePoint(lng, lat), 4326) 创建地理点
        """
        dict_obj = obj.model_dump(exclude={'lng', 'lat'})
        # 使用 WKT 格式创建点
        dict_obj['geom'] = f'SRID=4326;POINT({obj.lng} {obj.lat})'

        new_location = self.model(**dict_obj)
        db.add(new_location)
        await db.flush()
        await db.refresh(new_location)
        return new_location

    async def update(
        self,
        db: AsyncSession,
        location_id: int,
        obj: UpdateLocationParam,
    ) -> int:
        """更新位置"""
        update_data = obj.model_dump(exclude_unset=True, exclude={'lng', 'lat'})
        if obj.lng is not None and obj.lat is not None:
            update_data['geom'] = f'SRID=4326;POINT({obj.lng} {obj.lat})'

        return await self.update_model(db, location_id, update_data)

    async def delete(self, db: AsyncSession, location_id: int) -> int:
        """删除位置"""
        return await self.delete_model(db, location_id)

    async def search_nearby(
        self,
        db: AsyncSession,
        lng: float,
        lat: float,
        radius_meters: float = 5000,
        category: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        附近搜索

        Args:
            lng: 经度
            lat: 纬度
            radius_meters: 搜索半径（米）
            category: 分类过滤
            limit: 返回数量

        Returns:
            包含距离的位置列表
        """
        # 创建查询点（geography 类型用于球面距离计算）
        point = func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)

        # 计算距离（米）
        distance = func.ST_Distance(
            type_coerce(Location.geom, Geography),
            type_coerce(point, Geography),
        ).label('distance')

        # 构建查询
        stmt = (
            select(
                Location.id,
                Location.name,
                Location.description,
                Location.address,
                Location.category,
                func.ST_X(Location.geom).label('lng'),
                func.ST_Y(Location.geom).label('lat'),
                Location.attrs,
                Location.status,
                distance,
            )
            .where(Location.status == 1)
            .where(
                func.ST_DWithin(
                    type_coerce(Location.geom, Geography),
                    type_coerce(point, Geography),
                    radius_meters,
                )
            )
        )

        if category:
            stmt = stmt.where(Location.category == category)

        stmt = stmt.order_by(distance).limit(limit)

        result = await db.execute(stmt)
        return [dict(row._mapping) for row in result.all()]

    async def search_in_bounds(
        self,
        db: AsyncSession,
        min_lng: float,
        min_lat: float,
        max_lng: float,
        max_lat: float,
        category: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        矩形范围内搜索

        Args:
            min_lng: 最小经度
            min_lat: 最小纬度
            max_lng: 最大经度
            max_lat: 最大纬度

        Returns:
            范围内的位置列表
        """
        # 创建边界框
        envelope = func.ST_MakeEnvelope(min_lng, min_lat, max_lng, max_lat, 4326)

        stmt = (
            select(
                Location.id,
                Location.name,
                Location.description,
                Location.address,
                Location.category,
                func.ST_X(Location.geom).label('lng'),
                func.ST_Y(Location.geom).label('lat'),
                Location.attrs,
                Location.status,
            )
            .where(Location.status == 1)
            .where(func.ST_Within(Location.geom, envelope))
        )

        if category:
            stmt = stmt.where(Location.category == category)

        stmt = stmt.limit(limit)

        result = await db.execute(stmt)
        return [dict(row._mapping) for row in result.all()]


location_dao: CRUDLocation = CRUDLocation(Location)
