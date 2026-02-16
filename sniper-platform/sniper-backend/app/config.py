from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False)

    app_name: str = 'Sniper Trading Backend'
    api_prefix: str = '/api/v1'
    environment: str = 'dev'
    allowed_origins: List[str] = Field(default_factory=lambda: ['http://localhost:3000'])

    database_url: str = 'postgresql+asyncpg://postgres:postgres@localhost:5432/sniper'
    redis_url: str = 'redis://localhost:6379/0'

    ibm_quantum_token: str = ''
    ibm_quantum_backend: str = 'ibm_brisbane'

    enable_quantum_routing: bool = True
    enable_quantum_portfolio: bool = True
    enable_quantum_hedging: bool = True
    quantum_routing_min_order_size: float = 100000.0
    quantum_portfolio_min_assets: int = 50
    quantum_hedging_min_positions: int = 10
    quantum_timeout_ms: int = 5000

    zerodha_api_key: str = ''
    zerodha_api_secret: str = ''

    max_daily_loss_pct: float = 0.02
    max_drawdown_pct: float = 0.10
    max_delta: float = 0.30
    max_gamma: float = 0.05
    max_vega: float = 10000.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
