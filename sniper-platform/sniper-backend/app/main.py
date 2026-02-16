from __future__ import annotations

import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from app.api.v1.backtest import router as backtest_router
from app.api.v1.execution import router as execution_router
from app.api.v1.quantum import router as quantum_router
from app.api.v1.risk import router as risk_router
from app.api.v1.strategy import router as strategy_router
from app.api.v1.websocket import router as websocket_router
from app.config import get_settings
from app.dependencies import get_container
from app.utils.logger import configure_logging, get_logger

settings = get_settings()
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = get_container()
    container.quantum_service.connect()
    models_dir = Path(__file__).resolve().parents[1] / 'models'
    container.execution_service.load_models(str(models_dir))
    container.strategy_service.load_models(str(models_dir))
    app.state.container = container
    logger.info('backend startup complete')
    yield
    logger.info('backend shutdown complete')


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.middleware('http')
async def log_requests(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - started) * 1000
    logger.info('%s %s -> %s %.2fms', request.method, request.url.path, response.status_code, duration_ms)
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception('unhandled error on %s', request.url.path)
    return JSONResponse(status_code=500, content={'error': str(exc)})


@app.get('/health')
async def health() -> dict:
    return {'status': 'ok', 'service': settings.app_name}


@app.get('/items/{item_id}')
async def read_item(item_id: int, q: str | None = None) -> dict:
    return {'item_id': item_id, 'q': q}


@app.get('/favicon.ico')
async def favicon() -> Response:
    return Response(status_code=204)


app.include_router(strategy_router, prefix=settings.api_prefix)
app.include_router(execution_router, prefix=settings.api_prefix)
app.include_router(risk_router, prefix=settings.api_prefix)
app.include_router(backtest_router, prefix=settings.api_prefix)
app.include_router(quantum_router, prefix=settings.api_prefix)
app.include_router(websocket_router)
