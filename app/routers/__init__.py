from fastapi import APIRouter
from .bucket import router as bucket_router
from .image_layered import router as image_layered_router

# 메인 API 라우터 생성
api_router = APIRouter(prefix="/api")

# 서브 라우터들을 메인 라우터에 포함
api_router.include_router(bucket_router, tags=["B2 Storage"])
api_router.include_router(image_layered_router, prefix="/image", tags=["Image Layered"])

__all__ = ["api_router"]