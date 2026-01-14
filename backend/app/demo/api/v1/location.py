"""位置 API 接口"""
from typing import Annotated

from fastapi import APIRouter, Body, Path, Query

from backend.app.demo.schema.location import (
    CreateLocationParam,
    GetLocationDetail,
    GetNearbyLocationDetail,
    UpdateLocationParam,
)
from backend.app.demo.service.location_service import location_service
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('', summary='获取位置列表')
async def get_locations(
    db: CurrentSession,
    category: Annotated[str | None, Query(description='分类')] = None,
    status: Annotated[int | None, Query(description='状态')] = None,
) -> list[GetLocationDetail]:
    """获取位置列表"""
    data = await location_service.get_list(db=db, category=category, status=status)
    return data


@router.get('/nearby', summary='附近位置搜索')
async def search_nearby(
    db: CurrentSession,
    lng: Annotated[float, Query(description='经度', ge=-180, le=180)],
    lat: Annotated[float, Query(description='纬度', ge=-90, le=90)],
    radius: Annotated[float, Query(description='搜索半径（米）', gt=0, le=50000)] = 5000,
    category: Annotated[str | None, Query(description='分类过滤')] = None,
    limit: Annotated[int, Query(description='返回数量', ge=1, le=100)] = 20,
) -> list[GetNearbyLocationDetail]:
    """
    附近位置搜索

    使用 PostGIS 的 ST_DWithin 函数进行空间查询，返回指定半径内的位置，
    按距离升序排列。
    """
    data = await location_service.search_nearby(
        db=db,
        lng=lng,
        lat=lat,
        radius=radius,
        category=category,
        limit=limit,
    )
    return data


@router.get('/bounds', summary='矩形范围内搜索')
async def search_in_bounds(
    db: CurrentSession,
    min_lng: Annotated[float, Query(description='最小经度', ge=-180, le=180)],
    min_lat: Annotated[float, Query(description='最小纬度', ge=-90, le=90)],
    max_lng: Annotated[float, Query(description='最大经度', ge=-180, le=180)],
    max_lat: Annotated[float, Query(description='最大纬度', ge=-90, le=90)],
    category: Annotated[str | None, Query(description='分类过滤')] = None,
    limit: Annotated[int, Query(description='返回数量', ge=1, le=500)] = 100,
) -> list[dict]:
    """
    矩形范围内搜索

    使用 PostGIS 的 ST_Within 和 ST_MakeEnvelope 函数进行空间查询，
    返回指定矩形范围内的所有位置。
    """
    data = await location_service.search_in_bounds(
        db=db,
        min_lng=min_lng,
        min_lat=min_lat,
        max_lng=max_lng,
        max_lat=max_lat,
        category=category,
        limit=limit,
    )
    return data


@router.get('/{pk}', summary='获取位置详情')
async def get_location(
    db: CurrentSession,
    pk: Annotated[int, Path(description='位置 ID')],
) -> GetLocationDetail:
    """获取位置详情"""
    data = await location_service.get(db=db, pk=pk)
    return data


@router.post('', summary='创建位置')
async def create_location(
    db: CurrentSessionTransaction,
    obj: CreateLocationParam,
) -> GetLocationDetail:
    """
    创建位置

    使用 PostGIS 的 ST_SetSRID(ST_MakePoint(lng, lat), 4326) 创建地理点，
    SRID 4326 表示 WGS84 坐标系。
    """
    data = await location_service.create(db=db, obj=obj)
    return data


@router.post('/mock', summary='创建 Mock 位置（用于测试）')
async def create_mock_location(
    db: CurrentSessionTransaction,
    name: Annotated[str, Query(description='位置名称')] = '天安门',
    category: Annotated[str, Query(description='分类')] = '景点',
    lng: Annotated[float, Query(description='经度', ge=-180, le=180)] = 116.4074,
    lat: Annotated[float, Query(description='纬度', ge=-90, le=90)] = 39.9042,
) -> GetLocationDetail:
    """
    创建 Mock 位置（用于测试）

    使用 Location.mock() 方法创建测试数据。
    """
    data = await location_service.create_mock(
        db=db,
        name=name,
        category=category,
        lng=lng,
        lat=lat,
    )
    return data


@router.put('/{pk}', summary='更新位置')
async def update_location(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='位置 ID')],
    obj: UpdateLocationParam,
) -> dict:
    """更新位置"""
    count = await location_service.update(db=db, pk=pk, obj=obj)
    return {'updated': count > 0}


@router.delete('/{pk}', summary='删除位置')
async def delete_location(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='位置 ID')],
) -> dict:
    """删除位置"""
    count = await location_service.delete(db=db, pk=pk)
    return {'deleted': count > 0}
