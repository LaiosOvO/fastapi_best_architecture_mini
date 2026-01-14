"""
向量嵌入服务 - 硅基流动

使用 LangChain 封装硅基流动的 Embedding API
"""

from typing import List

from langchain_core.embeddings import Embeddings
import httpx

from backend.core.conf import settings
from backend.common.log import log


class SiliconFlowEmbeddings(Embeddings):
    """
    硅基流动 Embeddings 服务

    使用 LangChain Embeddings 接口封装硅基流动 API
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "BAAI/bge-large-zh-v1.5",
        base_url: str = "https://api.siliconflow.cn/v1",
    ):
        """
        初始化硅基流动 Embeddings

        :param api_key: API 密钥
        :param model: 模型名称（默认：BAAI/bge-large-zh-v1.5）
        :param base_url: API 基础 URL
        """
        self.api_key = api_key or getattr(settings, 'SILICONFLOW_API_KEY', '')
        self.model = model
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

        if not self.api_key:
            raise ValueError("SILICONFLOW_API_KEY 未配置")

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        异步嵌入多个文档

        :param texts: 文本列表
        :return: 向量列表
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "input": texts,
                },
            )
            response.raise_for_status()
            data = response.json()

            # 返回嵌入向量
            embeddings = [item["embedding"] for item in data["data"]]
            log.info(f"生成 {len(embeddings)} 个文档向量，维度: {len(embeddings[0])}")
            return embeddings

        except httpx.HTTPStatusError as e:
            log.error(f"硅基流动 API 错误: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            log.error(f"生成向量失败: {e}")
            raise

    async def aembed_query(self, text: str) -> List[float]:
        """
        异步嵌入单个查询

        :param text: 查询文本
        :return: 向量
        """
        embeddings = await self.aembed_documents([text])
        return embeddings[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        同步嵌入多个文档（LangChain 接口）

        :param texts: 文本列表
        :return: 向量列表
        """
        import asyncio

        return asyncio.run(self.aembed_documents(texts))

    def embed_query(self, text: str) -> List[float]:
        """
        同步嵌入单个查询（LangChain 接口）

        :param text: 查询文本
        :return: 向量
        """
        import asyncio

        return asyncio.run(self.aembed_query(text))

    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()


# 全局单例
_embeddings_instance = None


def get_embeddings() -> SiliconFlowEmbeddings:
    """
    获取全局 Embeddings 实例

    :return: SiliconFlowEmbeddings 实例
    """
    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = SiliconFlowEmbeddings()
    return _embeddings_instance


siliconFlowEmbeddings = get_embeddings()