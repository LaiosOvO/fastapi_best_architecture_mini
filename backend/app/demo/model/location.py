"""
位置模型 - 使用 PostGIS 空间数据类型

演示 GIS 功能：
- 点位存储
- 空间索引
- 距离计算
- 范围查询
"""
import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class Location(Base):
    """位置表（PostGIS 空间数据）"""

    __tablename__ = 'demo_location'

    id: Mapped[id_key] = mapped_column(init=False)

    # 必填字段（添加空默认值以兼容 dataclass）
    name: Mapped[str] = mapped_column(sa.String(128), default='', comment='位置名称')
    category: Mapped[str] = mapped_column(sa.String(64), default='', index=True, comment='分类')

    # PostGIS 空间列 - 使用 SRID 4326 (WGS84 坐标系)
    # 存储格式: POINT(lng lat)，如 POINT(116.4074 39.9042)
    geom: Mapped[str] = mapped_column(
        Geometry(geometry_type='POINT', srid=4326),
        default='',
        comment='地理位置点',
    )

    # 有默认值的字段放在后面
    description: Mapped[str | None] = mapped_column(sa.Text, default=None, comment='位置描述')
    address: Mapped[str | None] = mapped_column(sa.String(256), default=None, comment='详细地址')

    # 额外属性（JSONB 存储动态数据）
    attrs: Mapped[dict | None] = mapped_column(
        JSONB,
        default=None,
        comment='扩展属性',
    )

    # 状态
    status: Mapped[int] = mapped_column(default=1, index=True, comment='状态(0停用 1正常)')

    __table_args__ = (
        # GeoAlchemy2 会自动为 Geometry 列创建 GIST 索引，无需手动定义
        {'comment': '位置表（PostGIS 空间数据）'},
    )

    @staticmethod
    def mock(name: str = '天安门', category: str = '景点', lng: float = 116.4074, lat: float = 39.9042):
        """
        创建 Mock 位置数据

        :param name: 位置名称
        :param category: 分类
        :param lng: 经度
        :param lat: 纬度
        :return: Location 实例
        """
        from geoalchemy2.elements import WKTElement

        return Location(
            name=name,
            category=category,
            geom=WKTElement(f'POINT({lng} {lat})', srid=4326),
            description=f'{name}是一个著名的{category}',
            address=f'北京市东城区{name}',
            attrs={'tags': ['热门', '推荐'], 'rating': 4.8},
            status=1,
        )
