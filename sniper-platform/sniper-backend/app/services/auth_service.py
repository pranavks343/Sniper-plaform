from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config import Settings
from app.models.database.audit import AuditLog
from app.models.database.user import User, UserPreference


class AuthService:
    """Stores token -> (user_id, email) for validation; tokens are in-memory (lost on restart)."""

    def __init__(self, settings: Settings, session_factory: async_sessionmaker) -> None:
        self.settings = settings
        self.session_factory = session_factory
        self._tokens: dict[str, tuple[str, str]] = {}  # token -> (user_id, email)

    def _normalize_email(self, email: str) -> str:
        return email.strip().lower()

    def _hash_password(self, password: str, salt: str) -> str:
        return hashlib.sha256(f'{salt}:{password}'.encode('utf-8')).hexdigest()

    async def register(self, email: str, password: str) -> dict:
        normalized_email = self._normalize_email(email)
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters long')

        async with self.session_factory() as session:
            existing = await session.execute(select(User).where(User.email == normalized_email))
            if existing.scalar_one_or_none() is not None:
                raise ValueError('Email already registered')

            user_id = str(uuid4())
            created_at = datetime.utcnow()
            salt = secrets.token_hex(16)
            password_hash = self._hash_password(password, salt)

            user = User(
                id=user_id,
                email=normalized_email,
                password_hash=password_hash,
                password_salt=salt,
                role='trader',
                is_active=True,
            )
            prefs = UserPreference(
                id=str(uuid4()),
                user_id=user_id,
                timezone='Asia/Kolkata',
                theme='dark',
                preferences_json='{}',
            )
            audit = AuditLog(
                id=str(uuid4()),
                user_id=user_id,
                entity_type='user',
                entity_id=user_id,
                action='register',
                details={'email': normalized_email},
                source='api',
            )
            session.add_all([user, prefs, audit])
            await session.commit()

        token = secrets.token_urlsafe(32)
        self._tokens[token] = (user_id, normalized_email)
        return {
            'token': token,
            'user': {
                'id': user_id,
                'email': normalized_email,
                'created_at': created_at,
            },
        }

    def get_user_for_token(self, token: str) -> tuple[str, str] | None:
        """Return (user_id, email) if token is valid, else None."""
        return self._tokens.get(token) if token else None

    async def login(self, email: str, password: str) -> dict:
        normalized_email = self._normalize_email(email)
        async with self.session_factory() as session:
            result = await session.execute(select(User).where(User.email == normalized_email))
            user = result.scalar_one_or_none()
            if user is None or not user.password_hash or not user.password_salt:
                raise ValueError('Invalid email or password')

            computed = self._hash_password(password, user.password_salt)
            if not hmac.compare_digest(user.password_hash, computed):
                raise ValueError('Invalid email or password')

            session.add(
                AuditLog(
                    id=str(uuid4()),
                    user_id=user.id,
                    entity_type='user',
                    entity_id=user.id,
                    action='login',
                    details={'email': user.email},
                    source='api',
                )
            )
            await session.commit()

        token = secrets.token_urlsafe(32)
        self._tokens[token] = (user.id, normalized_email)
        return {
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'created_at': user.created_at,
            },
        }
