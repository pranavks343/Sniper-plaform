from __future__ import annotations

import asyncio
import random
import time
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from app.api.v1.ai import router as ai_router
from app.api.v1.auth import router as auth_router
from app.api.v1.backtest import router as backtest_router
from app.api.v1.execution import router as execution_router
from app.api.v1.market import router as market_router
from app.api.v1.quantum import router as quantum_router
from app.api.v1.risk import router as risk_router
from app.api.v1.strategy import router as strategy_router
from app.api.v1.websocket import router as websocket_router
from app.config import get_settings
from app.db.session import init_db
from app.dependencies import get_container
from app.utils.logger import configure_logging, get_logger

settings = get_settings()
configure_logging()
logger = get_logger(__name__)


async def _publish_market_ticks(container) -> None:
    from app.utils.market_data import get_market_data_service

    mds = get_market_data_service()
    symbols = ['NIFTY', 'BANKNIFTY', 'RELIANCE', 'TCS', 'INFY', 'HDFCBANK']
    # Cache previous prices for fallback
    cached: dict[str, float] = {}
    interval = max(3.0, float(settings.market_tick_interval_seconds))

    while True:
        for symbol in symbols:
            try:
                live = await mds.aget_price(symbol)
                price = live if live is not None else cached.get(symbol, 100.0)
                cached[symbol] = price
            except Exception:
                price = cached.get(symbol, 100.0)

            tick = {
                'symbol': symbol,
                'ltp': round(price, 2),
                'price': round(price, 2),
                'volume': random.randint(10, 250),
                'ts': time.time(),
            }
            await container.event_bus.publish_event('market:tick', 'market:tick', tick)
            await container.event_bus.publish_event(f'market:tick:{symbol}', 'market:tick', tick)
            await container.event_bus.set_json(f'market:latest:{symbol}', tick, ttl_seconds=3600)
        await asyncio.sleep(interval)


async def _mandatory_analysis_heartbeat(container) -> None:
    interval = max(10, int(settings.mandatory_analysis_heartbeat_seconds))
    while True:
        try:
            await container.ensure_mandatory_analysis_services(strict=False)
        except Exception:
            logger.warning('mandatory analysis service heartbeat failed', exc_info=True)
        await asyncio.sleep(interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = get_container()
    await init_db()
    await container.event_bus.connect()
    await container.risk_service.bootstrap_limits()
    try:
        quantum_timeout_seconds = max(0.5, float(settings.quantum_timeout_ms) / 1000.0)
        await asyncio.wait_for(
            asyncio.to_thread(container.quantum_service.connect),
            timeout=quantum_timeout_seconds,
        )
    except Exception:
        logger.warning('initial quantum connect timed out/failed; continuing with fallback mode', exc_info=True)
    models_dir = Path(__file__).resolve().parents[1] / 'models'
    container.execution_service.load_models(str(models_dir))
    await container.execution_service.ensure_broker_account()
    container.strategy_service.load_models(str(models_dir))
    await container.ensure_mandatory_analysis_services(strict=False)
    market_task = None
    analysis_task = None
    if container.event_bus.connected:
        market_task = asyncio.create_task(_publish_market_ticks(container))
    analysis_task = asyncio.create_task(_mandatory_analysis_heartbeat(container))
    app.state.container = container
    logger.info('backend startup complete')
    try:
        yield
    finally:
        if market_task is not None:
            market_task.cancel()
            with suppress(asyncio.CancelledError):
                await market_task
        if analysis_task is not None:
            analysis_task.cancel()
            with suppress(asyncio.CancelledError):
                await analysis_task
        await container.event_bus.disconnect()
        logger.info('backend shutdown complete')


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allow_headers=['Authorization', 'Content-Type', 'Accept'],
)


@app.middleware('http')
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    if settings.environment == 'production':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response


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
    # Never expose internal error details in production
    detail = str(exc) if settings.environment != 'production' else 'Internal server error'
    return JSONResponse(status_code=500, content={'error': detail})


@app.get('/health')
async def health() -> dict:
    return {'status': 'ok', 'service': settings.app_name}


@app.get('/favicon.ico')
async def favicon() -> Response:
    return Response(status_code=204)


app.include_router(ai_router, prefix=settings.api_prefix)
app.include_router(strategy_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(execution_router, prefix=settings.api_prefix)
app.include_router(market_router, prefix=settings.api_prefix)
app.include_router(risk_router, prefix=settings.api_prefix)
app.include_router(backtest_router, prefix=settings.api_prefix)
app.include_router(quantum_router, prefix=settings.api_prefix)
app.include_router(websocket_router)
