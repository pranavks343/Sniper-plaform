from functools import lru_cache
from pathlib import Path
from typing import List
from uuid import NAMESPACE_DNS, UUID, uuid5

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env from backend root (directory containing app/), not CWD, so it works from any run dir
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
_ENV_FILE = _BACKEND_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), env_file_encoding='utf-8', case_sensitive=False)

    app_name: str = 'Sniper Trading Backend'
    api_prefix: str = '/api/v1'
    environment: str = 'dev'
    # Comma-separated in env (e.g. ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com)
    allowed_origins: List[str] = Field(default_factory=lambda: ['http://localhost:3000'])

    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v: object) -> List[str]:
        if isinstance(v, str):
            return [x.strip() for x in v.split(',') if x.strip()]
        return v if isinstance(v, list) else ['http://localhost:3000']

    database_url: str = 'postgresql+asyncpg://postgres:postgres@localhost:5432/sniper'
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_recycle_seconds: int = 300
    default_user_id: str = '00000000-0000-0000-0000-000000000001'
    convex_deployment: str = ''
    convex_url: str = ''
    convex_deploy_key: str = ''
    data_encryption_key: str = ''

    ibm_quantum_token: str = ''
    ibm_quantum_backend: str = 'ibm_brisbane'

    enable_quantum_routing: bool = True
    enable_quantum_portfolio: bool = True
    enable_quantum_hedging: bool = True
    quantum_routing_min_order_size: float = 100000.0
    quantum_portfolio_min_assets: int = 50
    quantum_hedging_min_positions: int = 10
    quantum_timeout_ms: int = 5000
    mandatory_analysis_heartbeat_seconds: int = 45
    # Interval between simulated market ticks (each tick = 4 Convex mutations). Default 1.0 = 4 mutations/sec.
    market_tick_interval_seconds: float = 1.0

    zerodha_api_key: str = ''
    zerodha_api_secret: str = ''
    broker_provider: str = 'paper'

    upstox_api_key: str = ''
    upstox_api_secret: str = ''
    upstox_redirect_uri: str = ''
    upstox_access_token: str = ''

    openai_api_key: str = ''
    openai_model: str = 'gpt-4o-mini'
    openai_request_timeout_seconds: float = 45.0
    openai_retry_delay_seconds: float = 1.5
    openai_max_retries: int = 1

    max_daily_loss_pct: float = 0.02
    max_drawdown_pct: float = 0.10
    max_delta: float = 500.0
    max_gamma: float = 50.0
    max_vega: float = 10000.0

    # Circuit breaker deactivation: set in production to a strong secret
    circuit_breaker_admin_secret: str = ''

    # Clerk: JWKS URL to verify Clerk JWTs (e.g. https://xxx.clerk.accounts.dev/.well-known/jwks.json)
    clerk_jwks_url: str = ''

    @property
    def default_user_uuid(self) -> str:
        candidate = (self.default_user_id or '').strip()
        try:
            return str(UUID(candidate))
        except ValueError:
            return str(uuid5(NAMESPACE_DNS, candidate or 'default-user'))


@lru_cache
def get_settings() -> Settings:
    return Settings()
