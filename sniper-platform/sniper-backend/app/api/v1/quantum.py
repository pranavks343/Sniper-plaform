from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import Container, get_container
from app.models.schemas.quantum import QuantumConfigUpdate

router = APIRouter(prefix='/quantum', tags=['quantum'])


@router.get('/status')
async def get_status(container: Container = Depends(get_container)):
    return container.quantum_service.get_status()


@router.post('/test')
async def test_connection(container: Container = Depends(get_container)) -> dict:
    return container.quantum_service.test_connection()


@router.get('/usage')
async def usage(container: Container = Depends(get_container)):
    return container.quantum_service.get_usage()


@router.put('/config')
async def update_config(payload: QuantumConfigUpdate, container: Container = Depends(get_container)) -> dict:
    return container.quantum_service.update_config(payload.model_dump(exclude_unset=True))
