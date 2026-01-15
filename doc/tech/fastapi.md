# FastAPI 基础用法指南

## 1. FastAPI 简介

FastAPI 是一个现代、快速（高性能）的 Web 框架，用于构建 API，基于 Python 3.7+ 的类型提示。

### 主要特性：
- **高性能**：接近 Node.js 和 Go 的性能
- **快速编码**：减少约 40% 的开发时间
- **更少的 Bug**：约 40% 的人为错误
- **直观**：编辑器支持和自动补全
- **简单**：易于理解和使用
- **短小精悍**：代码量少且容易维护
- **标准化**：基于开放 API 和 JSON Schema 标准

## 2. 安装和基本设置

```bash
pip install fastapi uvicorn
```

### 最简单的 FastAPI 应用
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
```

运行应用：
```bash
uvicorn main:app --reload
```

## 3. 路由和路径操作

### 3.1 HTTP 方法
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")          # GET 请求
@app.post("/")         # POST 请求
@app.put("/")          # PUT 请求
@app.delete("/")       # DELETE 请求
@app.patch("/")        # PATCH 请求
@app.options("/")      # OPTIONS 请求
@app.head("/")         # HEAD 请求
@app.trace("/")        # TRACE 请求
```

### 3.2 路径参数
```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

### 3.3 查询参数
```python
@app.get("/items/")
def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# 可选参数
from typing import Optional

@app.get("/items/{item_id}")
def read_item(item_id: str, q: Optional[str] = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}
```

## 4. 请求体和 Pydantic 模型

### 4.1 Pydantic 模型
```python
from pydantic import BaseModel
from typing import Optional

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

@app.post("/items/")
def create_item(item: Item):
    return item
```

### 4.2 嵌套模型
```python
class User(BaseModel):
    username: str
    email: str

class Item(BaseModel):
    name: str
    owner: User

@app.post("/items/")
def create_item_with_owner(item: Item):
    return item
```

## 5. 请求体 - 多个参数

### 5.1 路径参数 + 查询参数 + 请求体
```python
from typing import Optional

@app.put("/items/{item_id}")
def update_item(
    item_id: int,
    item: Item,
    q: Optional[str] = None
):
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result
```

### 5.2 表单数据
```python
from fastapi import Form

@app.post("/login/")
def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}
```

### 5.3 文件上传
```python
from fastapi import File, UploadFile

@app.post("/files/")
def create_file(file: bytes = File(...)):
    return {"file_size": len(file)}

@app.post("/uploadfile/")
def upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}
```

## 6. 响应处理

### 6.1 响应模型
```python
class UserOut(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

@app.post("/user/", response_model=UserOut)
def create_user(user: UserOut):
    return user
```

### 6.2 响应状态码
```python
from fastapi import status

@app.post("/items/", status_code=status.HTTP_201_CREATED)
def create_item(item: Item):
    return item
```

## 7. 依赖注入

### 7.1 简单依赖
```python
from fastapi import Depends

def get_current_user(token: str = Depends(oauth2_scheme)):
    return token

@app.get("/users/me")
def read_users_me(current_user: str = Depends(get_current_user)):
    return {"current_user": current_user}
```

### 7.2 类依赖
```python
class DBSession:
    def __init__(self):
        self.session = "database_session"

def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        # 清理代码
        pass

@app.get("/items/")
def read_items(db: DBSession = Depends(get_db)):
    return {"db": db.session}
```

## 8. 中间件和事件处理器

### 8.1 事件处理器
```python
from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("应用启动")

@app.on_event("shutdown")
async def shutdown_event():
    print("应用关闭")
```

### 8.2 中间件
```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class CustomHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Custom-Header"] = "Value"
        return response

app.add_middleware(CustomHeaderMiddleware)
```

## 9. 异常处理

```python
from fastapi import HTTPException, status

@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id < 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return {"item_id": item_id}
```

### 自定义异常处理器
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": f"Value error: {exc}"}
    )
```

## 10. 路由分组

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/users/{user_id}")
def read_user(user_id: str):
    return {"user_id": user_id}

app.include_router(router, prefix="/api/v1")
```

## 11. 数据验证和错误处理

### 11.1 字段验证
```python
from pydantic import BaseModel, Field
from typing import Optional

class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=300)
    price: float = Field(..., gt=0, description="价格必须大于0")
    tax: Optional[float] = None
```

### 11.2 自定义验证器
```python
from pydantic import BaseModel, validator

class User(BaseModel):
    username: str
    email: str
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('邮箱格式不正确')
        return v
```

## 12. 路径操作配置

```python
@app.get(
    "/items/",
    tags=["items"],
    summary="获取物品列表",
    description="返回所有物品的列表",
    response_description="物品列表",
    deprecated=True  # 标记为废弃
)
def read_items():
    return [{"name": "Foo"}]
```

## 13. 安全性和认证

### 3.1 OAuth2 密码流
```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/users/me")
def read_users_me(token: str = Depends(oauth2_scheme)):
    return {"token": token}
```

## 14. 异步支持

```python
import asyncio
from fastapi import BackgroundTasks

async def send_notification(email: str, message: str):
    # 模拟异步发送通知
    await asyncio.sleep(1)
    print(f"发送邮件到 {email}: {message}")

@app.post("/send-notification/{email}")
async def send_notification_endpoint(
    email: str, background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_notification, email, "你的消息")
    return {"message": "通知将在后台发送"}
```

## 15. 数据库集成示例

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends

# 依赖注入数据库会话
async def get_db():
    async with AsyncSession(engine) as session:
        yield session

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user
```

## 16. 自动 API 文档

FastAPI 自动生成交互式 API 文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 17. 测试

```python
from fastapi.testclient import TestClient

def test_read_main():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}
```

## 18. 项目结构建议

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI 实例
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── users.py
│   │           └── items.py
│   ├── models/          # 数据模型
│   ├── schemas/         # Pydantic 模型
│   ├── database/        # 数据库相关
│   └── utils/           # 工具函数
├── tests/               # 测试文件
├── requirements.txt
└── README.md
```

FastAPI 结合了现代 Python 特性（如类型提示）和异步编程，提供了简洁而强大的 API 开发体验。通过 Pydantic 的数据验证、自动文档生成和高性能的 ASGI 服务器，FastAPI 成为了构建现代 Web API 的优秀选择。