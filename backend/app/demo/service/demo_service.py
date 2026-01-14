from typing import Any
from collections.abc import Sequence

from backend.app.demo.crud.crud_demo import demo_dao
from backend.common.pagination import paging_data
from backend.app.demo.model import Demo
from backend.common.exception import errors
from backend.app.demo.schema.demo import AddDemoParam
from sqlalchemy.ext.asyncio import AsyncSession


class DemoService:


    @staticmethod
    async def getById(*, db: AsyncSession, id: int) -> Demo:
        demo = await demo_dao.get(db, id=id)
        if not demo:
            raise errors.NotFoundError(msg='demo不存在')
        return demo

    @staticmethod
    async def get(*, db: AsyncSession, username: str) -> Demo:
        demo = await demo_dao.get_by_username(db,username)
        if not demo:
            raise errors.NotFoundError(msg='demo不存在')
        return demo

    @staticmethod
    async def get_list(*, db: AsyncSession, filter) -> dict[str, Any]:

        demo_select = await demo_dao.get_select(filter)
        data = await paging_data(db, demo_select)

        return data

    @staticmethod
    async def create(*, db: AsyncSession, obj: AddDemoParam) -> Demo:
        """
        创建用户

        :param db: 数据库会话
        :param obj: 用户添加参数
        :return:
        """
        if await demo_dao.get_by_username(db, obj.username):
            raise errors.ConflictError(msg='用户名已注册')

        await demo_dao.add(db, obj)
        demo = await demo_dao.get_by_username(db, obj.username)
        return demo

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: AddDemoParam) -> int:
        """
        更新用户信息

        :param db: 数据库会话
        :param pk: 用户 ID
        :param obj: 用户更新参数
        :return:
        """
        demo = await demo_dao.get(db, id=pk)
        if not demo:
            raise errors.NotFoundError(msg='用户不存在')

        count = await demo_dao.update(db, demo.id, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, pk: int) -> int:
        """
        删除用户

        :param db: 数据库会话
        :param pk: 用户 ID
        :return:
        """
        demo = await demo_dao.get(db, pk)
        if not demo:
            raise errors.NotFoundError(msg='Demo不存在')
        count = await demo_dao.delete(db, demo.id)
        return count


demo_service = DemoService()
