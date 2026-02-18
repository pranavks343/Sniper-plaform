from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import Container, get_container
from app.models.schemas.execution import OrderOut, PlaceOrderRequest, PositionOut, TradeOut

router = APIRouter(prefix='/execution', tags=['execution'])


@router.post('/order', response_model=OrderOut)
async def place_order(payload: PlaceOrderRequest, container: Container = Depends(get_container)) -> dict:
    try:
        return await container.execution_service.place_order(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get('/orders', response_model=list[OrderOut])
async def list_orders(
    status: str | None = Query(default=None), strategy_id: str | None = Query(default=None), container: Container = Depends(get_container)
) -> list[dict]:
    return await container.execution_service.list_orders(status=status, strategy_id=strategy_id)


@router.get('/orders/{order_id}', response_model=OrderOut)
async def get_order(order_id: str, container: Container = Depends(get_container)) -> dict:
    try:
        return await container.execution_service.get_order(order_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail='order not found') from exc


@router.post('/orders/{order_id}/cancel', response_model=OrderOut)
async def cancel_order(order_id: str, container: Container = Depends(get_container)) -> dict:
    try:
        return await container.execution_service.cancel_order(order_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail='order not found') from exc


@router.get('/positions', response_model=list[PositionOut])
async def get_positions(container: Container = Depends(get_container)) -> list[dict]:
    return container.execution_service.get_positions()


@router.get('/trades', response_model=list[TradeOut])
async def list_trades(
    strategy_id: str | None = Query(default=None), symbol: str | None = Query(default=None), container: Container = Depends(get_container)
) -> list[dict]:
    return await container.execution_service.list_trades(strategy_id=strategy_id, symbol=symbol)
