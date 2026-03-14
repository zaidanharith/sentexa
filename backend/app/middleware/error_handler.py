import logging
from collections.abc import Sequence
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.middleware.request_context import get_request_id

logger = logging.getLogger(__name__)

def _build_error_payload(
    detail: str, errors: Sequence[Any] | None = None
) -> dict[str, Any]:
    payload: dict[str, Any] = {"detail": detail}
    request_id = get_request_id()
    if request_id:
        payload["request_id"] = request_id
    if errors is not None:
        payload["errors"] = errors
    return payload

async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    _ = request
    if not isinstance(exc, StarletteHTTPException):
        return JSONResponse(
            status_code=500,
            content=_build_error_payload("Internal server error"),
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=_build_error_payload(str(exc.detail)),
        headers=exc.headers,
    )

async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    _ = request
    if not isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=500,
            content=_build_error_payload("Internal server error"),
        )

    return JSONResponse(
        status_code=422,
        content=_build_error_payload("Validation error", errors=exc.errors()),
    )

async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "Unhandled error on %s %s [request_id=%s]",
        request.method,
        request.url.path,
        get_request_id(),
    )
    return JSONResponse(
        status_code=500,
        content=_build_error_payload("Internal server error"),
    )

def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, internal_error_handler)
