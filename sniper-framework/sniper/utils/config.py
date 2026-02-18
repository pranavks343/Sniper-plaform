"""
Configuration Management
Loads and validates configuration from environment variables + optional .env file.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    # Broker
    broker:              str   = "paper"           # "paper" | "zerodha" | "dhan"
    zerodha_api_key:     str   = ""
    zerodha_access_token: str  = ""
    dhan_client_id:      str   = ""
    dhan_access_token:   str   = ""

    # Database
    database_url:        str   = "postgresql+asyncpg://localhost/sniper"
    redis_url:           str   = "redis://localhost:6379/0"

    # Risk limits
    max_daily_loss_pct:  float = 0.02
    max_drawdown_pct:    float = 0.10
    max_delta:           float = 5000.0
    max_gamma:           float = 100.0
    max_vega:            float = 50000.0

    # Models
    models_dir:          str   = "models"

    # Logging
    log_level:           str   = "INFO"
    log_json:            bool  = True
    log_file:            str | None = None

    # App
    environment:         str   = "development"     # "development" | "production"
    admin_secret:        str   = "change-me-in-production"

    # Data
    symbols:             list[str] = field(default_factory=lambda: ["NIFTY", "BANKNIFTY"])
    timeframes:          list[str] = field(default_factory=lambda: ["1m", "5m", "15m"])

    def validate(self) -> list[str]:
        """Return list of validation errors (empty = valid)."""
        errors: list[str] = []
        if self.broker == "zerodha" and not self.zerodha_api_key:
            errors.append("ZERODHA_API_KEY is required when broker=zerodha")
        if self.broker == "dhan" and not self.dhan_client_id:
            errors.append("DHAN_CLIENT_ID is required when broker=dhan")
        if self.environment == "production" and self.admin_secret == "change-me-in-production":
            errors.append("ADMIN_SECRET must be set in production")
        if self.max_daily_loss_pct <= 0 or self.max_daily_loss_pct > 0.5:
            errors.append("MAX_DAILY_LOSS_PCT must be between 0 and 0.5")
        return errors


def load_config(env_file: str | None = None) -> Config:
    """
    Load configuration from environment variables.
    Optionally reads a .env file first.

    Environment variable names: uppercase, underscore (e.g. BROKER, MAX_DAILY_LOSS_PCT)
    """
    if env_file:
        _load_env_file(env_file)

    cfg = Config(
        broker=os.getenv("BROKER", "paper"),
        zerodha_api_key=os.getenv("ZERODHA_API_KEY", ""),
        zerodha_access_token=os.getenv("ZERODHA_ACCESS_TOKEN", ""),
        dhan_client_id=os.getenv("DHAN_CLIENT_ID", ""),
        dhan_access_token=os.getenv("DHAN_ACCESS_TOKEN", ""),
        database_url=os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost/sniper"),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        max_daily_loss_pct=float(os.getenv("MAX_DAILY_LOSS_PCT", "0.02")),
        max_drawdown_pct=float(os.getenv("MAX_DRAWDOWN_PCT", "0.10")),
        max_delta=float(os.getenv("MAX_DELTA", "5000")),
        max_gamma=float(os.getenv("MAX_GAMMA", "100")),
        max_vega=float(os.getenv("MAX_VEGA", "50000")),
        models_dir=os.getenv("MODELS_DIR", "models"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_json=os.getenv("LOG_JSON", "true").lower() == "true",
        log_file=os.getenv("LOG_FILE") or None,
        environment=os.getenv("ENVIRONMENT", "development"),
        admin_secret=os.getenv("ADMIN_SECRET", "change-me-in-production"),
        symbols=os.getenv("SYMBOLS", "NIFTY,BANKNIFTY").split(","),
        timeframes=os.getenv("TIMEFRAMES", "1m,5m,15m").split(","),
    )
    return cfg


def _load_env_file(path: str) -> None:
    """Parse simple KEY=VALUE .env file into os.environ."""
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key   = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
