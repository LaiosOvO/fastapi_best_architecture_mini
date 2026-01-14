from fastapi import APIRouter

from backend.app.demo.api.router import  v1 as demo_v1

router = APIRouter()
router.include_router(demo_v1)


