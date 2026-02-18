from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import Container, get_container
from app.models.schemas.common import BaseResponse, Regime
from app.models.schemas.strategy import StrategyCreate, StrategyOut, StrategyUpdate

router = APIRouter(prefix='/strategy', tags=['strategy'])


async def _ensure_analysis_services(container: Container) -> None:
    try:
        await container.ensure_mandatory_analysis_services(strict=True)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post('/', response_model=StrategyOut)
async def create_strategy(payload: StrategyCreate, container: Container = Depends(get_container)) -> dict:
    await _ensure_analysis_services(container)
    return await container.strategy_service.create(payload.model_dump())


@router.get('/', response_model=list[StrategyOut])
async def list_strategies(
    status: str | None = Query(default=None), regime: Regime | None = Query(default=None), container: Container = Depends(get_container)
) -> list[dict]:
    await _ensure_analysis_services(container)
    return await container.strategy_service.list(status=status, regime=regime)


@router.get('/{strategy_id}', response_model=StrategyOut)
async def get_strategy(strategy_id: str, container: Container = Depends(get_container)) -> dict:
    await _ensure_analysis_services(container)
    try:
        return await container.strategy_service.get(strategy_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail='strategy not found') from exc


@router.put('/{strategy_id}', response_model=StrategyOut)
async def update_strategy(strategy_id: str, payload: StrategyUpdate, container: Container = Depends(get_container)) -> dict:
    await _ensure_analysis_services(container)
    try:
        return await container.strategy_service.update(strategy_id, payload.model_dump(exclude_unset=True))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail='strategy not found') from exc


@router.delete('/{strategy_id}', response_model=BaseResponse)
async def delete_strategy(strategy_id: str, container: Container = Depends(get_container)) -> BaseResponse:
    await _ensure_analysis_services(container)
    await container.strategy_service.delete(strategy_id)
    return BaseResponse(success=True, message='strategy deleted')


@router.post('/{strategy_id}/activate', response_model=StrategyOut)
async def activate_strategy(strategy_id: str, container: Container = Depends(get_container)) -> dict:
    await _ensure_analysis_services(container)
    return await container.strategy_service.activate(strategy_id)


@router.post('/{strategy_id}/deactivate', response_model=StrategyOut)
async def deactivate_strategy(strategy_id: str, container: Container = Depends(get_container)) -> dict:
    await _ensure_analysis_services(container)
    return await container.strategy_service.deactivate(strategy_id)
