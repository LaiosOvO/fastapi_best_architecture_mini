from typing import Any

import bcrypt
from backend.app.demo.schema.demo import AddDemoParam

from sqlalchemy import Select, delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus, JoinConfig
from backend.app.demo.model.demo import Demo
from sqlalchemy.ext.asyncio import AsyncSession
from backend.common.log import log

class CRUDDemo(CRUDPlus[Demo]):

    async def get(self, db: AsyncSession, id: int) -> Demo | None:
        """
        获取用户详情

        :param db: 数据库会话
        :param user_id: 用户 ID
        :return:
        """
        return await self.select_model(db, id)

    async def get_by_username(self, db: AsyncSession, username: str) -> Demo | None:
        """
        通过用户名获取用户

        :param db: 数据库会话
        :param username: 用户名
        :return:
        """
        return await self.select_model_by_column(db, username=username)


    async def get_select(self, filter) -> Select:
        """
        获取用户列表查询表达式

        :param dept: 部门 ID
        :param username: 用户名
        :param phone: 电话号码
        :param status: 用户状态
        :return:
        """
        filters = {}

        # if dept:
        #     filters['dept_id'] = dept
        # if username:
        #     filters['username__like'] = f'%{username}%'
        # if phone:
        #     filters['phone__like'] = f'%{phone}%'
        # if status is not None:
        #     filters['status'] = status

        return await self.select_order(
            'id',
            'desc',
            **filters,
        )

    async def add(self, db: AsyncSession, obj: AddDemoParam) -> None:
        """

        :param db: 数据库会话
        :param obj: 添加用户参数
        :return:
        """
        salt = bcrypt.gensalt()

        dict_obj = obj.model_dump(exclude={'roles'})
        dict_obj.update({'salt': salt})
        new_demo = self.model(**dict_obj)

        log.info("param ==> \n" , new_demo)
        db.add(new_demo)
        log.info("domain ==> \n" , new_demo)
        await db.flush()


    async def update(self, db: AsyncSession, id: int, obj: AddDemoParam) -> int:
        """
        更新用户信息

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param obj: 更新用户参数
        :return:
        """
        # role_ids = obj.roles
        # del obj.roles

        count = await self.update_model(db, id, obj)
        return count

    async def update_login_time(self, db: AsyncSession, username: str) -> int:
        """
        更新用户上次登录时间

        :param db: 数据库会话
        :param username: 用户名
        :return:
        """
        return await self.update_model_by_column(db, {'last_login_time': timezone.now()}, username=username)


    async def delete(self, db: AsyncSession, id: int) -> int:
        """
        删除用户

        :param db: 数据库会话
        :param user_id: 用户 ID
        :return:
        """
        return await self.delete_model(db, id)



demo_dao: CRUDDemo = CRUDDemo(Demo)