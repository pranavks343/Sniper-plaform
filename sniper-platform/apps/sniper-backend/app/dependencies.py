from __future__ import annotations

import asyncio
from functools import lru_cache

import httpx
import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import Settings, get_settings
from app.db.session import SessionLocal
from app.services.auth_service import AuthService
from app.services.backtest_service import BacktestService
from app.services.execution_service import ExecutionService
from app.services.quantum_service import QuantumService
from app.services.risk_service import RiskService
from app.services.strategy_service import StrategyService
from app.utils.convex_bus import ConvexBus
from app.utils.encryption import DataEncryptor, EncryptionError
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ── Clerk JWKS client (lazy-init) ────────────────────────────────────────────
_jwks_client: PyJWKClient | None = None


def _get_jwks_client() -> PyJWKClient | None:
    """Return a cached PyJWKClient for Clerk JWT verification."""
    global _jwks_client
    if _jwks_client is not None:
        return _jwks_client
    settings = get_settings()
    jwks_url = (settings.clerk_jwks_url or '').strip()
    if not jwks_url:
        return None
    _jwks_client = PyJWKClient(jwks_url, cache_keys=True)
    return _jwks_client


def _verify_clerk_jwt(token: str) -> str | None:
    """Verify a Clerk-issued JWT. Returns user ID / subject on success, None on failure."""
    client = _get_jwks_client()
    if client is None:
        return None
    try:
        signing_key = client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=['RS256'],
            options={'verify_aud': False},
        )
        # Clerk puts user ID in 'sub', email may be in the payload too
        return payload.get('sub') or payload.get('email') or 'clerk_user'
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Exception) as exc:
        logger.debug('Clerk JWT verification failed: %s', exc)
        return None


class Container:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.session_factory = SessionLocal
        self.encryptor = None
        if settings.data_encryption_key:
            try:
                self.encryptor = DataEncryptor(settings.data_encryption_key)
            except EncryptionError as exc:
                raise ValueError(str(exc)) from exc
        self.event_bus = ConvexBus(settings.convex_url, settings.convex_deploy_key)
        self.auth_service = AuthService(settings, self.session_factory)
        self.quantum_service = QuantumService(settings)
        self.strategy_service = StrategyService(settings, self.quantum_service, self.session_factory)
        self.risk_service = RiskService(settings, self.quantum_service, event_bus=self.event_bus, session_factory=self.session_factory)
        self.execution_service = ExecutionService(
            settings,
            self.quantum_service,
            self.risk_service,
            self.event_bus,
            self.session_factory,
            encryptor=self.encryptor,
        )
        self.backtest_service = BacktestService(settings, self.session_factory)

    async def ensure_mandatory_analysis_services(self, strict: bool = False) -> dict:
        status: dict[str, bool | int] = {
            'strategy_service_ok': False,
            'backtest_service_ok': False,
            'quantum_service_ok': False,
            'strategy_count': 0,
            'backtest_count': 0,
        }
        errors: list[str] = []

        try:
            strategies = await self.strategy_service.list(status=None, regime=None)
            status['strategy_service_ok'] = True
            status['strategy_count'] = len(strategies)
        except Exception as exc:  # pragma: no cover - defensive
            errors.append(f'strategy:{exc}')
            logger.warning('mandatory strategy service check failed', exc_info=True)

        try:
            backtests = await self.backtest_service.list_backtests()
            status['backtest_service_ok'] = True
            status['backtest_count'] = len(backtests)
        except Exception as exc:  # pragma: no cover - defensive
            errors.append(f'backtest:{exc}')
            logger.warning('mandatory backtest service check failed', exc_info=True)

        try:
            quantum_status = self.quantum_service.get_status()
            status['quantum_service_ok'] = bool(getattr(quantum_status, 'available', False))
            if not status['quantum_service_ok']:
                timeout_seconds = max(0.5, float(self.settings.quantum_timeout_ms) / 1000.0)
                connected = await asyncio.wait_for(
                    asyncio.to_thread(self.quantum_service.connect),
                    timeout=timeout_seconds,
                )
                status['quantum_service_ok'] = bool(connected)
        except Exception as exc:  # pragma: no cover - defensive
            errors.append(f'quantum:{exc}')
            logger.warning('mandatory quantum service check failed', exc_info=True)

        if not status['quantum_service_ok']:
            errors.append('quantum:offline')
            logger.warning('mandatory quantum service is offline (set IBM_QUANTUM_TOKEN to keep analysis pipeline fully armed)')

        if strict and errors:
            raise RuntimeError(f"mandatory analysis services unavailable: {', '.join(errors)}")

        return status


@lru_cache
def get_container() -> Container:
    return Container(get_settings())


_bearer = HTTPBearer(auto_error=False)


async def verify_token(
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
) -> str:
    """
    Validates Bearer token from Authorization header.

    Checks in order:
      1. Clerk JWT (if CLERK_JWKS_URL is configured)
      2. Backend-issued internal token (AuthService._tokens)

    Returns user identifier on success, raises 401 on failure.
    """
    # Dev bypass: skip auth entirely when SKIP_AUTH=true
    settings = get_settings()
    if settings.skip_auth:
        logger.debug('Auth bypassed (SKIP_AUTH=true) — using default user')
        return settings.default_user_id

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Missing Authorization header',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    token = credentials.credentials

    # 1. Try Clerk JWT verification
    clerk_user = _verify_clerk_jwt(token)
    if clerk_user:
        return clerk_user

    # 2. Fall back to backend-issued token
    container = get_container()
    email = container.auth_service._tokens.get(token)
    if email:
        return email

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid or expired token',
        headers={'WWW-Authenticate': 'Bearer'},
    )
