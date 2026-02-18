from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import Container, get_container
from app.models.schemas.backtest import BacktestCreate

router = APIRouter(prefix='/backtest', tags=['backtest'])


async def _ensure_analysis_services(container: Container) -> None:
    try:
        await container.ensure_mandatory_analysis_services(strict=True)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post('/')
async def create_backtest(payload: BacktestCreate, container: Container = Depends(get_container)) -> dict:
    await _ensure_analysis_services(container)
    return await container.backtest_service.create_backtest(payload.model_dump())


@router.get('/{job_id}')
async def get_backtest_status(job_id: str, container: Container = Depends(get_container)) -> dict:
    await _ensure_analysis_services(container)
    try:
        return await container.backtest_service.get_status(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail='backtest not found') from exc


@router.get('/{job_id}/results')
async def get_backtest_results(job_id: str, container: Container = Depends(get_container)) -> dict:
    await _ensure_analysis_services(container)
    try:
        return await container.backtest_service.get_results(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail='backtest not found') from exc


@router.get('/')
async def list_backtests(container: Container = Depends(get_container)) -> list[dict]:
    await _ensure_analysis_services(container)
    return await container.backtest_service.list_backtests()
