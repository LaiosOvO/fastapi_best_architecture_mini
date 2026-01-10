# 创建环境（指定 Python 3.10，环境名 admin）
conda create -n admin python=3.10 -y

conda activate admin
 
pip install uv

# 方式 1：直接安装（推荐，uv 会自动解析并安装依赖）
uv pip install -r requirements.txt

# 方式 2（可选）：先同步依赖到虚拟环境，再安装
uv sync --requirements requirements.txt

pip install -r requirements.txt



