"""
逻辑删除（软删除）全局过滤器

自动为所有查询添加 deleted=0 的过滤条件
"""

from sqlalchemy import event
from sqlalchemy.orm import Session

from backend.common.log import log


def enable_soft_delete_filter():
    """
    为 Session 启用逻辑删除过滤器

    自动为所有 SELECT 查询添加 deleted=0 条件
    """

    @event.listens_for(Session, 'do_orm_execute')
    def _soft_delete_filter(execute_state):
        """
        在执行查询前自动添加 deleted=0 过滤条件

        仅对 SELECT 查询生效，不影响 INSERT/UPDATE/DELETE
        """
        # 检查是否是查询操作
        if not execute_state.is_select:
            return

        # 检查是否已经禁用软删除过滤（通过 execution_options 标记）
        if execute_state.execution_options.get('include_deleted', False):
            return

        # 获取查询对象
        statement = execute_state.statement

        # 遍历所有被查询的表
        try:
            if hasattr(statement, 'column_descriptions'):
                for mapper in statement.column_descriptions:
                    entity = mapper.get('entity')
                    if entity is None:
                        continue

                    # 检查模型是否有 deleted 字段
                    if hasattr(entity, 'deleted'):
                        # 自动添加 deleted=0 条件
                        statement = statement.where(entity.deleted == 0)

                # 更新查询语句
                execute_state.statement = statement
        except (AttributeError, Exception):
            # 某些查询可能没有 column_descriptions 或其他错误，跳过
            pass


def include_deleted(query):
    """
    在查询中包含已删除的记录

    用法：
        # 正常查询（只返回未删除的）
        result = await db.execute(select(User))

        # 包含已删除的记录
        result = await db.execute(include_deleted(select(User)))

    :param query: SQLAlchemy 查询对象
    :return: 修改后的查询对象
    """
    return query.execution_options(include_deleted=True)


def soft_delete_method(instance):
    """
    软删除方法：标记记录为已删除而不是真正删除

    用法：
        from backend.common.soft_delete import soft_delete_method

        user = await db.get(User, 1)
        soft_delete_method(user)
        await db.commit()

    :param instance: 模型实例
    """
    if hasattr(instance, 'deleted'):
        instance.deleted = 1
        log.info(f'软删除: {instance.__class__.__name__} id={getattr(instance, "id", None)}')
    else:
        raise AttributeError(f'{instance.__class__.__name__} 没有 deleted 字段，无法进行软删除')


def restore_deleted(instance):
    """
    恢复已删除的记录

    用法：
        from backend.common.soft_delete import restore_deleted

        user = await db.get(User, 1)
        restore_deleted(user)
        await db.commit()

    :param instance: 模型实例
    """
    if hasattr(instance, 'deleted'):
        instance.deleted = 0
        log.info(f'恢复删除: {instance.__class__.__name__} id={getattr(instance, "id", None)}')
    else:
        raise AttributeError(f'{instance.__class__.__name__} 没有 deleted 字段，无法恢复')
