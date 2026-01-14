from typing import Annotated

from fastapi import APIRouter, Path, Query, Request

from backend.database.db import CurrentSession, CurrentSessionTransaction
from backend.app.demo.service.demo_service import demo_service
from backend.app.demo.model.demo import Demo
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.pagination import DependsPagination, PageData
from backend.app.demo.schema.demo import AddDemoParam, GetDemoDetail

router = APIRouter()

@router.get('/{id}', summary='id获取实体')
async def get_by_Id(
    db: CurrentSession,
    id: Annotated[int, Path(description='ID')]
) -> ResponseSchemaModel[GetDemoDetail]:
    data = await demo_service.getById(db=db, id=id)
    return response_base.success(data=data)


@router.get(
    '',
    summary='分页列表',
    dependencies=[
        DependsPagination,
    ],
)
async def get_demo_paginated(
    db: CurrentSession,
    filter: dict
) -> ResponseSchemaModel[PageData[GetDemoDetail]]:
    page_data = await demo_service.get_list(db=db, filter=filter)
    return response_base.success(data=page_data)

@router.post('/create', summary='创建demo')
async def create_demo(
    db: CurrentSessionTransaction,
    obj: AddDemoParam
) -> ResponseSchemaModel[GetDemoDetail]:
    req = AddDemoParam.mock()
    await demo_service.create(db=db, obj=req)
    data = await demo_service.get(db=db, username=req.username)
    return response_base.success(data=data)


@router.put('/{pk}', summary='更新demo信息')
async def update_demo(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='用户 ID')],
    obj: AddDemoParam,
) -> ResponseModel:
    count = await demo_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    path='/{pk}',
    summary='删除',
)
async def delete_user(db: CurrentSessionTransaction, pk: Annotated[int, Path(description='用户 ID')]) -> ResponseModel:
    count = await demo_service.delete(db=db, pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()

