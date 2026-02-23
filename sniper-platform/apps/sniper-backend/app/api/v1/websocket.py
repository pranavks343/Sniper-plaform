from __future__ import annotations

import asyncio
import json
import time
from contextlib import suppress

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.utils.logger import get_logger
from app.utils.market_data import get_market_data_service

router = APIRouter(tags=['websocket'])
logger = get_logger(__name__)

# Default symbols to stream if client does not specify
_DEFAULT_MARKET_SYMBOLS = ['NIFTY', 'BANKNIFTY', 'RELIANCE', 'TCS', 'INFY', 'HDFCBANK']


async def _live_market_stream(websocket: WebSocket, symbols: list[str], interval: float = 5.0) -> None:
    """Push real-time prices from Yahoo Finance every *interval* seconds."""
    mds = get_market_data_service()
    try:
        while True:
            ticks = []
            for sym in symbols:
                price = await mds.aget_price(sym)
                if price is not None:
                    ticks.append({'symbol': sym, 'ltp': price, 'ts': time.time(), 'source': 'yahoo'})
                else:
                    ticks.append({'symbol': sym, 'ltp': None, 'ts': time.time(), 'source': 'unavailable'})

            payload = {'event': 'market:tick', 'data': ticks}
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(interval)
    except WebSocketDisconnect:
        return
    except Exception as exc:
        logger.warning('live market stream error: %s', exc, exc_info=True)


async def _fallback_stream(websocket: WebSocket, event_type: str) -> None:
    """Simulated 1 Hz heartbeat when no real data is available."""
    try:
        while True:
            payload = {'event': event_type, 'data': {'ts': time.time(), 'source': 'simulated'}}
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return


async def _stream(websocket: WebSocket, patterns: list[str], fallback_event: str) -> None:
    await websocket.accept()
    container = getattr(websocket.app.state, 'container', None)
    event_bus = getattr(container, 'event_bus', None)

    if event_bus is None or not event_bus.connected:
        await _fallback_stream(websocket, fallback_event)
        return

    try:
        async for payload in event_bus.subscribe(patterns):
            await websocket.send_text(json.dumps(payload))
    except WebSocketDisconnect:
        return
    except Exception:
        logger.warning('websocket stream failed for patterns=%s', patterns, exc_info=True)
        with suppress(WebSocketDisconnect):
            await websocket.send_text(json.dumps({'event': 'system:error', 'data': {'message': 'stream disconnected'}}))


@router.websocket('/ws/market')
async def market_ws(websocket: WebSocket) -> None:
    """
    Real-time market data stream.

    Client may optionally send a JSON message after connecting to specify symbols:
        {"symbols": ["RELIANCE", "TCS", "NIFTY"]}

    If no message is received within 2 seconds, default symbols are used.
    Prices are refreshed every 5 seconds from Yahoo Finance.
    """
    await websocket.accept()

    # Try to receive a custom symbol list from client (non-blocking, 2 s timeout)
    symbols = _DEFAULT_MARKET_SYMBOLS
    try:
        raw = await asyncio.wait_for(websocket.receive_text(), timeout=2.0)
        msg = json.loads(raw)
        if isinstance(msg.get('symbols'), list) and msg['symbols']:
            symbols = [str(s).strip().upper() for s in msg['symbols']]
            logger.info('WS /ws/market custom symbols: %s', symbols)
    except (asyncio.TimeoutError, Exception):
        pass  # use defaults

    await _live_market_stream(websocket, symbols, interval=5.0)


@router.websocket('/ws/orders')
async def orders_ws(websocket: WebSocket) -> None:
    await _stream(websocket, ['order:update*'], 'order:update')


@router.websocket('/ws/positions')
async def positions_ws(websocket: WebSocket) -> None:
    await _stream(websocket, ['position:update*'], 'position:update')


@router.websocket('/ws/risk')
async def risk_ws(websocket: WebSocket) -> None:
    await _stream(websocket, ['risk:update*'], 'risk:update')
