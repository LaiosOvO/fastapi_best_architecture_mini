-- PostgreSQL 扩展初始化脚本
-- 在数据库创建后执行此脚本

-- ==========================================
-- 基础扩展
-- ==========================================

-- UUID 生成
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 加密函数
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 模糊搜索（三元组）
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ==========================================
-- 地理空间 (PostGIS)
-- ==========================================

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- ==========================================
-- 向量搜索 (PGVector)
-- ==========================================

CREATE EXTENSION IF NOT EXISTS vector;

-- ==========================================
-- 时序数据 (TimescaleDB)
-- ==========================================

CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ==========================================
-- 图数据库 (AGE)
-- ==========================================

CREATE EXTENSION IF NOT EXISTS age;
LOAD 'age';
SET search_path = ag_catalog, "$user", public;

-- 创建默认图
SELECT create_graph('default_graph');

-- ==========================================
-- 中文分词 (zhparser) - 可选
-- 如果安装了 zhparser 扩展，取消下面的注释
-- ==========================================

-- CREATE EXTENSION IF NOT EXISTS zhparser;
-- CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = zhparser);
-- ALTER TEXT SEARCH CONFIGURATION chinese ADD MAPPING FOR n,v,a,i,e,l WITH simple;

-- ==========================================
-- 显示已安装的扩展
-- ==========================================

SELECT
    extname AS "扩展名称",
    extversion AS "版本"
FROM pg_extension
ORDER BY extname;

-- ==========================================
-- 验证扩展功能
-- ==========================================

-- 测试 PostGIS
SELECT PostGIS_Version() AS postgis_version;

-- 测试 PGVector
SELECT '[1,2,3]'::vector AS vector_test;

-- 测试 pg_trgm
SELECT similarity('hello', 'helo') AS trgm_test;

-- 测试 UUID
SELECT uuid_generate_v4() AS uuid_test;

SELECT '所有扩展已成功安装！' AS message;
