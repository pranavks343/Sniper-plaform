from functools import lru_cache

from app.config import Settings, get_settings
from app.services.backtest_service import BacktestService
from app.services.execution_service import ExecutionService
from app.services.quantum_service import QuantumService
from app.services.risk_service import RiskService
from app.services.strategy_service import StrategyService


class Container:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.quantum_service = QuantumService(settings)
        self.strategy_service = StrategyService(settings, self.quantum_service)
        self.risk_service = RiskService(settings, self.quantum_service)
        self.execution_service = ExecutionService(settings, self.quantum_service, self.risk_service)
        self.backtest_service = BacktestService(settings)


@lru_cache
def get_container() -> Container:
    return Container(get_settings())
