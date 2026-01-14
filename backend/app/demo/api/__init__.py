from fastapi import APIRouter

from backend.app.demo.api.v1.location import router as location_router
from backend.app.demo.api.v1.document import router as document_router

router = APIRouter(prefix='/demo')

router.include_router(location_router, prefix='/locations', tags=['Demo - 位置管理'])
router.include_router(document_router, prefix='/documents', tags=['Demo - 文档管理'])
