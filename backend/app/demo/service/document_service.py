"""文档服务层"""
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.demo.crud.crud_document import document_dao
from backend.app.demo.model.document import Document
from backend.app.demo.schema.document import CreateDocumentParam, UpdateDocumentParam


class DocumentService:
    """文档服务类"""

    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> Document:
        """获取文档详情"""
        document = await document_dao.get(db, pk)
        if not document:
            raise ValueError('文档不存在')
        return document

    @staticmethod
    async def get_list(
        *,
        db: AsyncSession,
        category: str | None = None,
        status: int | None = None,
    ) -> list[Document]:
        """获取文档列表"""
        select_stmt = await document_dao.get_select(category=category, status=status)
        result = await db.execute(select_stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateDocumentParam) -> Document:
        """创建文档"""
        document = await document_dao.create(db, obj)
        # 自动更新全文检索向量
        await document_dao.update_tsv(db, document.id)
        return document

    @staticmethod
    async def create_mock(
        *,
        db: AsyncSession,
        title: str = 'FastAPI 最佳实践',
        content: str = 'FastAPI 是一个现代化的 Python Web 框架',
        category: str = '技术文档',
        generate_embedding: bool = True,
    ) -> Document:
        """
        使用 Mock 方法创建文档

        :param db: 数据库会话
        :param title: 文档标题
        :param content: 文档内容
        :param category: 分类
        :param generate_embedding: 是否生成向量嵌入
        :return: Document 实例
        """
        # 使用 Document.mock() 创建实例
        document = await Document.mock(
            title=title,
            content=content,
            category=category,
            generate_embedding=generate_embedding,
        )

        # 保存到数据库
        db.add(document)
        await db.flush()
        await db.refresh(document)

        # 自动更新全文检索向量
        await document_dao.update_tsv(db, document.id)

        return document

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateDocumentParam) -> int:
        """更新文档"""
        document = await document_dao.get(db, pk)
        if not document:
            raise ValueError('文档不存在')

        count = await document_dao.update(db, pk, obj)

        # 如果更新了内容，重新生成全文检索向量
        if obj.title is not None or obj.content is not None:
            await document_dao.update_tsv(db, pk)

        return count

    @staticmethod
    async def update_embedding(
        *,
        db: AsyncSession,
        pk: int,
        embedding: list[float],
    ) -> int:
        """更新文档向量嵌入"""
        document = await document_dao.get(db, pk)
        if not document:
            raise ValueError('文档不存在')

        return await document_dao.update_embedding(db, pk, embedding)

    @staticmethod
    async def delete(*, db: AsyncSession, pk: int) -> int:
        """删除文档"""
        document = await document_dao.get(db, pk)
        if not document:
            raise ValueError('文档不存在')

        return await document_dao.delete(db, pk)

    @staticmethod
    async def vector_search(
        *,
        db: AsyncSession,
        embedding: list[float],
        limit: int = 10,
        category: str | None = None,
        threshold: float | None = None,
    ) -> list[dict[str, Any]]:
        """
        向量相似度搜索

        Args:
            embedding: 查询向量
            limit: 返回数量
            category: 分类过滤
            threshold: 相似度阈值

        Returns:
            包含相似度的文档列表
        """
        return await document_dao.vector_search(
            db,
            query_embedding=embedding,
            limit=limit,
            category=category,
            threshold=threshold,
        )

    @staticmethod
    async def fulltext_search(
        *,
        db: AsyncSession,
        query: str,
        config: str = 'simple',
        limit: int = 20,
        category: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        全文检索

        Args:
            query: 搜索词
            config: 分词配置
            limit: 返回数量
            category: 分类过滤

        Returns:
            包含排名的文档列表
        """
        return await document_dao.fulltext_search(
            db,
            query=query,
            config=config,
            limit=limit,
            category=category,
        )

    @staticmethod
    async def hybrid_search(
        *,
        db: AsyncSession,
        query: str,
        embedding: list[float],
        config: str = 'simple',
        limit: int = 10,
        vector_weight: float = 0.5,
    ) -> list[dict[str, Any]]:
        """
        混合检索

        Args:
            query: 全文搜索词
            embedding: 查询向量
            config: 分词配置
            limit: 返回数量
            vector_weight: 向量搜索权重

        Returns:
            RRF 融合排序的文档列表
        """
        return await document_dao.hybrid_search(
            db,
            query=query,
            query_embedding=embedding,
            config=config,
            limit=limit,
            vector_weight=vector_weight,
        )

    @staticmethod
    async def semantic_search(
        *,
        db: AsyncSession,
        query: str,
        limit: int = 10,
        category: str | None = None,
        threshold: float | None = None,
    ) -> list[dict[str, Any]]:
        """
        语义搜索（自动生成向量）

        用户只需输入搜索文本，系统自动调用硅基流动 API 生成向量并搜索

        Args:
            query: 搜索文本
            limit: 返回数量
            category: 分类过滤
            threshold: 相似度阈值

        Returns:
            包含相似度的文档列表
        """
        from backend.common.embeddings import get_embeddings

        # 调用硅基流动 API 生成向量
        embeddings_service = get_embeddings()
        query_embedding = await embeddings_service.aembed_query(query)

        # 使用生成的向量进行搜索
        return await document_dao.vector_search(
            db,
            query_embedding=query_embedding,
            limit=limit,
            category=category,
            threshold=threshold,
        )


document_service: DocumentService = DocumentService()
