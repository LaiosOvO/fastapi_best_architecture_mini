"""
文档模型 - 使用 PGVector 向量搜索

演示向量功能：
- 向量存储（embedding）
- 向量相似度搜索
- HNSW/IVFFlat 索引
- 混合检索（全文 + 向量）
"""
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class Document(Base):
    """文档表（PGVector 向量搜索）"""

    __tablename__ = 'demo_document'

    id: Mapped[id_key] = mapped_column(init=False)
    title: Mapped[str] = mapped_column(sa.String(256), default='', comment='文档标题')
    content: Mapped[str] = mapped_column(sa.Text, default='', comment='文档内容')
    category: Mapped[str | None] = mapped_column(sa.String(64), default=None, index=True, comment='分类')
    source: Mapped[str | None] = mapped_column(sa.String(128), default=None, comment='来源')

    # PGVector 向量列 - 1024 维（BAAI/bge-large-zh-v1.5 - 硅基流动）
    # 其他常用维度：384（all-MiniLM-L6-v2），1536（OpenAI text-embedding-3-small）
    embedding: Mapped[list | None] = mapped_column(
        Vector(1024),
        default=None,
        comment='文档向量嵌入',
    )

    # 全文检索向量列（PostgreSQL 内置）
    tsv: Mapped[str | None] = mapped_column(
        TSVECTOR,
        default=None,
        comment='全文检索向量',
    )

    # 元数据（JSONB 存储）
    metadata_: Mapped[dict | None] = mapped_column(
        'metadata',
        JSONB,
        default=None,
        comment='文档元数据',
    )

    # 状态
    status: Mapped[int] = mapped_column(default=1, index=True, comment='状态(0停用 1正常)')

    __table_args__ = (
        # 向量索引 - HNSW（适合大数据量，查询快）
        sa.Index(
            'idx_demo_document_embedding_hnsw',
            'embedding',
            postgresql_using='hnsw',
            postgresql_with={'m': 16, 'ef_construction': 64},
            postgresql_ops={'embedding': 'vector_cosine_ops'},
        ),
        # 全文检索索引
        sa.Index('idx_demo_document_tsv', 'tsv', postgresql_using='gin'),
        {'comment': '文档表（PGVector 向量搜索）'},
    )

    @staticmethod
    async def mock(
        title: str = 'FastAPI 最佳实践',
        content: str = 'FastAPI 是一个现代化的 Python Web 框架，基于 Starlette 和 Pydantic。它提供了自动生成 API 文档、类型提示、异步支持等特性。',
        category: str = '技术文档',
        generate_embedding: bool = True,
    ):
        """
        创建 Mock 文档数据

        :param title: 文档标题
        :param content: 文档内容
        :param category: 分类
        :param generate_embedding: 是否生成向量嵌入
        :return: Document 实例
        """
        # 生成向量嵌入
        embedding = None
        if generate_embedding:
            try:
                from backend.common.embeddings import get_embeddings

                embeddings_service = get_embeddings()
                # 将标题和内容组合后生成向量
                text = f"{title}\n{content}"
                embedding = await embeddings_service.aembed_query(text)
            except Exception as e:
                from backend.common.log import log

                log.warning(f"生成向量失败: {e}，跳过向量嵌入")

        # 生成全文检索向量（PostgreSQL tsvector）
        # 注意：这里简化处理，实际应该在数据库触发器中生成
        from sqlalchemy import func

        return Document(
            title=title,
            content=content,
            category=category,
            source='Mock 数据',
            embedding=embedding,
            tsv=None,  # 由数据库触发器自动生成
            metadata_={'author': 'System', 'tags': ['示例', '测试']},
            status=1,
        )
