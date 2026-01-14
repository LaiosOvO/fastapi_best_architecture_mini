# PostgreSQL 全能数据库 Docker 部署指南

PostgreSQL 通过丰富的扩展插件生态，可以胜任几乎所有数据库场景。

> **"一专多长"**: 
> PostgreSQL = OLTP + OLAP + 时序 + GIS + 全文检索 + JSON文档 + 图 + 向量

---

## 一、插件生态全景

### 1.1 核心插件矩阵

| 插件 | 定位 | 对标产品 | 典型场景 |
|------|------|---------|---------|
| **PostGIS** | 地理时空数据库 | MongoDB Geo、专业 GIS | 地图应用、位置服务、轨迹分析 |
| **TimescaleDB** | 时序数据库 | InfluxDB、TDengine | IoT、监控、金融行情 |
| **Citus** | 分布式/HTAP | TiDB、CockroachDB | 大数据分析、多租户 SaaS |
| **PGVector** | AI 向量数据库 | Milvus、Pinecone | 语义搜索、RAG、推荐系统 |
| **AGE** | 图数据库 | Neo4j、JanusGraph | 社交网络、知识图谱、欺诈检测 |
| **pg_trgm** | 模糊搜索 | Elasticsearch | 搜索建议、拼写纠错 |
| **zhparser** | 中文分词 | IK Analyzer | 中文全文检索 |

### 1.2 内置能力

| 能力 | 说明 | 对标 |
|------|------|------|
| **JSONB** | 二进制 JSON，支持索引 | MongoDB |
| **全文检索** | tsvector/tsquery | Elasticsearch |
| **数组类型** | 原生数组支持 | NoSQL |
| **hstore** | 键值对存储 | Redis Hash |
| **范围类型** | 时间/数值范围 | 专用时序库 |
| **物化视图** | 预计算 OLAP | ClickHouse |

---

## 二、Docker 快速部署

### 2.1 方式一：docker-compose（推荐）

```bash
# 启动所有服务（包含所有扩展）
docker-compose up -d

# 仅启动数据库
docker-compose up -d postgres redis

# 查看日志
docker-compose logs -f postgres

# 停止服务
docker-compose down
```

### 2.2 方式二：构建全能镜像

```bash
# 构建包含所有扩展的镜像
docker build -f Dockerfile.postgres -t fba-postgres:16 .

# 运行容器
docker run -d \
  --name fba-postgres \
  -e POSTGRES_DB=fba_mini \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  fba-postgres:16
```

### 2.3 方式三：使用预构建镜像

#### PostGIS 镜像
```bash
docker run -d \
  --name postgres-postgis \
  -e POSTGRES_DB=fba_mini \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgis/postgis:16-3.4
```

#### PGVector 镜像
```bash
docker run -d \
  --name postgres-pgvector \
  -e POSTGRES_DB=fba_mini \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  ankane/pgvector:v0.7.4-pg16
```

#### TimescaleDB 镜像
```bash
docker run -d \
  --name postgres-timescale \
  -e POSTGRES_DB=fba_mini \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  timescale/timescaledb:latest-pg16
```

---

## 三、各插件 Docker 安装详解

### 3.1 PostGIS（地理空间）

**使用官方镜像：**

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgis/postgis:16-3.4
    environment:
      POSTGRES_DB: fba_mini
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

**手动安装到现有容器：**

```dockerfile
# Dockerfile
FROM postgres:16

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-16-postgis-3 \
    postgresql-16-postgis-3-scripts \
    && rm -rf /var/lib/apt/lists/*
```

**启用扩展：**

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS postgis_raster;

-- 验证
SELECT PostGIS_Version();
```

---

### 3.2 TimescaleDB（时序数据）

**使用官方镜像：**

```yaml
services:
  postgres:
    image: timescale/timescaledb:latest-pg16
    environment:
      POSTGRES_DB: fba_mini
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
```

**手动安装到现有容器：**

```dockerfile
FROM postgres:16

