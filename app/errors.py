"""Ortak hata formati (proje dokumani Bolum 25).

Tum hata cevaplari su sekildedir:
    {"error": "EVENT_NOT_FOUND", "message": "Event 31 does not exist."}
"""
import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class ApiError(Exception):
    """Servis katmaninin firlattigi, HTTP cevabina donusturulen hata."""

    def __init__(self, status_code: int, error: str, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.error = error
        self.message = message


class NotFoundError(ApiError):
    def __init__(self, error: str, message: str):
        super().__init__(status.HTTP_404_NOT_FOUND, error, message)


class ConflictError(ApiError):
    def __init__(self, error: str, message: str):
        super().__init__(status.HTTP_409_CONFLICT, error, message)


def error_body(error: str, message: str) -> dict:
    return {"error": error, "message": message}


_DEFAULT_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def api_error_handler(request: Request, exc: ApiError):
        return JSONResponse(status_code=exc.status_code, content=error_body(exc.error, exc.message))

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        if isinstance(exc.detail, dict) and "error" in exc.detail:
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        code = _DEFAULT_CODES.get(exc.status_code, "HTTP_ERROR")
        return JSONResponse(status_code=exc.status_code, content=error_body(code, str(exc.detail)))

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        # Dokuman yanlis input icin 400 bekliyor (FastAPI varsayilani 422).
        problems = []
        for err in exc.errors():
            field = ".".join(str(p) for p in err.get("loc", []) if p not in ("body", "query", "path"))
            problems.append(f"{field}: {err.get('msg')}" if field else str(err.get("msg")))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_body("VALIDATION_ERROR", "; ".join(problems) or "Invalid request."),
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_body("INTERNAL_ERROR", "An unexpected error occurred."),
        )
