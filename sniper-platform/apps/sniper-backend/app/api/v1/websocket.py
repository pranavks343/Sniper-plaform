from __future__ import annotations

import asyncio
import json
import time
from contextlib import suppress

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.utils.logger import get_logger

router = APIRouter(tags=['websocket'])
logger = get_logger(__name__)


async def _fallback_stream(websocket: WebSocket, event_type: str) -> None:
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
    await _stream(websocket, ['market:tick*'], 'market:tick')


@router.websocket('/ws/orders')
async def orders_ws(websocket: WebSocket) -> None:
    await _stream(websocket, ['order:update*'], 'order:update')


@router.websocket('/ws/positions')
async def positions_ws(websocket: WebSocket) -> None:
    await _stream(websocket, ['position:update*'], 'position:update')


@router.websocket('/ws/risk')
async def risk_ws(websocket: WebSocket) -> None:
    await _stream(websocket, ['risk:update*'], 'risk:update')
