from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import Container, get_container
from app.models.schemas.quantum import QuantumConfigUpdate, QuantumConnectPayload

router = APIRouter(prefix='/quantum', tags=['quantum'])


@router.get('/status')
async def get_status(container: Container = Depends(get_container)):
    return container.quantum_service.get_status()


@router.post('/connect')
async def connect(payload: QuantumConnectPayload, container: Container = Depends(get_container)) -> dict:
    # Always succeeds — falls back to local simulation if IBM cloud is unavailable
    container.quantum_service.connect(payload.api_token)
    return container.quantum_service.test_connection()


@router.post('/disconnect')
async def disconnect(container: Container = Depends(get_container)) -> dict:
    return container.quantum_service.disconnect()


@router.post('/test')
async def test_connection(container: Container = Depends(get_container)) -> dict:
    return container.quantum_service.test_connection()


@router.get('/usage')
async def usage(container: Container = Depends(get_container)):
    return container.quantum_service.get_usage()


@router.put('/config')
async def update_config(payload: QuantumConfigUpdate, container: Container = Depends(get_container)) -> dict:
    return container.quantum_service.update_config(payload.model_dump(exclude_unset=True))
