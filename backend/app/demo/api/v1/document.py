"""文档 API 接口"""
from typing import Annotated

from fastapi import APIRouter, Body, Path, Query

from backend.app.demo.schema.document import (
    CreateDocumentParam,
    GetDocumentDetail,
    GetDocumentSearchDetail,
    UpdateDocumentParam,
    SemanticSearchParam,
)
from backend.app.demo.service.document_service import document_service
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('', summary='获取文档列表')
async def get_documents(
    db: CurrentSession,
    category: Annotated[str | None, Query(description='分类')] = None,
    status: Annotated[int | None, Query(description='状态')] = None,
) -> list[GetDocumentDetail]:
    """获取文档列表"""
    data = await document_service.get_list(db=db, category=category, status=status)
    return data


@router.post('/search/vector', summary='向量相似度搜索')
async def vector_search(
    db: CurrentSession,
    embedding: Annotated[list[float], Body(description='查询向量')],
    limit: Annotated[int, Query(description='返回数量', ge=1, le=100)] = 10,
    category: Annotated[str | None, Query(description='分类过滤')] = None,
    threshold: Annotated[float | None, Query(description='相似度阈值', ge=0, le=1)] = None,
) -> list[GetDocumentSearchDetail]:
    """
    向量相似度搜索

    使用 PGVector 的余弦距离计算文档相似度，返回最相似的文档列表。
    支持 HNSW 索引加速查询。
    """
    data = await document_service.vector_search(
        db=db,
        embedding=embedding,
        limit=limit,
        category=category,
        threshold=threshold,
    )
    return data


@router.get('/search/fulltext', summary='全文检索')
async def fulltext_search(
    db: CurrentSession,
    query: Annotated[str, Query(description='搜索词', min_length=1)],
    config: Annotated[str, Query(description='分词配置（simple/chinese）')] = 'simple',
    limit: Annotated[int, Query(description='返回数量', ge=1, le=100)] = 20,
    category: Annotated[str | None, Query(description='分类过滤')] = None,
) -> list[GetDocumentSearchDetail]:
    """
    全文检索

    使用 PostgreSQL 内置的 tsvector/tsquery 进行全文检索。
    搜索词支持 & (AND), | (OR), ! (NOT) 操作符。

    示例：
    - `python & web`: 同时包含 python 和 web
    - `python | java`: 包含 python 或 java
    - `python & !java`: 包含 python 但不包含 java
    """
    data = await document_service.fulltext_search(
        db=db,
        query=query,
        config=config,
        limit=limit,
        category=category,
    )
    return data


@router.post('/search/hybrid', summary='混合检索')
async def hybrid_search(
    db: CurrentSession,
    query: Annotated[str, Body(description='全文搜索词')],
    embedding: Annotated[list[float], Body(description='查询向量')],
    config: Annotated[str, Query(description='分词配置')] = 'simple',
    limit: Annotated[int, Query(description='返回数量', ge=1, le=100)] = 10,
    vector_weight: Annotated[float, Query(description='向量搜索权重', ge=0, le=1)] = 0.5,
) -> list[GetDocumentSearchDetail]:
    """
    混合检索（全文 + 向量）

    使用 RRF (Reciprocal Rank Fusion) 算法融合全文检索和向量搜索的结果。
    vector_weight 控制向量搜索的权重，0 表示纯全文检索，1 表示纯向量搜索。
    """
    data = await document_service.hybrid_search(
        db=db,
        query=query,
        embedding=embedding,
        config=config,
        limit=limit,
        vector_weight=vector_weight,
    )
    return data


@router.post('/search/semantic', summary='语义搜索（基于文本自动生成向量）')
async def semantic_search(
    db: CurrentSession,
    query: Annotated[str, Body(description='搜索文本', min_length=1)],
    limit: Annotated[int, Query(description='返回数量', ge=1, le=100)] = 10,
    category: Annotated[str | None, Query(description='分类过滤')] = None,
    threshold: Annotated[float | None, Query(description='相似度阈值', ge=0, le=1)] = None,
) -> list[GetDocumentSearchDetail]:
    """
    语义搜索（基于文本自动生成向量）

    用户只需输入搜索文本，系统会自动调用硅基流动 API 生成向量，
    然后进行向量相似度搜索。非常适合终端用户使用。

    示例：
    - 搜索 "如何使用 FastAPI 构建 API"
    - 系统自动生成向量并返回最相关的文档
    """
    data = await document_service.semantic_search(
        db=db,
        query=query,
        limit=limit,
        category=category,
        threshold=threshold,
    )
    return data


@router.get('/{pk}', summary='获取文档详情')
async def get_document(
    db: CurrentSession,
    pk: Annotated[int, Path(description='文档 ID')],
) -> GetDocumentDetail:
    """获取文档详情"""
    data = await document_service.get(db=db, pk=pk)
    return data


@router.post('', summary='创建文档')
async def create_document(
    db: CurrentSessionTransaction,
    obj: CreateDocumentParam,
) -> GetDocumentDetail:
    """
    创建文档

    创建文档后会自动生成全文检索向量（tsv）。
    如果需要支持向量搜索，请在创建时提供 embedding 或后续调用更新接口。
    """
    data = await document_service.create(db=db, obj=obj)
    return data


@router.post('/mock', summary='创建 Mock 文档（用于测试）')
async def create_mock_document(
    db: CurrentSessionTransaction,
    title: Annotated[str, Query(description='文档标题')] = 'FastAPI 最佳实践',
    content: Annotated[str, Query(description='文档内容')] = 'FastAPI 是一个现代化的 Python Web 框架，基于 Starlette 和 Pydantic。',
    category: Annotated[str, Query(description='分类')] = '技术文档',
    generate_embedding: Annotated[bool, Query(description='是否生成向量')] = True,
) -> GetDocumentDetail:
    """
    创建 Mock 文档（用于测试）

    使用 Document.mock() 方法创建测试数据，自动生成向量嵌入。
    """
    data = await document_service.create_mock(
        db=db,
        title=title,
        content=content,
        category=category,
        generate_embedding=generate_embedding,
    )
    return data


@router.put('/{pk}', summary='更新文档')
async def update_document(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='文档 ID')],
    obj: UpdateDocumentParam,
) -> dict:
    """
    更新文档

    如果更新了 title 或 content，会自动重新生成全文检索向量。
    """
    count = await document_service.update(db=db, pk=pk, obj=obj)
    return {'updated': count > 0}


@router.put('/{pk}/embedding', summary='更新文档向量嵌入')
async def update_embedding(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='文档 ID')],
    embedding: Annotated[list[float], Body(description='文档向量嵌入')],
) -> dict:
    """
    更新文档向量嵌入

    用于将外部生成的向量（如 OpenAI text-embedding-3-small）存储到数据库。
    """
    count = await document_service.update_embedding(db=db, pk=pk, embedding=embedding)
    return {'updated': count > 0}


@router.delete('/{pk}', summary='删除文档')
async def delete_document(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='文档 ID')],
) -> dict:
    """删除文档"""
    count = await document_service.delete(db=db, pk=pk)
    return {'deleted': count > 0}
