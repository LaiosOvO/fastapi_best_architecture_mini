"""位置数据验证模式"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class LocationSchemaBase(BaseModel):
    """位置基础模型"""

    name: str = Field(description='位置名称', max_length=128)
    description: str | None = Field(None, description='位置描述')
    address: str | None = Field(None, description='详细地址', max_length=256)
    category: str = Field(description='分类', max_length=64)
    lng: float = Field(description='经度', ge=-180, le=180)
    lat: float = Field(description='纬度', ge=-90, le=90)
    attrs: dict[str, Any] | None = Field(None, description='扩展属性')


class CreateLocationParam(LocationSchemaBase):
    """创建位置参数"""

    pass


class UpdateLocationParam(BaseModel):
    """更新位置参数"""

    name: str | None = Field(None, description='位置名称', max_length=128)
    description: str | None = Field(None, description='位置描述')
    address: str | None = Field(None, description='详细地址', max_length=256)
    category: str | None = Field(None, description='分类', max_length=64)
    lng: float | None = Field(None, description='经度', ge=-180, le=180)
    lat: float | None = Field(None, description='纬度', ge=-90, le=90)
    attrs: dict[str, Any] | None = Field(None, description='扩展属性')
    status: int | None = Field(None, description='状态(0停用 1正常)')


class GetLocationDetail(BaseModel):
    """位置详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='位置 ID')
    name: str = Field(description='位置名称')
    description: str | None = Field(None, description='位置描述')
    address: str | None = Field(None, description='详细地址')
    category: str = Field(description='分类')
    lng: float | None = Field(None, description='经度')
    lat: float | None = Field(None, description='纬度')
    attrs: dict[str, Any] | None = Field(None, description='扩展属性')
    status: int = Field(description='状态')
    created_time: datetime = Field(description='创建时间')
    updated_time: datetime | None = Field(None, description='更新时间')

    @model_validator(mode='before')
    @classmethod
    def extract_coordinates(cls, data: Any) -> Any:
        """从 GeoAlchemy2 的 geom 字段提取经纬度"""
        if isinstance(data, dict):
            return data

        # 处理 ORM 对象
        if hasattr(data, 'geom') and data.geom is not None:
            try:
                from geoalchemy2.shape import to_shape
                from geoalchemy2.elements import WKBElement, WKTElement

                geom = data.geom

                # 如果是 WKTElement，先获取其 WKT 字符串并解析
                if isinstance(geom, WKTElement):
                    # WKTElement 的格式类似 'POINT(lng lat)'
                    wkt_str = str(geom)
                    if wkt_str.startswith('POINT('):
                        # 提取坐标 'POINT(116.4074 39.9042)' -> '116.4074 39.9042'
                        coords = wkt_str[6:-1].split()
                        if len(coords) == 2:
                            data.lng = float(coords[0])
                            data.lat = float(coords[1])
                            return data

                # 如果是 WKBElement（已保存到数据库的）
                point = to_shape(geom)
                data.lng = point.x
                data.lat = point.y
            except Exception:
                # 解析失败时保持 None

                import traceback
                traceback.print_exc()

            pass

        return data


class GetNearbyLocationDetail(BaseModel):
    """附近位置详情（包含距离）"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='位置 ID')
    name: str = Field(description='位置名称')
    description: str | None = Field(None, description='位置描述')
    address: str | None = Field(None, description='详细地址')
    category: str = Field(description='分类')
    lng: float = Field(description='经度')
    lat: float = Field(description='纬度')
    attrs: dict[str, Any] | None = Field(None, description='扩展属性')
    status: int = Field(description='状态')
    distance: float = Field(description='距离（米）')

    @model_validator(mode='before')
    @classmethod
    def extract_coordinates(cls, data: Any) -> Any:
        """从 GeoAlchemy2 的 geom 字段提取经纬度"""
        if isinstance(data, dict):
            return data

        # 处理 ORM 对象
        if hasattr(data, 'geom') and data.geom is not None:
            try:
                from geoalchemy2.shape import to_shape
                from geoalchemy2.elements import WKBElement, WKTElement

                geom = data.geom

                # 如果是 WKTElement，先获取其 WKT 字符串并解析
                if isinstance(geom, WKTElement):
                    wkt_str = str(geom)
                    if wkt_str.startswith('POINT('):
                        coords = wkt_str[6:-1].split()
                        if len(coords) == 2:
                            data.lng = float(coords[0])
                            data.lat = float(coords[1])
                            return data

                # 如果是 WKBElement（已保存到数据库的）
                point = to_shape(geom)
                data.lng = point.x
                data.lat = point.y
            except Exception:
                pass

        return data


class NearbySearchParam(BaseModel):
    """附近搜索参数"""

    lng: float = Field(description='经度', ge=-180, le=180)
    lat: float = Field(description='纬度', ge=-90, le=90)
    radius: float = Field(5000, description='搜索半径（米）', gt=0, le=50000)
    category: str | None = Field(None, description='分类过滤')
    limit: int = Field(20, description='返回数量', ge=1, le=100)


class BoundsSearchParam(BaseModel):
    """矩形范围搜索参数"""

    min_lng: float = Field(description='最小经度', ge=-180, le=180)
    min_lat: float = Field(description='最小纬度', ge=-90, le=90)
    max_lng: float = Field(description='最大经度', ge=-180, le=180)
    max_lat: float = Field(description='最大纬度', ge=-90, le=90)
    category: str | None = Field(None, description='分类过滤')
    limit: int = Field(100, description='返回数量', ge=1, le=500)
