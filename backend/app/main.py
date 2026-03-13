from contextlib import asynccontextmanager
from time import perf_counter
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.metrics import metrics_state
from app.api.router import api_router
from app.middleware.error_handler import register_error_handlers

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="Sentexa API",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def collect_metrics(request, call_next):
    started = perf_counter()
    response = await call_next(request)
    elapsed_ms = (perf_counter() - started) * 1000
    metrics_state.record(response.status_code, elapsed_ms)
    return response

app.include_router(api_router, prefix="/api")
register_error_handlers(app)


@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/api", status_code=307)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
    )