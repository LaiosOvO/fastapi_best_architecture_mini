# FastAPI Admin Pro

企业级 FastAPI 后台管理系统，参考 ruoyi-vue-pro 接口规范

## 🚀 特性

- **现代化架构**: 基于 FastAPI + SQLAlchemy 2.0 + Pydantic V2
- **多数据库支持**: MySQL、PostgreSQL、MongoDB、Redis、Elasticsearch、Milvus
- **完整权限系统**: RBAC + 数据权限 + 行级控制
- **插件化架构**: 灵活的插件系统，支持动态扩展
- **AI 集成**: 支持多 AI 模型对话管理
- **微服务支持**: 支持单体和微服务两种部署模式
- **企业级功能**: 操作日志、字典管理、文件上传、定时任务
- **生产就绪**: Docker 部署、监控告警、性能优化

## 📁 项目结构

```
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
│   └── plugins/                # 插件
│       ├── mysql/
│       ├── postgresql/
│       ├── mongodb/
│       ├── redis/
│       ├── elasticsearch/
│       ├── milvus/
│       ├── kafka/
│       ├── oss/
│       ├── scheduler/
│       ├── ai/
│       ├── dataperm/
│       ├── dict/
│       └── operlog/
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
```

## 🛠️ 技术栈

### 后端框架
- **语言**: Python 3.11+
- **Web框架**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **数据验证**: Pydantic V2
- **异步**: asyncio + httpx

### 数据库
- **关系型**: MySQL、PostgreSQL
- **非关系型**: MongoDB、Redis、Elasticsearch
- **向量数据库**: Milvus

### 中间件与工具
- **消息队列**: Kafka
- **定时任务**: APScheduler
- **API文档**: Swagger UI
- **日志**: Loguru
- **配置**: Pydantic Settings
- **认证**: JWT

## 🚦 快速开始

### 环境要求
- Python 3.11+
- Docker & Docker Compose

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-org/fastapi-admin-pro.git
cd fastapi-admin-pro
```

2. **安装依赖**
```bash
# 使用 uv
uv sync

# 或使用 pip
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息
```

4. **启动数据库服务**
```bash
docker-compose up -d mysql postgresql mongodb redis elasticsearch
```

5. **运行数据库迁移**
```bash
alembic upgrade head
```

6. **启动服务**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port8000
```

7. **访问系统**
- API 文档: http://localhost:8000/docs
- Admin 界面: http://localhost:8000/admin

## 📖 文档

- [开发文档](docs/tech/README.md)
- [API 文档](http://localhost:8000/docs)
- [数据库设计](docs/sql/README.md)
- [部署文档](docs/deploy/README.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [ruoyi-vue-pro](https://github.com/YunaiV/ruoyi-vue-pro) - 接口规范参考
- [starlette-admin](https://github.com/jowilf/starlette-admin) - 架构设计参考
- [fastapi_best_architecture](https://github.com/fastapi-practices/fastapi_best_architecture) - 企业级实践参考
