from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content={"error": "Not found"})


async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(404, not_found_handler)
    app.add_exception_handler(500, internal_error_handler)
