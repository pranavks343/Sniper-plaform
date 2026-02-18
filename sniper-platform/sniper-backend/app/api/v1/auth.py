from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import Container, get_container
from app.models.schemas.auth import AuthResponse, LoginRequest, RegisterRequest

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=AuthResponse)
async def register(payload: RegisterRequest, container: Container = Depends(get_container)) -> dict:
    try:
        return await container.auth_service.register(payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post('/login', response_model=AuthResponse)
async def login(payload: LoginRequest, container: Container = Depends(get_container)) -> dict:
    try:
        return await container.auth_service.login(payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