# 添加 TimescaleDB 源
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    lsb-release \
    && echo "deb https://packagecloud.io/timescale/timescaledb/debian/ $(lsb_release -cs) main" \
    > /etc/apt/sources.list.d/timescaledb.list \
    && curl -fsSL https://packagecloud.io/timescale/timescaledb/gpgkey \
    | gpg --dearmor -o /etc/apt/trusted.gpg.d/timescaledb.gpg \
    && apt-get update \
    && apt-get install -y --no-install-recommends timescaledb-2-postgresql-16 \
    && rm -rf /var/lib/apt/lists/*

# 配置 shared_preload_libraries
RUN echo "shared_preload_libraries = 'timescaledb'" >> /usr/share/postgresql/postgresql.conf.sample
```

**启用扩展：**

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 验证
SELECT * FROM timescaledb_information.hypertables;
```

---

### 3.3 PGVector（向量搜索）

**使用官方镜像：**

```yaml
services:
  postgres:
    image: ankane/pgvector:v0.7.4-pg16
    environment:
      POSTGRES_DB: fba_mini
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
```

**手动安装（从源码编译）：**

```dockerfile
FROM postgres:16

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    postgresql-server-dev-16 \
    && cd /tmp \
    && git clone --branch v0.7.4 https://github.com/pgvector/pgvector.git \
    && cd pgvector \
    && make \
    && make install \
    && cd .. \
    && rm -rf pgvector \
    && apt-get purge -y --auto-remove build-essential git postgresql-server-dev-16 \
    && rm -rf /var/lib/apt/lists/*
```

**启用扩展：**

```sql
CREATE EXTENSION IF NOT EXISTS vector;

-- 验证
SELECT '[1,2,3]'::vector;
```

---

### 3.4 AGE（图数据库）

**手动安装（需从源码编译）：**

```dockerfile
FROM postgres:16

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    postgresql-server-dev-16 \
    libreadline-dev \
    bison \
    flex \
    && cd /tmp \
    && git clone https://github.com/apache/age.git \
    && cd age \
    && git checkout release/PG16/1.5.0 \
    && make \
    && make install \
    && cd .. \
    && rm -rf age \
    && apt-get purge -y --auto-remove build-essential git postgresql-server-dev-16 \
    && rm -rf /var/lib/apt/lists/*

# 配置 shared_preload_libraries
RUN echo "shared_preload_libraries = 'age'" >> /usr/share/postgresql/postgresql.conf.sample
```

**启用扩展：**

```sql
CREATE EXTENSION IF NOT EXISTS age;
LOAD 'age';
SET search_path = ag_catalog, "$user", public;

-- 创建图
SELECT create_graph('my_graph');

-- 验证
SELECT * FROM ag_catalog.ag_graph;
```

---

### 3.5 Citus（分布式数据库）

**使用官方镜像（单节点）：**

```bash
docker run -d \
  --name citus-master \
  -e POSTGRES_DB=fba_mini \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -v citus_data:/var/lib/postgresql/data \
  citusdata/citus:12.1-pg16
```

**docker-compose 单节点配置：**

```yaml
services:
  postgres:
    image: citusdata/citus:12.1-pg16
    container_name: citus-master
    environment:
      POSTGRES_DB: fba_mini
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - citus_data:/var/lib/postgresql/data

volumes:
  citus_data:
```

**docker-compose 集群配置（1 主 2 从）：**

```yaml
version: '3.8'

services:
  # 协调节点（主节点）
  citus-master:
    image: citusdata/citus:12.1-pg16
    container_name: citus-master
    environment:
      POSTGRES_DB: fba_mini
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - citus_master_data:/var/lib/postgresql/data
    networks:
      - citus-network
    command: ["postgres", "-c", "shared_preload_libraries=citus"]

  # 工作节点 1
  citus-worker-1:
    image: citusdata/citus:12.1-pg16
    container_name: citus-worker-1
    environment:
      POSTGRES_DB: fba_mini
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - citus_worker1_data:/var/lib/postgresql/data
    networks:
      - citus-network
    command: ["postgres", "-c", "shared_preload_libraries=citus"]

  # 工作节点 2
  citus-worker-2:
    image: citusdata/citus:12.1-pg16
    container_name: citus-worker-2
    environment:
      POSTGRES_DB: fba_mini
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - citus_worker2_data:/var/lib/postgresql/data
    networks:
      - citus-network
    command: ["postgres", "-c", "shared_preload_libraries=citus"]

networks:
  citus-network:
    driver: bridge

volumes:
  citus_master_data:
  citus_worker1_data:
  citus_worker2_data:
```

**初始化集群：**

```bash
# 进入主节点
docker exec -it citus-master psql -U postgres -d fba_mini

# 添加工作节点
SELECT citus_add_node('citus-worker-1', 5432);
SELECT citus_add_node('citus-worker-2', 5432);

# 查看节点状态
SELECT * FROM citus_get_active_worker_nodes();
```

**启用扩展和使用：**

```sql
CREATE EXTENSION IF NOT EXISTS citus;

-- 验证
SELECT citus_version();

-- 创建分布式表（按 tenant_id 分片）
CREATE TABLE orders (
    id BIGSERIAL,
    tenant_id INT NOT NULL,
    order_date TIMESTAMPTZ DEFAULT NOW(),
    total_amount DECIMAL(10, 2)
);
SELECT create_distributed_table('orders', 'tenant_id');

-- 创建参考表（小表，复制到所有节点）
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT,
    price DECIMAL(10, 2)
);
SELECT create_reference_table('products');

-- 列式存储（OLAP 加速）
SELECT alter_table_set_access_method('analytics_events', 'columnar');

-- 查看分片分布
SELECT * FROM citus_shards;
```

**手动安装到现有容器：**

```dockerfile
FROM postgres:16

# 添加 Citus 源
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    ca-certificates \
    && curl https://install.citusdata.com/community/deb.sh | bash \
    && apt-get install -y --no-install-recommends postgresql-16-citus-12.1 \
    && rm -rf /var/lib/apt/lists/*

# 配置 shared_preload_libraries
RUN echo "shared_preload_libraries = 'citus'" >> /usr/share/postgresql/postgresql.conf.sample
```

---

### 3.6 PipelineDB / 流处理

> **注意**: PipelineDB 项目已停止维护，其功能已合并到 TimescaleDB 的连续聚合中。
> 推荐使用 TimescaleDB 连续聚合或 PostgreSQL 触发器实现流处理。

#### 方式一：TimescaleDB 连续聚合（推荐）

```bash
# 使用 TimescaleDB 镜像
docker run -d \
  --name timescale-stream \
  -e POSTGRES_DB=fba_mini \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  timescale/timescaledb:latest-pg16
```

**创建连续聚合（实时统计）：**

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 创建原始数据表
CREATE TABLE request_logs (
    time TIMESTAMPTZ NOT NULL,
    endpoint TEXT,
    status_code INT,
    response_time FLOAT
);

-- 转为超表
SELECT create_hypertable('request_logs', 'time');

-- 创建连续聚合（实时统计）
CREATE MATERIALIZED VIEW realtime_stats
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 minute', time) AS bucket,
    endpoint,
    COUNT(*) AS request_count,
    AVG(response_time) AS avg_response_time,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time) AS p95,
    SUM(CASE WHEN status_code >= 500 THEN 1 ELSE 0 END) AS error_count
FROM request_logs
GROUP BY bucket, endpoint;

-- 设置自动刷新策略（每分钟刷新）
SELECT add_continuous_aggregate_policy('realtime_stats',
    start_offset => INTERVAL '10 minutes',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute'
);

-- 查询实时统计
SELECT * FROM realtime_stats
WHERE bucket > NOW() - INTERVAL '1 hour'
ORDER BY bucket DESC;

-- 滑动窗口查询（最近 5 分钟移动平均）
SELECT
    bucket,
    AVG(avg_response_time) OVER (
        ORDER BY bucket
        ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
    ) AS moving_avg_5min
FROM realtime_stats
ORDER BY bucket DESC
LIMIT 60;
```

#### 方式二：PostgreSQL 触发器实现流处理

```sql
-- 实时计数器表
CREATE TABLE realtime_counters (
    metric_name TEXT PRIMARY KEY,
    value BIGINT DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 流处理触发器函数
CREATE OR REPLACE FUNCTION process_event() RETURNS TRIGGER AS $$
BEGIN
    -- 更新计数器（原子操作）
    INSERT INTO realtime_counters (metric_name, value, updated_at)
    VALUES (NEW.event_type, 1, NOW())
    ON CONFLICT (metric_name) DO UPDATE
    SET value = realtime_counters.value + 1,
        updated_at = NOW();

    -- 错误告警（使用 NOTIFY）
    IF NEW.status_code >= 500 THEN
        PERFORM pg_notify('alerts', json_build_object(
            'type', 'error',
            'endpoint', NEW.endpoint,
            'status', NEW.status_code,
            'time', NOW()
        )::text);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER event_stream_trigger
AFTER INSERT ON request_logs
FOR EACH ROW EXECUTE FUNCTION process_event();

-- 监听告警（Python 示例）
-- import asyncio
-- import asyncpg
-- async def listen_alerts():
--     conn = await asyncpg.connect(...)
--     await conn.add_listener('alerts', lambda conn, pid, channel, payload: print(payload))
--     await asyncio.sleep(3600)
```

#### 方式三：使用旧版 PipelineDB（不推荐，仅供参考）

> PipelineDB 最后支持 PostgreSQL 11，已过时。

```dockerfile
# 仅供参考，不推荐生产使用
FROM postgres:11

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -s http://download.pipelinedb.com/apt.sh | bash \
    && apt-get install -y --no-install-recommends pipelinedb-postgresql-11 \
    && rm -rf /var/lib/apt/lists/*

RUN echo "shared_preload_libraries = 'pipelinedb'" >> /usr/share/postgresql/postgresql.conf.sample
```

```sql
-- PipelineDB 语法（已废弃）
CREATE EXTENSION pipelinedb;

-- 创建流（Stream）
CREATE FOREIGN TABLE events_stream (
    event_type TEXT,
    value INT,
    ts TIMESTAMPTZ
) SERVER pipelinedb;

-- 创建连续视图
CREATE VIEW events_minute WITH (action=materialize) AS
SELECT
    event_type,
    minute(ts) AS minute,
    COUNT(*) AS count,
    AVG(value) AS avg_value
FROM events_stream
GROUP BY event_type, minute;
```

---

### 3.7 pg_trgm（模糊搜索）

**已内置，无需额外安装：**

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 验证
SELECT similarity('hello', 'helo');

-- 创建模糊搜索索引
CREATE INDEX idx_name_trgm ON products USING GIN (name gin_trgm_ops);
```

---

### 3.7 zhparser（中文分词）

**手动安装：**

```dockerfile
FROM postgres:16

# 安装 SCWS 和 zhparser
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    wget \
    postgresql-server-dev-16 \
    && cd /tmp \
    # 安装 SCWS
    && wget -q http://www.xunsearch.com/scws/down/scws-1.2.3.tar.bz2 \
    && tar xf scws-1.2.3.tar.bz2 \
    && cd scws-1.2.3 \
    && ./configure \
    && make \
    && make install \
    && cd .. \
    # 安装 zhparser
    && git clone https://github.com/amutu/zhparser.git \
    && cd zhparser \
    && SCWS_HOME=/usr/local make \
    && make install \
    && cd .. \
    && rm -rf scws-1.2.3* zhparser \
    && apt-get purge -y --auto-remove build-essential git wget postgresql-server-dev-16 \
    && rm -rf /var/lib/apt/lists/*
```

**启用扩展：**

```sql
CREATE EXTENSION IF NOT EXISTS zhparser;

-- 创建中文分词配置
CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = zhparser);
ALTER TEXT SEARCH CONFIGURATION chinese ADD MAPPING FOR n,v,a,i,e,l WITH simple;

-- 验证
SELECT to_tsvector('chinese', '我爱北京天安门');
```

---

### 3.8 其他常用扩展

```sql
-- UUID 生成
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
SELECT uuid_generate_v4();

-- 加密函数
CREATE EXTENSION IF NOT EXISTS pgcrypto;
SELECT crypt('password', gen_salt('bf'));

-- hstore 键值对
CREATE EXTENSION IF NOT EXISTS hstore;
SELECT 'a=>1, b=>2'::hstore;

-- 统计信息
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 外部数据包装器
CREATE EXTENSION IF NOT EXISTS postgres_fdw;
```

---

## 四、完整全能镜像 Dockerfile

```dockerfile
# Dockerfile.postgres
FROM postgres:16-bookworm

LABEL maintainer="FastAPI Best Architecture"
LABEL description="PostgreSQL with all extensions"

# 环境变量
ENV POSTGRES_DB=fba_mini
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    build-essential \
    git \
    wget \
    postgresql-server-dev-16 \
    libreadline-dev \
    bison \
    flex \
    && rm -rf /var/lib/apt/lists/*

# ==========================================
# 1. PostGIS
# ==========================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-16-postgis-3 \
    postgresql-16-postgis-3-scripts \
    && rm -rf /var/lib/apt/lists/*

# ==========================================
# 2. TimescaleDB
# ==========================================
RUN echo "deb https://packagecloud.io/timescale/timescaledb/debian/ $(lsb_release -cs) main" \
    > /etc/apt/sources.list.d/timescaledb.list \
    && curl -fsSL https://packagecloud.io/timescale/timescaledb/gpgkey \
    | gpg --dearmor -o /etc/apt/trusted.gpg.d/timescaledb.gpg \
    && apt-get update \
    && apt-get install -y --no-install-recommends timescaledb-2-postgresql-16 \
    && rm -rf /var/lib/apt/lists/*

# ==========================================
# 3. PGVector（源码编译）
# ==========================================
RUN cd /tmp \
    && git clone --branch v0.7.4 https://github.com/pgvector/pgvector.git \
    && cd pgvector \
    && make \
    && make install \
    && cd .. \
    && rm -rf pgvector

# ==========================================
# 4. AGE 图数据库（源码编译）
# ==========================================
RUN cd /tmp \
    && git clone https://github.com/apache/age.git \
    && cd age \
    && git checkout release/PG16/1.5.0 \
    && make \
    && make install \
    && cd .. \
    && rm -rf age

# ==========================================
# 5. zhparser 中文分词（可选）
# ==========================================
RUN cd /tmp \
    && wget -q http://www.xunsearch.com/scws/down/scws-1.2.3.tar.bz2 \
    && tar xf scws-1.2.3.tar.bz2 \
    && cd scws-1.2.3 \
    && ./configure \
    && make \
    && make install \
    && cd .. \
    && git clone https://github.com/amutu/zhparser.git \
    && cd zhparser \
    && SCWS_HOME=/usr/local make \
    && make install \
    && cd .. \
    && rm -rf scws-1.2.3* zhparser

# ==========================================
# 清理构建依赖
# ==========================================
RUN apt-get purge -y --auto-remove \
    build-essential \
    git \
    wget \
    postgresql-server-dev-16 \
    libreadline-dev \
    bison \
    flex \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ==========================================
# 配置 PostgreSQL
# ==========================================
RUN echo "shared_preload_libraries = 'timescaledb,age'" \
    >> /usr/share/postgresql/postgresql.conf.sample

# 复制初始化脚本
COPY scripts/database/init_extensions.sql /docker-entrypoint-initdb.d/10-init-extensions.sql

EXPOSE 5432
VOLUME ["/var/lib/postgresql/data"]
```

---

## 五、初始化脚本

**scripts/database/init_extensions.sql**

```sql
-- ==========================================
-- PostgreSQL 扩展初始化脚本
-- ==========================================

-- 基础扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS hstore;

-- PostGIS（地理空间）
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- PGVector（向量搜索）
CREATE EXTENSION IF NOT EXISTS vector;

-- TimescaleDB（时序数据）
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- AGE（图数据库）
CREATE EXTENSION IF NOT EXISTS age;
LOAD 'age';
SET search_path = ag_catalog, "$user", public;
SELECT create_graph('default_graph');

-- zhparser（中文分词）- 如果已安装
-- CREATE EXTENSION IF NOT EXISTS zhparser;
-- CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = zhparser);
-- ALTER TEXT SEARCH CONFIGURATION chinese ADD MAPPING FOR n,v,a,i,e,l WITH simple;

-- 验证
SELECT extname AS "扩展名称", extversion AS "版本" FROM pg_extension ORDER BY extname;
```

---

## 六、Docker Compose 完整配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    build:
      context: .
      dockerfile: Dockerfile.postgres
    image: fba-postgres:16
    container_name: fba-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DATABASE_SCHEMA:-fba_mini}
      POSTGRES_USER: ${DATABASE_USER:-postgres}
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD:-postgres}
      TIMESCALEDB_TELEMETRY: 'off'
    ports:
      - "${DATABASE_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/database/init_extensions.sql:/docker-entrypoint-initdb.d/10-init-extensions.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d fba_mini"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - fba-network

  redis:
    image: redis:7-alpine
    container_name: fba-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    ports:
      - "${REDIS_PORT:-6379}:6379"
    volumes:
      - redis_data:/data
    networks:
      - fba-network

networks:
  fba-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

---

## 七、常用操作命令

### 容器管理

```bash
# 启动
docker-compose up -d

# 停止
docker-compose down

# 重建镜像
docker-compose build --no-cache postgres

# 查看日志
docker-compose logs -f postgres

# 进入容器
docker exec -it fba-postgres bash
```

### 数据库操作

```bash
# 连接数据库
docker exec -it fba-postgres psql -U postgres -d fba_mini

# 查看已安装扩展
docker exec -it fba-postgres psql -U postgres -d fba_mini -c "\dx"

# 执行 SQL 文件
docker exec -i fba-postgres psql -U postgres -d fba_mini < script.sql

# 备份
docker exec fba-postgres pg_dump -U postgres fba_mini > backup.sql

# 恢复
docker exec -i fba-postgres psql -U postgres -d fba_mini < backup.sql
```

### 扩展验证

```bash
# PostGIS
docker exec -it fba-postgres psql -U postgres -d fba_mini -c "SELECT PostGIS_Version();"

# PGVector
docker exec -it fba-postgres psql -U postgres -d fba_mini -c "SELECT '[1,2,3]'::vector;"

# TimescaleDB
docker exec -it fba-postgres psql -U postgres -d fba_mini -c "SELECT extversion FROM pg_extension WHERE extname='timescaledb';"

# AGE
docker exec -it fba-postgres psql -U postgres -d fba_mini -c "SELECT * FROM ag_catalog.ag_graph;"

# pg_trgm
docker exec -it fba-postgres psql -U postgres -d fba_mini -c "SELECT similarity('hello', 'helo');"
```

---

## 八、参考链接

- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [PostGIS Docker Hub](https://hub.docker.com/r/postgis/postgis)
- [TimescaleDB Docker](https://docs.timescale.com/self-hosted/latest/install/installation-docker/)
- [PGVector GitHub](https://github.com/pgvector/pgvector)
- [Apache AGE](https://age.apache.org/)
- [Citus Docker](https://hub.docker.com/r/citusdata/citus)
- [zhparser GitHub](https://github.com/amutu/zhparser)
