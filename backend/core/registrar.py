import os
from backend import __version__

from asyncio import create_task
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi_pagination import add_pagination


from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware


# from backend.common.log import set_custom_logfile, setup_logging
from backend.core.path_conf import STATIC_DIR, UPLOAD_DIR

from backend.core.conf import settings
from backend.utils.serializers import MsgSpecJSONResponse

from fastapi import Depends, FastAPI

from backend.database.db import create_tables


@asynccontextmanager
async def register_init(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    启动初始化

    :param app: FastAPI 应用实例
    :return:
    """
    # 创建数据库表
    await create_tables()

    # 初始化 redis
    # await redis_client.open()
    #
    # # 初始化 limiter
    # await FastAPILimiter.init(
    #     redis=redis_client,
    #     prefix=settings.REQUEST_LIMITER_REDIS_PREFIX,
    #     http_callback=http_limit_callback,
    # )
    #
    # # 初始化 snowflake 节点
    # await snowflake.init()

    # 创建操作日志任务
    # create_task(OperaLogMiddleware.consumer())

    yield

    # 释放 snowflake 节点
    # await snowflake.shutdown()

    # 关闭 redis 连接
    # await redis_client.aclose()


def register_app() -> FastAPI:
    """注册 FastAPI 应用"""

    app = FastAPI(
        title=settings.FASTAPI_TITLE,
        version=__version__,
        description=settings.FASTAPI_DESCRIPTION,
        docs_url=settings.FASTAPI_DOCS_URL,
        redoc_url=settings.FASTAPI_REDOC_URL,
        openapi_url=settings.FASTAPI_OPENAPI_URL,
        default_response_class=MsgSpecJSONResponse,
        lifespan=register_init,
    )

    # 注册组件
    register_logger()
    # register_socket_app(app)
    register_static_file(app)
    register_middleware(app)
    register_router(app)
    register_page(app)
    # register_exception(app)

    # if settings.GRAFANA_METRICS:
    #     register_metrics(app)

    return app


def register_logger() -> None:
    """注册日志"""
    # setup_logging()
    # set_custom_logfile()
    pass


def register_static_file(app: FastAPI) -> None:
    """
    注册静态资源服务

    :param app: FastAPI 应用实例
    :return:
    """
    # 上传静态资源
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    app.mount('/static/upload',
              StaticFiles(directory=UPLOAD_DIR), name='upload')

    # 固有静态资源
    if settings.FASTAPI_STATIC_FILES:
        app.mount('/static',
                  StaticFiles(directory=STATIC_DIR), name='static')


def register_middleware(app: FastAPI) -> None:
    """
    注册中间件（执行顺序从下往上）

    :param app: FastAPI 应用实例
    :return:
    """
    # Opera log
    # app.add_middleware(OperaLogMiddleware)

    # State
    # app.add_middleware(StateMiddleware)

    # JWT auth
    # app.add_middleware(
    #     AuthenticationMiddleware,
    #     backend=JwtAuthMiddleware(),
    #     on_error=JwtAuthMiddleware.auth_exception_handler,
    # )

    # I18n
    # app.add_middleware(I18nMiddleware)

    # Access log
    # app.add_middleware(AccessMiddleware)

    # ContextVar
    # plugins = [OtelTraceIdPlugin()] if settings.GRAFANA_METRICS else [RequestIdPlugin(validate=True)]
    # app.add_middleware(
    #     ContextMiddleware,
    #     plugins=plugins,
    #     default_error_response=MsgSpecJSONResponse(
    #         content={'code': StandardResponseCode.HTTP_400, 'msg': 'BAD_REQUEST', 'data': None},
    #         status_code=StandardResponseCode.HTTP_400,
    #     ),
    # )

    # CORS
    # https://github.com/fastapi-practices/fastapi_best_architecture/pull/789/changes
    # https://github.com/open-telemetry/opentelemetry-python-contrib/issues/4031
    if settings.MIDDLEWARE_CORS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
            expose_headers=settings.CORS_EXPOSE_HEADERS,
        )

def register_router(app: FastAPI) -> None:
    """
    注册路由

    :param app: FastAPI 应用实例
    :return:
    """
    # dependencies = [Depends(demo_site)] if settings.DEMO_MODE else None

    # API
    from backend.app.router import router
    # router = build_final_router()
    router = router
    app.include_router(router,
                       # dependencies=dependencies
                       )

    # Extra
    # ensure_unique_route_names(app)
    # simplify_operation_ids(app)

def register_page(app: FastAPI) -> None:
    """
    注册分页查询功能

    :param app: FastAPI 应用实例
    :return:
    """
    add_pagination(app)

