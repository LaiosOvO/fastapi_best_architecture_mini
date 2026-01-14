"""
文档 CRUD 操作

演示 PGVector 向量查询：
- 向量相似度搜索（余弦距离）
- 全文检索
- 混合检索（RRF 融合）
"""
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import Select, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.demo.model.document import Document
from backend.app.demo.schema.document import CreateDocumentParam, UpdateDocumentParam

from backend.common.embeddings import siliconFlowEmbeddings
from backend.common.log import log

class CRUDDocument(CRUDPlus[Document]):
    """文档数据库操作类"""

    async def get(self, db: AsyncSession, document_id: int) -> Document | None:
        """获取文档详情"""
        return await self.select_model(db, document_id)

    async def get_by_title(self, db: AsyncSession, title: str) -> Document | None:
        """通过标题获取文档"""
        return await self.select_model_by_column(db, title=title)

    async def get_select(
        self,
        category: str | None = None,
        status: int | None = None,
    ) -> Select:
        """获取文档列表查询表达式"""
        filters = {}
        if category:
            filters['category'] = category
        if status is not None:
            filters['status'] = status

        return await self.select_order('id', 'desc', **filters)

    async def create(self, db: AsyncSession, obj: CreateDocumentParam) -> Document:
        """创建文档"""
        dict_obj = obj.model_dump()
        new_document = self.model(**dict_obj)

        if new_document.content:

            embedding = siliconFlowEmbeddings.embed_query(new_document.content)
            new_document.embedding = embedding
            log.info("生成向量 \n embedding: \n",embedding[:10])

        db.add(new_document)
        await db.flush()
        await db.refresh(new_document)
        return new_document

    async def update(
        self,
        db: AsyncSession,
        document_id: int,
        obj: UpdateDocumentParam,
    ) -> int:
        """更新文档"""
        update_data = obj.model_dump(exclude_unset=True)
        return await self.update_model(db, document_id, update_data)

    async def update_embedding(
        self,
        db: AsyncSession,
        document_id: int,
        embedding: list[float],
    ) -> int:
        """更新文档向量嵌入"""
        return await self.update_model(db, document_id, {'embedding': embedding})

    async def update_tsv(
        self,
        db: AsyncSession,
        document_id: int,
        config: str = 'simple',
    ) -> int:
        """
        更新全文检索向量

        Args:
            document_id: 文档 ID
            config: 分词配置（'simple' 或 'chinese'）
        """
        stmt = text("""
            UPDATE demo_document
            SET tsv = to_tsvector(:config, COALESCE(title, '') || ' ' || COALESCE(content, ''))
            WHERE id = :document_id
        """)
        result = await db.execute(stmt, {'config': config, 'document_id': document_id})
        return result.rowcount

    async def delete(self, db: AsyncSession, document_id: int) -> int:
        """删除文档"""
        return await self.delete_model(db, document_id)

    async def vector_search(
        self,
        db: AsyncSession,
        query_embedding: list[float],
        limit: int = 10,
        category: str | None = None,
        threshold: float | None = None,
    ) -> list[dict[str, Any]]:
        """
        向量相似度搜索

        Args:
            query_embedding: 查询向量（与文档 embedding 维度相同）
            limit: 返回数量
            category: 分类过滤
            threshold: 相似度阈值（0-1，越大越相似）

        Returns:
            包含相似度的文档列表
        """
        # 余弦相似度 = 1 - 余弦距离
        similarity = (1 - Document.embedding.cosine_distance(query_embedding)).label('similarity')

        stmt = (
            select(
                Document.id,
                Document.title,
                Document.content,
                Document.category,
                Document.source,
                Document.metadata_,
                Document.status,
                similarity,
            )
            .where(Document.status == 1)
            .where(Document.embedding.isnot(None))
        )

        if category:
            stmt = stmt.where(Document.category == category)

        if threshold is not None:
            # 余弦距离 < (1 - threshold) 等价于 相似度 > threshold
            stmt = stmt.where(Document.embedding.cosine_distance(query_embedding) < (1 - threshold))

        stmt = stmt.order_by(similarity.desc()).limit(limit)

        result = await db.execute(stmt)
        return [dict(row._mapping) for row in result.all()]

    async def fulltext_search(
        self,
        db: AsyncSession,
        query: str,
        config: str = 'simple',
        limit: int = 20,
        category: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        全文检索

        Args:
            query: 搜索词，支持 & (AND), | (OR), ! (NOT)
            config: 分词配置（'simple' 或 'chinese'）
            limit: 返回数量

        Returns:
            包含排名的文档列表
        """
        ts_query = func.to_tsquery(config, query)
        rank = func.ts_rank(Document.tsv, ts_query).label('rank')

        stmt = (
            select(
                Document.id,
                Document.title,
                Document.content,
                Document.category,
                Document.source,
                Document.metadata_,
                Document.status,
                rank,
            )
            .where(Document.status == 1)
            .where(Document.tsv.op('@@')(ts_query))
        )

        if category:
            stmt = stmt.where(Document.category == category)

        stmt = stmt.order_by(rank.desc()).limit(limit)

        result = await db.execute(stmt)
        return [dict(row._mapping) for row in result.all()]

    async def hybrid_search(
        self,
        db: AsyncSession,
        query: str,
        query_embedding: list[float],
        config: str = 'simple',
        limit: int = 10,
        vector_weight: float = 0.5,
    ) -> list[dict[str, Any]]:
        """
        混合检索（全文 + 向量，RRF 融合）

        Args:
            query: 全文搜索词
            query_embedding: 查询向量
            config: 分词配置
            limit: 返回数量
            vector_weight: 向量搜索权重（0-1）

        Returns:
            RRF 融合排序的文档列表
        """
        # RRF (Reciprocal Rank Fusion) 公式: score = sum(1 / (k + rank_i))
        # k 通常取 60
        k = 60

        stmt = text("""
            WITH
            -- 全文检索结果
            fulltext_results AS (
                SELECT id, ROW_NUMBER() OVER (ORDER BY ts_rank(tsv, to_tsquery(:config, :query)) DESC) AS rank
                FROM demo_document
                WHERE status = 1 AND tsv @@ to_tsquery(:config, :query)
                LIMIT :limit * 2
            ),
            -- 向量检索结果
            vector_results AS (
                SELECT id, ROW_NUMBER() OVER (ORDER BY embedding <=> :embedding) AS rank
                FROM demo_document
                WHERE status = 1 AND embedding IS NOT NULL
                LIMIT :limit * 2
            ),
            -- RRF 融合
            rrf_scores AS (
                SELECT
                    COALESCE(f.id, v.id) AS id,
                    COALESCE(1.0 / (:k + f.rank), 0) * (1 - :vector_weight) +
                    COALESCE(1.0 / (:k + v.rank), 0) * :vector_weight AS rrf_score
                FROM fulltext_results f
                FULL OUTER JOIN vector_results v ON f.id = v.id
            )
            SELECT
                d.id, d.title, d.content, d.category, d.source, d.metadata, d.status,
                r.rrf_score
            FROM demo_document d
            JOIN rrf_scores r ON d.id = r.id
            ORDER BY r.rrf_score DESC
            LIMIT :limit
        """)

        result = await db.execute(stmt, {
            'config': config,
            'query': query,
            'embedding': str(query_embedding),
            'k': k,
            'vector_weight': vector_weight,
            'limit': limit,
        })

        return [dict(row._mapping) for row in result.all()]


document_dao: CRUDDocument = CRUDDocument(Document)
