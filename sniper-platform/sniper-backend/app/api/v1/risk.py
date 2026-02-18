from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import Container, get_container, get_current_user
from app.models.schemas.risk import CircuitBreakerDeactivateRequest, CircuitBreakerRequest, RiskLimits

router = APIRouter(prefix='/risk', tags=['risk'], dependencies=[Depends(get_current_user)])


@router.get('/metrics')
async def get_metrics(container: Container = Depends(get_container)) -> dict:
    return await container.risk_service.get_metrics()


@router.get('/greeks')
async def get_greeks(container: Container = Depends(get_container)) -> dict:
    return await container.risk_service.get_greeks()


@router.get('/limits')
async def get_limits(container: Container = Depends(get_container)) -> dict:
    return await container.risk_service.get_limits()


@router.put('/limits')
async def update_limits(payload: RiskLimits, container: Container = Depends(get_container)) -> dict:
    return await container.risk_service.update_limits(payload.model_dump())


@router.get('/violations')
async def get_violations(container: Container = Depends(get_container)) -> list[dict]:
    return await container.risk_service.get_violations()


@router.post('/circuit-breaker/activate')
async def activate_breaker(payload: CircuitBreakerRequest, container: Container = Depends(get_container)) -> dict:
    return await container.risk_service.activate_circuit_breaker(payload.reason)


@router.post('/circuit-breaker/deactivate')
async def deactivate_breaker(payload: CircuitBreakerDeactivateRequest, container: Container = Depends(get_container)) -> dict:
    try:
        return await container.risk_service.deactivate_circuit_breaker(payload.admin_password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
