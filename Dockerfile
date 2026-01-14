# ===========================================
# FastAPI Best Architecture Mini - Dockerfile
# ===========================================
#
# 多阶段构建：
# 1. builder: 安装依赖
# 2. runtime: 运行时镜像
#

# ==========================================
# 构建阶段
# ==========================================
FROM python:3.11-slim as builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ==========================================
# 运行时阶段
# ==========================================
FROM python:3.11-slim as runtime

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 从 builder 阶段复制 Python 包
COPY --from=builder /root/.local /root/.local

# 确保 Python 包在 PATH 中
ENV PATH=/root/.local/bin:$PATH

# 复制应用代码
COPY backend /app/backend
COPY pyproject.toml /app/

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# 启动命令
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
