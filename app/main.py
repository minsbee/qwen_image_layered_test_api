import uvicorn
from fastapi import FastAPI
from app.config import envs, logger, setup_exception_handlers
from app.routers import (
    authorize_b2_router,
    get_upload_url_b2_router,
)


def create_app():
    app = FastAPI(title="Fast API")

    logger.info(f"Environment: {envs.CURRENT_ENV}")
    logger.info(f"Log level: {envs.LOG_LEVEL}")

    app.include_router(
        authorize_b2_router,
        prefix="/api",
        tags=["Authorize_b2"],
    )

    app.include_router(
        get_upload_url_b2_router,
        prefix="/api",
        tags=["Get_upload_url_b2"],
    )

    setup_exception_handlers(app)

    @app.get("/")
    async def root():
        return {"message": "Welcome to Fast API!"}

    return app


main_application = create_app()

if __name__ == "__main__":
    uvicorn.run(main_application, host="0.0.0.0", port=8000, reload=True)