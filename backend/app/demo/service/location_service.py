"""位置服务层"""
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.demo.crud.crud_location import location_dao
from backend.app.demo.model.location import Location
from backend.app.demo.schema.location import CreateLocationParam, UpdateLocationParam


class LocationService:
    """位置服务类"""

    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> Location:
        """获取位置详情"""
        location = await location_dao.get(db, pk)
        if not location:
            raise ValueError('位置不存在')
        return location

    @staticmethod
    async def get_list(
        *,
        db: AsyncSession,
        category: str | None = None,
        status: int | None = None,
    ) -> list[Location]:
        """获取位置列表"""
        select_stmt = await location_dao.get_select(category=category, status=status)
        result = await db.execute(select_stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateLocationParam) -> Location:
        """创建位置"""
        # 检查名称是否已存在
        existing = await location_dao.get_by_name(db, obj.name)
        if existing:
            raise ValueError('位置名称已存在')

        return await location_dao.create(db, obj)

    @staticmethod
    async def create_mock(
        *,
        db: AsyncSession,
        name: str = '天安门',
        category: str = '景点',
        lng: float = 116.4074,
        lat: float = 39.9042,
    ) -> Location:
        """
        使用 Mock 方法创建位置

        :param db: 数据库会话
        :param name: 位置名称
        :param category: 分类
        :param lng: 经度
        :param lat: 纬度
        :return: Location 实例
        """
        # 使用 Location.mock() 创建实例
        location = Location.mock(name=name, category=category, lng=lng, lat=lat)

        # 保存到数据库
        db.add(location)
        await db.flush()
        await db.refresh(location)

        return location

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateLocationParam) -> int:
        """更新位置"""
        location = await location_dao.get(db, pk)
        if not location:
            raise ValueError('位置不存在')

        # 如果更新名称，检查是否已存在
        if obj.name and obj.name != location.name:
            existing = await location_dao.get_by_name(db, obj.name)
            if existing:
                raise ValueError('位置名称已存在')

        return await location_dao.update(db, pk, obj)

    @staticmethod
    async def delete(*, db: AsyncSession, pk: int) -> int:
        """删除位置"""
        location = await location_dao.get(db, pk)
        if not location:
            raise ValueError('位置不存在')

        return await location_dao.delete(db, pk)

    @staticmethod
    async def search_nearby(
        *,
        db: AsyncSession,
        lng: float,
        lat: float,
        radius: float = 5000,
        category: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        附近搜索

        Args:
            lng: 经度
            lat: 纬度
            radius: 搜索半径（米）
            category: 分类过滤
            limit: 返回数量

        Returns:
            包含距离的位置列表
        """
        return await location_dao.search_nearby(
            db,
            lng=lng,
            lat=lat,
            radius_meters=radius,
            category=category,
            limit=limit,
        )

    @staticmethod
    async def search_in_bounds(
        *,
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
            category: 分类过滤
            limit: 返回数量

        Returns:
            范围内的位置列表
        """
        return await location_dao.search_in_bounds(
            db,
            min_lng=min_lng,
            min_lat=min_lat,
            max_lng=max_lng,
            max_lat=max_lat,
            category=category,
            limit=limit,
        )


location_service: LocationService = LocationService()
