from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import Container, get_container, verify_token
from app.models.schemas.risk import CircuitBreakerDeactivateRequest, CircuitBreakerRequest, PortfolioStateUpdate, RiskLimits

router = APIRouter(prefix='/risk', tags=['risk'])


@router.get('/metrics')
async def get_metrics(container: Container = Depends(get_container), _: str = Depends(verify_token)) -> dict:
    return await container.risk_service.get_metrics()


@router.get('/greeks')
async def get_greeks(container: Container = Depends(get_container), _: str = Depends(verify_token)) -> dict:
    return await container.risk_service.get_greeks()


@router.get('/limits')
async def get_limits(container: Container = Depends(get_container), _: str = Depends(verify_token)) -> dict:
    return await container.risk_service.get_limits()


@router.put('/limits')
async def update_limits(payload: RiskLimits, container: Container = Depends(get_container), _: str = Depends(verify_token)) -> dict:
    return await container.risk_service.update_limits(payload.model_dump())


@router.put('/portfolio-state')
async def update_portfolio_state(payload: PortfolioStateUpdate, container: Container = Depends(get_container), _: str = Depends(verify_token)) -> dict:
    container.risk_service.set_portfolio_state(payload.model_dump())
    return await container.risk_service.get_greeks()


@router.get('/violations')
async def get_violations(container: Container = Depends(get_container), _: str = Depends(verify_token)) -> list[dict]:
    return await container.risk_service.get_violations()


@router.post('/circuit-breaker/activate')
async def activate_breaker(payload: CircuitBreakerRequest, container: Container = Depends(get_container), _: str = Depends(verify_token)) -> dict:
    return await container.risk_service.activate_circuit_breaker(payload.reason)


@router.post('/circuit-breaker/deactivate')
async def deactivate_breaker(payload: CircuitBreakerDeactivateRequest, container: Container = Depends(get_container), _: str = Depends(verify_token)) -> dict:
    return await container.risk_service.deactivate_circuit_breaker(payload.admin_password)
