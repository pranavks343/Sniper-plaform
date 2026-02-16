from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=['websocket'])


async def _stream(websocket: WebSocket, event_type: str) -> None:
    await websocket.accept()
    try:
        while True:
            payload = {'event': event_type, 'data': {'ts': asyncio.get_event_loop().time()}}
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return


@router.websocket('/ws/market')
async def market_ws(websocket: WebSocket) -> None:
    await _stream(websocket, 'market:tick')


@router.websocket('/ws/orders')
async def orders_ws(websocket: WebSocket) -> None:
    await _stream(websocket, 'order:update')


@router.websocket('/ws/positions')
async def positions_ws(websocket: WebSocket) -> None:
    await _stream(websocket, 'position:update')


@router.websocket('/ws/risk')
async def risk_ws(websocket: WebSocket) -> None:
    await _stream(websocket, 'risk:update')
