"""Market data API — historical OHLCV bars and live prices via Yahoo Finance."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import verify_token
from app.utils.logger import get_logger
from app.utils.market_data import get_market_data_service

router = APIRouter(prefix='/market', tags=['market'])
logger = get_logger(__name__)


@router.get('/history')
async def get_history(
    symbol: str = Query(description='Symbol name, e.g. RELIANCE, NIFTY, TCS'),
    period: str = Query(default='6mo', description='Period: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max'),
    interval: str = Query(default='1d', description='Interval: 1m,5m,15m,30m,1h,1d,1wk,1mo'),
    _: str = Depends(verify_token),
) -> list[dict]:
    """Return OHLCV bars for *symbol* from Yahoo Finance."""
    mds = get_market_data_service()
    bars = await mds.aget_historical(symbol, period=period, interval=interval)
    if not bars:
        raise HTTPException(status_code=404, detail=f'No data found for symbol: {symbol}')
    return bars


@router.get('/price')
async def get_price(
    symbol: str = Query(description='Symbol name, e.g. RELIANCE, NIFTY, TCS'),
    _: str = Depends(verify_token),
) -> dict:
    """Return live price for *symbol*."""
    mds = get_market_data_service()
    price = await mds.aget_price(symbol)
    if price is None:
        raise HTTPException(status_code=404, detail=f'No price found for symbol: {symbol}')
    return {'symbol': symbol, 'price': price}


@router.get('/prices')
async def get_prices(
    symbols: str = Query(description='Comma-separated symbols, e.g. RELIANCE,TCS,INFY'),
    _: str = Depends(verify_token),
) -> dict[str, float]:
    """Return live prices for multiple symbols."""
    mds = get_market_data_service()
    sym_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
    if not sym_list:
        raise HTTPException(status_code=400, detail='No symbols provided')
    result = await mds.aget_prices(sym_list)
    return result
