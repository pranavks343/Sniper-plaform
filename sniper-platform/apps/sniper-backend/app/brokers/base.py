from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable


class BaseBroker(ABC):
    @abstractmethod
    def connect(self, credentials: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def place_order(self, symbol: str, quantity: int, order_type: str, price: float | None = None, side: str = 'BUY') -> dict:
        raise NotImplementedError

    @abstractmethod
    def modify_order(self, order_id: str, quantity: int | None = None, price: float | None = None) -> dict:
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, order_id: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_order_status(self, order_id: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_positions(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_holdings(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_margins(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def subscribe_market_data(self, symbols: list[str], callback: Callable[[dict], None]) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_historical_data(self, symbol: str, start: datetime, end: datetime, interval: str) -> list[dict]:
        raise NotImplementedError
