# FastAPI Admin 完整开发项目 - 参考若依Vue Pro

## 重要说明
- 这是一个大型 Python FastAPI 企业级后台管理系统项目
- 分为两个子项目：单体版 + 微服务版
- 严格按照阶段顺序执行，每完成一个功能就提交代码
- 提交信息**禁止**包含任何 AI 模型相关字样（GPT、Claude、AI生成等）
- 每个步骤都要在 \`docs/tech/step/\` 记录详细实现逻辑
- **只有在所有阶段都完成后，才输出 <promise>FASTAPI_ADMIN_COMPLETE</promise>**
- 在此之前**不要**输出任何 <promise> 标记

---

## 阶段 0：技术调研 - 寻找最佳参考项目

### 任务清单
- [ ] 搜索 FastAPI Admin 开源项目（至少 10 个）
- [ ] 分析每个项目的：
  - 代码可扩展性
  - 架构灵活性
  - 封装优雅性
  - Star 数和活跃度
  - 文档完整性
- [ ] 选出最适合参考的项目（单体版 1-2 个，微服务版 1 个）

### 搜索关键词
- \"fastapi admin\"
- \"fastapi backend\"
- \"fastapi-admin\"
- \"python admin backend\"
- \"fastapi microservices\"
- \"fastapi best practices\"

### 评估标准
为每个项目打分（1-5 分）：
1. **可扩展性**: 是否易于添加新功能
2. **灵活性**: 配置是否灵活，是否支持多数据库
3. **封装优雅性**: 代码组织、依赖注入、错误处理
4. **文档质量**: README、API 文档、开发文档
5. **社区活跃度**: Star 数、Issue 处理、最近更新

### 产出文档
创建 \`docs/research/00_开源项目调研报告.md\`，内容包括：

\`\`\`markdown
# FastAPI Admin 开源项目调研报告

## 单体应用项目

### 1. [项目名称](GitHub链接)
- **Star数**: XXX
- **最近更新**: YYYY-MM-DD
- **技术栈**: FastAPI + SQLAlchemy + Redis...
- **评分**:
  - 可扩展性: 4/5
  - 灵活性: 3/5
  - 封装优雅性: 5/5
  - 文档质量: 4/5
  - 社区活跃度: 3/5
- **优点**:
  - 目录结构清晰
  - 依赖注入做得好
  - 有完整的权限系统
- **缺点**:
  - 缺少微服务支持
  - 数据库支持有限
- **是否推荐**: ✅ 强烈推荐 / ⚠️ 可参考 / ❌ 不推荐

### 2. [项目名称2]...

## 微服务项目

### 1. [项目名称]...

## 最终推荐

### 单体版参考项目
1. **主要参考**: [项目名] - 理由
2. **次要参考**: [项目名] - 理由

### 微服务版参考项目
1. **主要参考**: [项目名] - 理由

## 与 fastapi_best_architecture 的对比
- fastapi_best_architecture 的优势
- 其他项目值得借鉴的地方
\`\`\`

### 本地参考项目分析
同时分析本地项目：
- \`/Volumes/T7/workspace/company/studio/code/admin/python/fastapi_best_architecture\`
  - 架构设计
  - 目录结构
  - 核心功能
  - 可复用模块

### 验收标准
- 至少找到 10 个开源项目
- 每个项目都有详细评分
- 明确推荐单体版和微服务版的参考项目
- 有与 fastapi_best_architecture 的对比分析

**完成后提交**: \`docs: 完成FastAPI Admin开源项目调研\`

---

## 项目目标

基于调研的最佳实践，参考 fastapi_best_architecture 和 ruoyi-vue-pro，构建：
1. **单体版**: 完整的企业级后台管理系统
2. **微服务版**: 分布式微服务架构（基于单体版拆分）

### 技术栈

#### 后端框架
- **语言**: Python 3.11+
- **Web框架**: FastAPI
- **ORM**: SQLAlchemy 2.0 或 Tortoise-ORM
- **数据验证**: Pydantic V2
- **异步**: asyncio + httpx

#### 数据库
- **关系型**:
  - MySQL（主数据库）
  - PostgreSQL（支持 PostGIS 地理信息 + pgvector 向量检索）
- **非关系型**:
  - MongoDB（文档存储）
  - Redis（缓存、Session、分布式锁）
  - Elasticsearch（全文搜索、日志分析）
- **向量数据库**:
  - Milvus（AI Embedding 向量检索）

#### 中间件与工具
- **消息队列**: Kafka（或 RabbitMQ）
- **定时任务**: APScheduler 或 Celery
- **API文档**: Swagger UI (FastAPI 自带)
- **日志**: Loguru
- **配置**: Pydantic Settings
- **认证**: JWT (python-jose)

#### AI 集成
- 参考 xiaozhi-server 的实现
- 支持多 AI 模型（OpenAI、Claude、本地模型）
- 实现对话管理、上下文记忆

#### 参考项目
1. **架构参考**: 调研阶段选定的最佳项目 + fastapi_best_architecture
2. **接口规范**: /Volumes/T7/workspace/company/studio/code/admin/ruoyi-vue-pro
3. **AI 集成**: xiaozhi-server

---

## 项目结构设计

### 单体版目录结构
\`\`\`
fastapi-admin-pro/
├── app/
│   ├── api/                    # API 路由
│   │   └── v1/
│   │       ├── system/         # 系统管理
│   │       ├── infra/          # 基础设施
│   │       └── ai/             # AI 功能
│   ├── core/                   # 核心功能
│   │   ├── config.py           # 配置管理
│   │   ├── security.py         # 安全相关（JWT等）
│   │   ├── database.py         # 数据库连接
│   │   └── deps.py             # 依赖注入
│   ├── models/                 # 数据模型
│   │   ├── base.py             # 基础模型
│   │   └── system/
│   ├── schemas/                # Pydantic schemas
│   │   └── system/
│   ├── services/               # 业务逻辑
│   │   └── system/
│   ├── middleware/             # 中间件
│   │   ├── auth.py
│   │   ├── cors.py
│   │   ├── rate_limit.py
│   │   └── logging.py
│   ├── utils/                  # 工具函数
│   └── plugins/                # 插件（参考 ruoyi starter）
│       ├── mysql/
│       ├── postgresql/
│       ├── mongodb/
│       ├── redis/
│       ├── elasticsearch/
│       ├── milvus/
│       ├── kafka/
│       ├── oss/                # 文件上传
│       ├── scheduler/          # 定时任务
│       ├── ai/                 # AI 集成
│       ├── dataperm/           # 数据权限
│       ├── dict/               # 字典管理
│       └── operlog/            # 操作日志
├── tests/                      # 测试
├── alembic/                    # 数据库迁移
├── docs/                       # 文档
│   ├── research/               # 调研文档
│   ├── tech/                   # 技术文档
│   │   ├── step/               # 实现步骤
│   │   ├── api/                # API 文档
│   │   └── architecture/       # 架构文档
│   └── sql/                    # SQL 脚本
├── scripts/                    # 脚本
├── docker/                     
│   └── docker-compose.yaml
├── .env.example
├── pyproject.toml
├── requirements.txt
├── main.py
└── README.md
\`\`\`

### 微服务版目录结构（后续阶段）
\`\`\`
fastapi-admin-microservices/
├── services/
│   ├── gateway/                # API 网关
│   ├── auth/                   # 认证服务
│   ├── system/                 # 系统管理服务
│   ├── file/                   # 文件服务
│   ├── ai/                     # AI 服务
│   └── job/                    # 定时任务服务
├── common/                     # 公共代码
│   ├── models/
│   ├── schemas/
│   └── utils/
├── deploy/
│   ├── kubernetes/
│   └── docker-compose.yaml
└── docs/
\`\`\`

---

## 阶段 1：项目初始化（单体版）

### 任务清单
- [ ] 创建项目目录结构（参考调研的最佳项目）
- [ ] 初始化 Git 仓库
- [ ] 配置 pyproject.toml 和 requirements.txt
- [ ] 编写项目 README.md
- [ ] 创建基础文档结构

### 依赖管理
使用 Poetry 或 pip：
\`\`\`toml
[tool.poetry.dependencies]
python = \"^3.11\"
fastapi = \"^0.109.0\"
uvicorn = {extras = [\"standard\"], version = \"^0.27.0\"}
sqlalchemy = \"^2.0.0\"
pydantic = \"^2.5.0\"
pydantic-settings = \"^2.1.0\"
alembic = \"^1.13.0\"
python-jose = {extras = [\"cryptography\"], version = \"^3.3.0\"}
passlib = {extras = [\"bcrypt\"], version = \"^1.7.4\"}
python-multipart = \"^0.0.6\"
loguru = \"^0.7.2\"
httpx = \"^0.26.0\"
redis = {extras = [\"hiredis\"], version = \"^5.0.0\"}
motor = \"^3.3.0\"  # MongoDB async
aiomysql = \"^0.2.0\"
asyncpg = \"^0.29.0\"  # PostgreSQL async
elasticsearch = {extras = [\"async\"], version = \"^8.11.0\"}
pymilvus = \"^2.3.0\"
aiokafka = \"^0.10.0\"
apscheduler = \"^3.10.0\"
# ... 其他依赖
\`\`\`

### Git 提交规范
\`\`\`
<type>(<scope>): <subject>

type:
- init: 初始化
- feat: 新功能
- fix: 修复
- docs: 文档
- refactor: 重构
- test: 测试
- chore: 构建/工具

示例:
init: 项目初始化，创建基础目录结构
feat(config): 实现配置文件加载功能
docs(step): 添加配置加载实现文档
\`\`\`

**禁止在提交信息中出现**: AI、GPT、Claude、ChatGPT、生成、模型等字样

### 产出文档
- \`docs/tech/01_技术选型说明.md\`
- \`docs/tech/02_项目架构设计.md\`
- \`docs/tech/03_接口规范文档.md\`（参考 ruoyi-vue-pro）
- \`docs/tech/04_数据库设计.md\`

### 验收标准
- 项目结构清晰
- 依赖配置完成
- 文档齐全

**完成后提交**: \`init: 项目初始化，创建基础架构\`

**记录文档**: \`docs/tech/step/01_项目初始化.md\`

---

## 阶段 2：配置文件加载

### 任务清单
- [ ] 使用 Pydantic Settings 管理配置
- [ ] 支持 .env 文件
- [ ] 支持环境变量覆盖
- [ ] 分环境配置（dev/test/prod）
- [ ] 配置验证

### 实现要求
\`\`\`python
# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseSettings):
    mysql_host: str = \"localhost\"
    mysql_port: int = 3306
    mysql_user: str = \"root\"
    mysql_password: str
    mysql_database: str = \"fastapi_admin\"
    
    postgresql_host: str = \"localhost\"
    postgresql_extensions: list[str] = [\"postgis\", \"vector\"]
    
    mongodb_uri: str = \"mongodb://localhost:27017\"
    
    redis_host: str = \"localhost\"
    redis_port: int = 6379
    
    elasticsearch_url: str = \"http://localhost:9200\"
    
    milvus_host: str = \"localhost\"
    milvus_port: int = 19530
    
    model_config = SettingsConfigDict(
        env_file=\".env\",
        case_sensitive=False,
        extra=\"ignore\"
    )

class KafkaSettings(BaseSettings):
    brokers: list[str] = [\"localhost:9092\"]
    
class AISettings(BaseSettings):
    enabled: bool = True
    provider: str = \"openai\"
    api_key: str
    model: str = \"gpt-4\"

class Settings(BaseSettings):
    # App
    app_name: str = \"FastAPI Admin Pro\"
    debug: bool = False
    api_v1_prefix: str = \"/api/v1\"
    
    # Security
    secret_key: str
    algorithm: str = \"HS256\"
    access_token_expire_minutes: int = 30
    
    # Database
    database: DatabaseSettings = DatabaseSettings()
    
    # Kafka
    kafka: KafkaSettings = KafkaSettings()
    
    # AI
    ai: AISettings = AISettings()
    
    model_config = SettingsConfigDict(
        env_file=\".env\",
        case_sensitive=False
    )

settings = Settings()
\`\`\`

### 验收标准
- 可以从 .env 加载配置
- 配置有类型验证
- 支持嵌套配置
- 有配置文档说明

**完成后提交**: \`feat(config): 实现配置文件加载功能\`

**记录文档**: \`docs/tech/step/02_配置文件加载.md\`
- Pydantic Settings 使用
- 配置结构设计
- 环境变量优先级
- 配置验证逻辑

---

## 阶段 3：数据库配置与连接池

### 子阶段 3.1：MySQL 集成

#### 任务清单
- [ ] 配置 SQLAlchemy 异步引擎
- [ ] 实现连接池
- [ ] 创建 Base 模型
- [ ] 实现数据库会话管理
- [ ] 创建 plugin/mysql/

#### 实现
\`\`\`python
# app/plugins/mysql/mysql.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

class MySQLPlugin:
    def __init__(self, settings):
        db_url = f\"mysql+aiomysql://{settings.database.mysql_user}:{settings.database.mysql_password}@{settings.database.mysql_host}:{settings.database.mysql_port}/{settings.database.mysql_database}\"
        
        self.engine = create_async_engine(
            db_url,
            echo=settings.debug,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True
        )
        
        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def get_session(self):
        async with self.async_session() as session:
            yield session
\`\`\`

#### 验收标准
- 可以连接 MySQL
- 连接池正常工作
- 有错误处理

**完成后提交**: \`feat(plugin): 实现MySQL数据库插件\`

**记录文档**: \`docs/tech/step/03_MySQL集成.md\`

### 子阶段 3.2：PostgreSQL 集成（含 PostGIS + pgvector）

#### 任务清单
- [ ] 配置 asyncpg
- [ ] 启用 PostGIS 扩展
- [ ] 启用 pgvector 扩展
- [ ] 实现地理信息查询示例
- [ ] 实现向量检索示例
- [ ] 创建 plugin/postgresql/

#### 实现
\`\`\`python
# app/plugins/postgresql/postgresql.py
from sqlalchemy.ext.asyncio import create_async_engine

class PostgreSQLPlugin:
    def __init__(self, settings):
        db_url = f\"postgresql+asyncpg://...\"
        self.engine = create_async_engine(db_url)
    
    async def enable_extensions(self):
        async with self.engine.begin() as conn:
            await conn.execute(text(\"CREATE EXTENSION IF NOT EXISTS postgis\"))
            await conn.execute(text(\"CREATE EXTENSION IF NOT EXISTS vector\"))

# app/plugins/postgresql/postgis.py
# PostGIS 地理信息查询封装

# app/plugins/postgresql/pgvector.py
# pgvector 向量检索封装
\`\`\`

**完成后提交**: \`feat(plugin): 实现PostgreSQL插件及PostGIS、pgvector扩展\`

**记录文档**: \`docs/tech/step/04_PostgreSQL及扩展集成.md\`

### 子阶段 3.3：MongoDB 集成

#### 实现
\`\`\`python
# app/plugins/mongodb/mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient

class MongoDBPlugin:
    def __init__(self, settings):
        self.client = AsyncIOMotorClient(settings.database.mongodb_uri)
        self.db = self.client.get_default_database()
\`\`\`

**完成后提交**: \`feat(plugin): 实现MongoDB插件\`

**记录文档**: \`docs/tech/step/05_MongoDB集成.md\`

### 子阶段 3.4：Redis 集成

#### 实现
\`\`\`python
# app/plugins/redis/redis.py
import redis.asyncio as aioredis

class RedisPlugin:
    def __init__(self, settings):
        self.redis = aioredis.from_url(
            f\"redis://{settings.database.redis_host}:{settings.database.redis_port}\",
            encoding=\"utf-8\",
            decode_responses=True
        )
    
    async def get(self, key: str):
        return await self.redis.get(key)
    
    async def set(self, key: str, value: str, expire: int = None):
        await self.redis.set(key, value, ex=expire)

# app/plugins/redis/cache.py
# 缓存装饰器封装
\`\`\`

**完成后提交**: \`feat(plugin): 实现Redis插件及缓存封装\`

**记录文档**: \`docs/tech/step/06_Redis集成.md\`

### 子阶段 3.5：Elasticsearch 集成

\`\`\`python
# app/plugins/elasticsearch/elasticsearch.py
from elasticsearch import AsyncElasticsearch

class ElasticsearchPlugin:
    def __init__(self, settings):
        self.es = AsyncElasticsearch([settings.database.elasticsearch_url])
\`\`\`

**完成后提交**: \`feat(plugin): 实现Elasticsearch插件\`

**记录文档**: \`docs/tech/step/07_Elasticsearch集成.md\`

### 子阶段 3.6：Milvus 集成

\`\`\`python
# app/plugins/milvus/milvus.py
from pymilvus import connections, Collection

class MilvusPlugin:
    def __init__(self, settings):
        connections.connect(
            alias=\"default\",
            host=settings.database.milvus_host,
            port=settings.database.milvus_port
        )
\`\`\`

**完成后提交**: \`feat(plugin): 实现Milvus向量数据库插件\`

**记录文档**: \`docs/tech/step/08_Milvus集成.md\`

---

## 阶段 4：ORM 与基础模型

### 任务清单
- [ ] 定义 Base 模型类
- [ ] 实现软删除
- [ ] 实现审计字段（创建/更新时间、创建/更新人）
- [ ] 实现数据库迁移（Alembic）
- [ ] 参考 ruoyi-vue-pro 定义核心表

### 基础模型
\`\`\`python
# app/models/base.py
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean, String
from sqlalchemy.ext.declarative import declared_attr

class BaseModel:
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)  # 软删除
    is_deleted = Column(Boolean, default=False)
    
    @declared_attr
    def __tablename__(cls):
        # 自动生成表名
        return cls.__name__.lower()

class AuditModel(BaseModel):
    create_by = Column(Integer)
    update_by = Column(Integer)
    remark = Column(String(500))
\`\`\`

### 核心表（参考 ruoyi-vue-pro）
\`\`\`python
# app/models/system/user.py
class User(AuditModel, Base):
    __tablename__ = \"system_user\"
    
    username = Column(String(30), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    nickname = Column(String(30))
    email = Column(String(50))
    mobile = Column(String(11))
    sex = Column(Integer)  # 0=男,1=女,2=未知
    avatar = Column(String(500))
    status = Column(Integer, default=0)  # 0=正常,1=停用
    login_ip = Column(String(50))
    login_date = Column(DateTime)

# app/models/system/role.py
class Role(AuditModel, Base):
    __tablename__ = \"system_role\"
    
    name = Column(String(30), nullable=False)
    code = Column(String(100), unique=True, nullable=False)
    sort = Column(Integer, default=0)
    status = Column(Integer, default=0)
    data_scope = Column(Integer, default=1)  # 数据范围

# app/models/system/menu.py
class Menu(AuditModel, Base):
    __tablename__ = \"system_menu\"
    
    name = Column(String(50), nullable=False)
    parent_id = Column(Integer, default=0)
    type = Column(Integer, nullable=False)  # 1=目录,2=菜单,3=按钮
    path = Column(String(200))
    component = Column(String(255))
    permission = Column(String(100))
    icon = Column(String(100))
    sort = Column(Integer, default=0)
    visible = Column(Boolean, default=True)
    status = Column(Integer, default=0)

# ... 其他表（dept, post, user_role, role_menu 等）
\`\`\`

### Alembic 迁移
\`\`\`bash
alembic init alembic
alembic revision --autogenerate -m \"create system tables\"
alembic upgrade head
\`\`\`

**完成后提交**: \`feat(model): 实现基础模型及系统核心表\`

**记录文档**: \`docs/tech/step/09_ORM与模型设计.md\`

---

## 阶段 5：依赖注入与会话管理

### 任务清单
- [ ] 实现数据库会话依赖
- [ ] 实现当前用户依赖
- [ ] 实现分页依赖
- [ ] 实现权限依赖

\`\`\`python
# app/core/deps.py
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    # JWT 解析并获取用户
    pass

def get_pagination(page: int = 1, size: int = 10):
    return {\"page\": page, \"size\": size}
\`\`\`

**完成后提交**: \`feat(core): 实现依赖注入系统\`

**记录文档**: \`docs/tech/step/10_依赖注入.md\`

---

## 阶段 6：中间件配置

### 任务清单
- [ ] CORS 中间件
- [ ] 日志中间件（Loguru）
- [ ] 请求追踪中间件
- [ ] 限流中间件
- [ ] 异常处理中间件

\`\`\`python
# app/middleware/logging.py
from loguru import logger

@app.middleware(\"http\")
async def log_requests(request: Request, call_next):
    logger.info(f\"{request.method} {request.url}\")
    response = await call_next(request)
    logger.info(f\"Status: {response.status_code}\")
    return response
\`\`\`

**完成后提交**: \`feat(middleware): 实现核心中间件\`

**记录文档**: \`docs/tech/step/11_中间件实现.md\`

---

## 阶段 7：JWT 认证实现

### 任务清单
- [ ] 生成 JWT Token
- [ ] 验证 Token
- [ ] 刷新 Token
- [ ] Token 黑名单（Redis）
- [ ] 密码加密（bcrypt）

\`\`\`python
# app/core/security.py
from passlib.context import CryptContext
from jose import JWTError, jwt

pwd_context = CryptContext(schemes=[\"bcrypt\"], deprecated=\"auto\")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({\"exp\": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
\`\`\`

**完成后提交**: \`feat(security): 实现JWT认证功能\`

**记录文档**: \`docs/tech/step/12_JWT认证实现.md\`

---

## 阶段 8：用户管理模块（完全对齐 ruoyi-vue-pro）
请你查看ruoyi-vue-pro具体实现的路由

### 任务清单
- [ ] 实现用户 CRUD
- [ ] 用户登录/登出
- [ ] 用户信息查询
- [ ] 用户分页查询
- [ ] 用户状态管理
- [ ] 密码修改

### 接口规范（与 ruoyi-vue-pro 完全一致）

#### Response 格式
\`\`\`python
# app/schemas/response.py
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    code: int = 0
    data: Optional[T] = None
    msg: str = \"操作成功\"

class PageResponse(BaseModel, Generic[T]):
    list: list[T]
    total: int
\`\`\`

#### 用户接口
\`\`\`python
# app/api/v1/system/user.py
from fastapi import APIRouter, Depends

router = APIRouter(prefix=\"/system/user\", tags=[\"用户管理\"])

@router.get(\"/page\", response_model=Response[PageResponse[UserOut]])
async def get_user_page(
    page_no: int = 1,
    page_size: int = 10,
    username: Optional[str] = None,
    mobile: Optional[str] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 实现分页查询
    pass

@router.get(\"/get\")
async def get_user(id: int, db: AsyncSession = Depends(get_db)):
    pass

@router.post(\"/create\")
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    pass

@router.put(\"/update\")
async def update_user(user: UserUpdate, db: AsyncSession = Depends(get_db)):
    pass

@router.delete(\"/delete\")
async def delete_user(id: int, db: AsyncSession = Depends(get_db)):
    pass

# app/api/v1/system/auth.py
@router.post(\"/auth/login\")
async def login(credentials: LoginRequest):
    # 返回格式: {\"code\": 0, \"data\": {\"token\": \"xxx\", \"expiresTime\": 123}}
    pass
\`\`\`

### 目录结构
\`\`\`
app/
├── api/v1/system/
│   ├── user.py
│   ├── auth.py
│   ├── role.py
│   └── menu.py
├── schemas/system/
│   ├── user.py
│   ├── role.py
│   └── menu.py
├── services/system/
│   ├── user.py
│   ├── role.py
│   └── menu.py
└── models/system/
    ├── user.py
    ├── role.py
    └── menu.py
\`\`\`

**完成后提交**: \`feat(system): 实现用户管理模块\`

**记录文档**: \`docs/tech/step/13_用户管理实现.md\`
- 详细说明与 ruoyi-vue-pro 的接口对应关系
- Schema 设计
- Service 层实现逻辑

---

## 阶段 9：角色管理模块
请你查看ruoyi-vue-pro具体实现的路由

**接口**: 完全对齐 ruoyi-vue-pro
\`\`\`
GET    /api/v1/system/role/page
GET    /api/v1/system/role/get
POST   /api/v1/system/role/create
PUT    /api/v1/system/role/update
DELETE /api/v1/system/role/delete
GET    /api/v1/system/role/list-all-simple
\`\`\`

**完成后提交**: \`feat(system): 实现角色管理模块\`

**记录文档**: \`docs/tech/step/14_角色管理实现.md\`

---

## 阶段 10：菜单管理模块
请你查看ruoyi-vue-pro具体实现的路由
**接口**: 支持树形结构
\`\`\`
GET    /api/v1/system/menu/list
GET    /api/v1/system/menu/get
POST   /api/v1/system/menu/create
PUT    /api/v1/system/menu/update
DELETE /api/v1/system/menu/delete
GET    /api/v1/system/permission/list-user-permissions
\`\`\`

**完成后提交**: \`feat(system): 实现菜单管理模块\`

**记录文档**: \`docs/tech/step/15_菜单管理实现.md\`

---

## 阶段 11：部门管理模块

**完成后提交**: \`feat(system): 实现部门管理模块\`

**记录文档**: \`docs/tech/step/16_部门管理实现.md\`

---

## 阶段 12：文件上传功能

### 任务清单
- [ ] 本地存储
- [ ] MinIO/S3 存储
- [ ] 阿里云 OSS（可选）
- [ ] 文件类型验证
- [ ] 大小限制
- [ ] 创建 plugin/oss/

\`\`\`python
# app/plugins/oss/oss.py
from abc import ABC, abstractmethod

class OSSInterface(ABC):
    @abstractmethod
    async def upload(self, file, filename: str) -> str:
        pass

class LocalOSS(OSSInterface):
    async def upload(self, file, filename: str) -> str:
        # 本地存储实现
        pass

class MinIOOSS(OSSInterface):
    async def upload(self, file, filename: str) -> str:
        # MinIO 实现
        pass

# app/api/v1/infra/file.py
@router.post(\"/file/upload\")
async def upload_file(file: UploadFile):
    # 返回: {\"code\": 0, \"data\": {\"url\": \"http://...\", \"fileName\": \"xxx\"}}
    pass
\`\`\`

**完成后提交**: \`feat(infra): 实现文件上传功能及OSS插件\`

**记录文档**: \`docs/tech/step/17_文件上传实现.md\`

---

## 阶段 13：Kafka 消息队列

\`\`\`python
# app/plugins/kafka/kafka.py
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

class KafkaPlugin:
    async def produce(self, topic: str, message: dict):
        pass
    
    async def consume(self, topic: str):
        pass
\`\`\`

**完成后提交**: \`feat(plugin): 实现Kafka消息队列插件\`

**记录文档**: \`docs/tech/step/18_Kafka集成.md\`

---

## 阶段 14：定时任务

\`\`\`python
# app/plugins/scheduler/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class SchedulerPlugin:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
    
    def add_job(self, func, trigger, **kwargs):
        self.scheduler.add_job(func, trigger, **kwargs)
\`\`\`

**完成后提交**: \`feat(plugin): 实现定时任务调度插件\`

**记录文档**: \`docs/tech/step/19_定时任务实现.md\`

---

## 阶段 15：AI 集成（参考 xiaozhi-server）

### 任务清单
- [ ] 研究 xiaozhi-server 的实现
- [ ] 支持多 AI 模型（OpenAI、Claude、本地模型）
- [ ] 实现对话管理
- [ ] 实现上下文记忆
- [ ] 实现流式响应
- [ ] 创建 plugin/ai/

### 技术文档要求
必须详细记录 xiaozhi-server 的实现方案：

\`\`\`python
# app/plugins/ai/ai.py
from abc import ABC, abstractmethod

class AIInterface(ABC):
    @abstractmethod
    async def chat(self, message: str, conversation_id: str = None) -> str:
        pass
    
    @abstractmethod
    async def chat_stream(self, message: str, conversation_id: str = None):
        # 流式响应
        pass

class OpenAIProvider(AIInterface):
    async def chat(self, message: str, conversation_id: str = None) -> str:
        # 实现
        pass

class ClaudeProvider(AIInterface):
    async def chat(self, message: str, conversation_id: str = None) -> str:
        # 实现
        pass

# app/plugins/ai/conversation.py
class ConversationManager:
    \"\"\"对话历史管理\"\"\"
    async def get_history(self, conversation_id: str):
        pass
    
    async def save_message(self, conversation_id: str, role: str, content: str):
        pass
\`\`\`

### API 接口
\`\`\`python
# app/api/v1/ai/chat.py
@router.post(\"/chat\")
async def chat(request: ChatRequest):
    # 返回: {\"code\": 0, \"data\": {\"reply\": \"...\", \"conversationId\": \"...\"}}
    pass

@router.post(\"/chat/stream\")
async def chat_stream(request: ChatRequest):
    # SSE 流式响应
    pass
\`\`\`

### 技术文档（xiaozhi-server 分析）
\`\`\`markdown
# xiaozhi-server AI 集成方案分析

## 1. 架构设计
- xiaozhi-server 的整体架构
- AI 模块的位置和作用
- 与其他模块的交互

## 2. 对话管理
- 对话上下文如何存储（Redis/数据库）
- 会话 ID 生成策略
- 历史消息管理

## 3. 流式响应实现
- 使用的技术（SSE/WebSocket）
- 如何处理长文本生成
- 前端如何接收

## 4. 多模型支持
- 如何抽象 AI 接口
- 不同模型的适配
- 模型切换策略

## 5. 错误处理
- API 调用失败处理
- 重试机制
- 降级方案

## 6. 性能优化
- 请求队列
- 缓存策略
- 并发控制
\`\`\`

**完成后提交**: \`feat(ai): 实现AI对话集成\`

**记录文档**: 
- \`docs/tech/step/20_AI集成实现.md\`
- \`docs/tech/xiaozhi_server_分析.md\`（详细分析 xiaozhi-server）

---

## 阶段 16：Ruoyi Starter 功能移植到 Plugin

### 任务清单
参考 ruoyi-vue-pro 的下面所有的 starter 模块，实现以下 plugin：

- [ ] plugin/dataperm/（数据权限）
- [ ] plugin/dict/（字典管理）
- [ ] plugin/operlog/（操作日志）
- [ ] plugin/errorcode/（错误码管理）
- [ ] plugin/security/（安全增强）
等
### 数据权限插件
\`\`\`python
# app/plugins/dataperm/dataperm.py
class DataPermissionPlugin:
    \"\"\"
    数据权限过滤
    支持：部门、角色、用户、自定义
    \"\"\"
    async def filter_query(self, query, user, scope: str):
        # 根据数据范围过滤查询
        pass
\`\`\`

### 字典管理插件
\`\`\`python
# app/plugins/dict/dict.py
class DictPlugin:
    \"\"\"字典数据管理\"\"\"
    async def get_dict_data(self, dict_type: str):
        # 从缓存或数据库获取字典数据
        pass
\`\`\`

### 操作日志插件
\`\`\`python
# app/plugins/operlog/operlog.py
class OperationLogPlugin:
    \"\"\"操作日志记录\"\"\"
    def log_operation(self, user, module: str, action: str, detail: str):
        # 记录操作日志
        pass
\`\`\`

**每个插件独立提交**:
- \`feat(plugin): 实现数据权限插件\`
- \`feat(plugin): 实现字典管理插件\`
- \`feat(plugin): 实现操作日志插件\`
- \`feat(plugin): 实现错误码管理插件\`

**记录文档**: 
- \`docs/tech/step/21_数据权限实现.md\`
- \`docs/tech/step/22_字典管理实现.md\`
- \`docs/tech/step/23_操作日志实现.md\`
- \`docs/tech/step/24_错误码管理实现.md\`

---

## 阶段 17：单体版集成测试

### 任务清单
- [ ] 编写单元测试（pytest）
- [ ] 编写集成测试
- [ ] API 测试（httpx）
- [ ] 性能测试（locust）

\`\`\`python
# tests/api/test_user.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_user_login():
    async with AsyncClient(app=app, base_url=\"http://test\") as ac:
        response = await ac.post(\"/api/v1/system/auth/login\", json={
            \"username\": \"admin\",
            \"password\": \"123456\"
        })
        assert response.status_code == 200
        assert response.json()[\"code\"] == 0
\`\`\`

**完成后提交**: \`test: 添加单元测试和集成测试\`

**记录文档**: \`docs/tech/step/25_测试实现.md\`

---

## 阶段 18：Docker 部署（单体版）

### docker-compose.yaml
\`\`\`yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: fastapi_admin
    
  postgresql:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_PASSWORD: password
  
  mongodb:
    image: mongo:6
  
  redis:
    image: redis:7
  
  elasticsearch:
    image: elasticsearch:8.8.0
    environment:
      discovery.type: single-node
  
  milvus:
    image: milvusdb/milvus:latest
  
  kafka:
    image: confluentinc/cp-kafka:latest
  
  app:
    build: .
    ports:
      - \"8000:8000\"
    depends_on:
      - mysql
      - postgresql
      - mongodb
      - redis
      - elasticsearch
      - milvus
\`\`\`

**完成后提交**: \`feat(deploy): 添加Docker部署配置\`

**记录文档**: \`docs/tech/step/26_Docker部署.md\`

---

## 阶段 19：文档完善（单体版）

### 任务清单
- [ ] API 文档（Swagger 自动生成）
- [ ] 部署文档
- [ ] 开发文档
- [ ] 数据库设计文档
- [ ] 插件使用文档

**完成后提交**: \`docs: 完善项目文档\`

---

## 阶段 20：微服务版拆分（基于单体版）

### 任务清单
- [ ] 设计微服务架构
- [ ] 服务拆分：
  - gateway（API 网关 - Kong/Nginx）
  - auth-service（认证服务）
  - system-service（系统管理）
  - file-service（文件服务）
  - ai-service（AI 服务）
  - job-service（定时任务服务）
- [ ] 服务间通信（gRPC/HTTP）
- [ ] 服务注册与发现（Consul/Nacos）
- [ ] 配置中心（Consul/Nacos）
- [ ] 分布式追踪（Jaeger）

**记录文档**: 
- \`docs/tech/microservices/01_架构设计.md\`
- \`docs/tech/microservices/02_服务拆分方案.md\`

---

## 阶段 21：最终验收

### 验收清单

#### 单体版
- [ ] 所有核心功能实现
- [ ] 接口与 ruoyi-vue-pro 完全一致
- [ ] 所有数据库正常运行
- [ ] AI 功能正常（参考 xiaozhi-server）
- [ ] Docker 一键部署
- [ ] 文档齐全

#### 微服务版
- [ ] 服务拆分合理
- [ ] 服务间通信正常
- [ ] 配置中心正常
- [ ] 可以独立部署

**只有在所有验收通过后，才输出: <promise>FASTAPI_ADMIN_COMPLETE</promise>**

**最终文档**: \`docs/tech/27_项目总结.md\`

---

## 执行规则

1. **先完成阶段 0 的调研**（最重要）
2. **严格按阶段顺序**: 0 → 1 → 2 → ... → 21
3. **每完成一个功能就提交**
4. **提交信息规范**（禁止 AI 字样）
5. **文档同步**（每步都记录）
6. **接口完全对齐** ruoyi-vue-pro
7. **详细分析 xiaozhi-server**（AI 部分）
8. **Plugin 独立可用**

---

## 进度跟踪

创建 \`PROGRESS.md\`:

\`\`\`markdown
# 开发进度

## 调研阶段
- [ ] 阶段 0: 开源项目调研 ⏳

## 单体版开发
- [ ] 阶段 1: 项目初始化
- [ ] 阶段 2: 配置加载
...

## 推荐参考项目
### 单体版
- 主要参考: [待填写]
- 次要参考: [待填写]

### 微服务版
- 主要参考: [待填写]

## 提交次数
已提交: 0 次
\`\`\`

---

**现在立即开始执行阶段 0：技术调研**

请先搜索并分析 FastAPI Admin 开源项目，找出最佳实践。

