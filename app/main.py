import uvicorn
from fastapi import FastAPI
from app.config import envs, logger, setup_exception_handlers
from app.routers import api_router


def create_app():
    main_application = FastAPI(title="Fast API")

    logger.info(f"Environment: {envs.CURRENT_ENV}")
    logger.info(f"Log level: {envs.LOG_LEVEL}")

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
