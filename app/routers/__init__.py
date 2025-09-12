from fastapi import APIRouter
from .bucket import router as bucket_router

# 메인 API 라우터 생성
api_router = APIRouter(prefix="/api")

# 서브 라우터들을 메인 라우터에 포함
api_router.include_router(bucket_router, tags=["B2 Storage"])

__all__ = ["api_router"]