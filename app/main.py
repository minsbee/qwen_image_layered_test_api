import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import envs, logger, setup_exception_handlers
from app.routers import api_router
from app.services import image_layered_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행되는 라이프사이클 관리"""
    # Startup
    logger.info("Starting up application...")
    logger.info(f"Environment: {envs.CURRENT_ENV}")
    logger.info(f"Log level: {envs.LOG_LEVEL}")

    if envs.ENABLE_ML_MODEL:
        try:
            logger.info("Attempting to load ML model...")
            await image_layered_service.load_model()
            logger.info("✅ ML model loaded successfully!")
        except Exception as e:
            logger.error(f"❌ Failed to load model on startup: {e}")
            logger.warning("App will start but image layered features may not work")
    else:
        logger.info("ML model loading is disabled (ENABLE_ML_MODEL=false)")

    yield

    # Shutdown
    logger.info("Shutting down application...")


def create_app():
    main_application = FastAPI(title="Fast API", lifespan=lifespan)

    # 통합된 API 라우터 한 번만 포함
    main_application.include_router(api_router)

    setup_exception_handlers(main_application)

    @main_application.get("/")
    async def root():
        return {"message": "Welcome to Fast API!"}

    return main_application


app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
