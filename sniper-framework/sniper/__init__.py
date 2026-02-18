"""
Sniper Framework — backend logic for algorithmic trading.

Covers: Risk engine, Execution engine, Strategy engine, Broker abstractions,
        Event bus, State management, Data pipeline, Backtest engine,
        Orchestration, and Utilities.

Use with FastAPI, Celery, or any Python service.
"""

# ── Brokers ──────────────────────────────────────────────────────────────────
from sniper.brokers import BaseBroker, PaperTradingBroker
from sniper.brokers.zerodha import ZerodhaBroker
from sniper.brokers.dhan import DhanBroker

# ── Core: Risk ────────────────────────────────────────────────────────────────
from sniper.core import (
    BreakerStatus,
    CircuitBreaker,
    LimitMonitor,
    RiskStatus,
)
from sniper.core.risk_engine.greeks_calculator import GreeksCalculator, Greeks, PortfolioGreeks

# ── Core: Execution ────────────────────────────────────────────────────────────
from sniper.core import (
    CostBreakdown,
    CostEstimator,
    RoutingDecision,
    SmartOrderRouter,
)
from sniper.core.execution_engine.ppo_agent import PPOExecutionAgent, ExecutionAction

# ── Core: Strategy ────────────────────────────────────────────────────────────
from sniper.core import (
    HMMRegimeDetector,
    RegimeState,
    SignalGenerator,
    TradingSignal,
)
from sniper.core.strategy_engine.position_sizer import PositionSizer, SizeResult
from sniper.core.strategy_engine.meta_labeler import MetaLabeler, MetaLabel

# ── Core: Quantum ─────────────────────────────────────────────────────────────
from sniper.core.quantum import QAOAOrderRouter, QAOAResult, QAOAHedger, HedgeResult

# ── Schemas ───────────────────────────────────────────────────────────────────
from sniper.schemas import BaseResponse, Direction, OrderStatus, Regime

# ── Events ────────────────────────────────────────────────────────────────────
from sniper.events import EventBus, EventType, Event

# ── State ─────────────────────────────────────────────────────────────────────
from sniper.state import StateManager, TradingState

# ── Data Pipeline ─────────────────────────────────────────────────────────────
from sniper.data import WebSocketManager, BarAggregator, Bar, MarketSimulator

# ── Backtest ──────────────────────────────────────────────────────────────────
from sniper.backtest import BacktestEngine, BacktestResult
from sniper.backtest.metrics import PerformanceCalculator, PerformanceMetrics

# ── Orchestration ─────────────────────────────────────────────────────────────
from sniper.orchestration import TradingLoop, StrategyLifecycle, ModelLoader

# ── Utilities ─────────────────────────────────────────────────────────────────
from sniper.utils import setup_logging, get_logger, Config, load_config, retry, RetryError, Cache

__version__ = "1.1.0"

__all__ = [
    # Brokers
    "BaseBroker", "PaperTradingBroker", "ZerodhaBroker", "DhanBroker",
    # Risk
    "BreakerStatus", "CircuitBreaker", "LimitMonitor", "RiskStatus",
    "GreeksCalculator", "Greeks", "PortfolioGreeks",
    # Execution
    "CostBreakdown", "CostEstimator", "RoutingDecision", "SmartOrderRouter",
    "PPOExecutionAgent", "ExecutionAction",
    # Strategy
    "HMMRegimeDetector", "RegimeState", "SignalGenerator", "TradingSignal",
    "PositionSizer", "SizeResult", "MetaLabeler", "MetaLabel",
    # Quantum
    "QAOAOrderRouter", "QAOAResult", "QAOAHedger", "HedgeResult",
    # Schemas
    "BaseResponse", "Direction", "OrderStatus", "Regime",
    # Events
    "EventBus", "EventType", "Event",
    # State
    "StateManager", "TradingState",
    # Data
    "WebSocketManager", "BarAggregator", "Bar", "MarketSimulator",
    # Backtest
    "BacktestEngine", "BacktestResult", "PerformanceCalculator", "PerformanceMetrics",
    # Orchestration
    "TradingLoop", "StrategyLifecycle", "ModelLoader",
    # Utils
    "setup_logging", "get_logger", "Config", "load_config",
    "retry", "RetryError", "Cache",
]
