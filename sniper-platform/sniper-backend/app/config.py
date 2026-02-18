from functools import lru_cache
from typing import List
from uuid import NAMESPACE_DNS, UUID, uuid5

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False)

    app_name: str = 'Sniper Trading Backend'
    api_prefix: str = '/api/v1'
    environment: str = 'dev'
    allowed_origins: List[str] = Field(default_factory=lambda: ['http://localhost:3000'])

    database_url: str = 'postgresql+asyncpg://postgres:postgres@localhost:5432/sniper'
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
