"""复杂业务逻辑 API 接口 - 演示跨表查询和服务依赖注入"""
from typing import Annotated, List

from fastapi import APIRouter, Body, Path

from backend.app.demo.schema.demo import GetDemoDetail
from backend.app.demo.schema.document import GetDocumentDetail
from backend.app.demo.schema.location import GetLocationDetail
from backend.app.demo.service.demo_complex_service import demo_complex_service
from backend.database.db import CurrentSession, CurrentSessionTransaction
from backend.common.response.response_schema import ResponseSchemaModel, response_base

router = APIRouter()


@router.get('/{demo_id}/with-documents-locations', summary='获取demo及其关联的文档和位置')
async def get_demo_with_documents_and_locations(
    db: CurrentSession,
    demo_id: Annotated[int, Path(description='Demo ID')],
) -> ResponseSchemaModel[dict[str, object]]:
    """
    根据ID查询demo，并根据demo中的document_ids查询相关文档和位置信息
    
    :param db: 数据库会话
    :param demo_id: demo ID
    :return: 包含demo、文档列表和位置列表的字典
    """
    result = await demo_complex_service.get_demo_with_documents_and_locations(
        db=db, 
        demo_id=demo_id
    )
    return response_base.success(data=result)


@router.post('/create-with-documents-locations', summary='创建demo及关联的文档和位置')
async def create_demo_with_documents_and_locations(
    db: CurrentSessionTransaction,
    demo_data: dict = Body(..., description='Demo数据'),
    documents_data: List[dict] = Body([], description='文档数据列表'),
    locations_data: List[dict] = Body([], description='位置数据列表'),
) -> ResponseSchemaModel[dict[str, object]]:
    """
    创建demo以及关联的文档和位置
    
    :param db: 数据库会话
    :param demo_data: demo数据
    :param documents_data: 文档数据列表
    :param locations_data: 位置数据列表
    :return: 包含创建的demo、文档和位置的字典
    """
    result = await demo_complex_service.create_demo_with_documents_and_locations(
        db=db,
        demo_data=demo_data,
        documents_data=documents_data,
        locations_data=locations_data
    )
    return response_base.success(data=result)