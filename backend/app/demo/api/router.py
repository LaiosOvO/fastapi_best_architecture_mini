from fastapi import APIRouter


from backend.app.demo.api.v1.document import router as document_router
from backend.app.demo.api.v1.location import router as location_router
from backend.app.demo.api.v1.demo import router as demo_router
from backend.app.demo.api.v1.demo_complex import router as demo_complex_router

from backend.core.conf import settings


v1 = APIRouter(prefix=settings.FASTAPI_API_V1_PATH)

v1.include_router(document_router, prefix='/documents', tags=['文档管理'])
v1.include_router(location_router, prefix='/locations', tags=['位置管理'])
v1.include_router(demo_router, prefix='/demo', tags=['demo管理'])
v1.include_router(demo_complex_router, prefix='/demo-complex', tags=['demo复杂操作'])

