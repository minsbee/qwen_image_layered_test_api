from fastapi import Request, FastAPI, HTTPException
from fastapi.responses import JSONResponse


def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        from .logger import logger

        logger.error(f"HTTP Exception: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        from .logger import logger

        logger.error(f"Unhandled Exception: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error"},
        )
