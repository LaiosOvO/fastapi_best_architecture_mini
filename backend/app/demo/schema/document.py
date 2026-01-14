"""文档数据验证模式"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DocumentSchemaBase(BaseModel):
    """文档基础模型"""

    title: str = Field(description='文档标题', max_length=256)
    content: str = Field(description='文档内容')
    category: str | None = Field(None, description='分类', max_length=64)
    source: str | None = Field(None, description='来源', max_length=128)
    metadata_: dict[str, Any] | None = Field(None, alias='metadata', description='文档元数据')


class CreateDocumentParam(DocumentSchemaBase):
    """创建文档参数"""

    embedding: list[float] | None = Field(None, description='文档向量嵌入')


class UpdateDocumentParam(BaseModel):
    """更新文档参数"""

    title: str | None = Field(None, description='文档标题', max_length=256)
    content: str | None = Field(None, description='文档内容')
    category: str | None = Field(None, description='分类', max_length=64)
    source: str | None = Field(None, description='来源', max_length=128)
    metadata_: dict[str, Any] | None = Field(None, alias='metadata', description='文档元数据')
    embedding: list[float] | None = Field(None, description='文档向量嵌入')
    status: int | None = Field(None, description='状态(0停用 1正常)')


class GetDocumentDetail(BaseModel):
    """文档详情"""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(description='文档 ID')
    title: str = Field(description='文档标题')
    content: str = Field(description='文档内容')
    category: str | None = Field(None, description='分类')
    source: str | None = Field(None, description='来源')
    metadata_: dict[str, Any] | None = Field(None, serialization_alias='metadata', description='文档元数据')
    status: int = Field(description='状态')
    created_time: datetime = Field(description='创建时间')
    updated_time: datetime | None = Field(None, description='更新时间')


class GetDocumentSearchDetail(BaseModel):
    """文档搜索结果详情"""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(description='文档 ID')
    title: str = Field(description='文档标题')
    content: str = Field(description='文档内容')
    category: str | None = Field(None, description='分类')
    source: str | None = Field(None, description='来源')
    metadata_: dict[str, Any] | None = Field(None, serialization_alias='metadata', description='文档元数据')
    status: int = Field(description='状态')
    similarity: float | None = Field(None, description='相似度（向量搜索）')
    rank: float | None = Field(None, description='排名分数（全文搜索）')
    rrf_score: float | None = Field(None, description='RRF 融合分数（混合搜索）')


class VectorSearchParam(BaseModel):
    """向量搜索参数"""

    embedding: list[float] = Field(description='查询向量')
    limit: int = Field(10, description='返回数量', ge=1, le=100)
    category: str | None = Field(None, description='分类过滤')
    threshold: float | None = Field(None, description='相似度阈值（0-1）', ge=0, le=1)


class FulltextSearchParam(BaseModel):
    """全文搜索参数"""

    query: str = Field(description='搜索词', min_length=1)
    config: str = Field('simple', description='分词配置（simple/chinese）')
    limit: int = Field(20, description='返回数量', ge=1, le=100)
    category: str | None = Field(None, description='分类过滤')


class HybridSearchParam(BaseModel):
    """混合搜索参数"""

    query: str = Field(description='全文搜索词', min_length=1)
    embedding: list[float] = Field(description='查询向量')
    config: str = Field('simple', description='分词配置（simple/chinese）')
    limit: int = Field(10, description='返回数量', ge=1, le=100)
    vector_weight: float = Field(0.5, description='向量搜索权重（0-1）', ge=0, le=1)


class SemanticSearchParam(BaseModel):
    """语义搜索参数（基于文本自动生成向量）"""

    query: str = Field(description='搜索文本', min_length=1)
    limit: int = Field(10, description='返回数量', ge=1, le=100)
    category: str | None = Field(None, description='分类过滤')
    threshold: float | None = Field(None, description='相似度阈值（0-1）', ge=0, le=1)
