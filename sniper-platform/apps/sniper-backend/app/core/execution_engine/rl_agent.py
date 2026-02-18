from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import joblib
import numpy as np


class ActionType(str, Enum):
    WAIT = 'WAIT'
    MARKET = 'MARKET'
    LIMIT = 'LIMIT'
    TWAP = 'TWAP'


@dataclass
class ExecutionAction:
    action_type: ActionType
    urgency: float
    limit_offset: float


class TradingExecutionEnv:
    def __init__(self) -> None:
        self.t = 0
        self.state = np.zeros(9, dtype=float)

    def reset(self) -> np.ndarray:
        self.t = 0
        self.state = np.zeros(9, dtype=float)
        return self.state

    def step(self, action: ExecutionAction) -> tuple[np.ndarray, float, bool, bool, dict]:
        executed_qty = max(0.0, action.urgency)
        cost = self._calculate_slippage(executed_qty, action.urgency)
        reward = self._calculate_reward(executed_qty, cost)
        self.t += 1
        done = self.t >= 50
        return self.state, reward, done, False, {'executed_qty': executed_qty, 'cost': cost}

    def _calculate_slippage(self, quantity: float, urgency: float) -> float:
        return float(0.0002 * quantity * (1 + urgency))

    def _calculate_reward(self, executed_qty: float, cost: float) -> float:
        return float(executed_qty - cost)


class PPOExecutionAgent:
    def __init__(self) -> None:
        self.weights = np.array([0.2, -0.1, -0.2, 0.1, 0.4, 0.2, -0.1, -0.1, -0.2], dtype=float)

    def train(self, env: TradingExecutionEnv, total_timesteps: int = 100000) -> None:
        # Lightweight placeholder training loop for deterministic behavior.
        _ = env
        _ = total_timesteps
        self.weights = self.weights / (np.linalg.norm(self.weights) + 1e-9)

    def predict_action(self, state: np.ndarray) -> ExecutionAction:
        score = float(np.dot(self.weights, state))
        urgency = float(np.clip(0.5 + score, 0.0, 1.0))
        if urgency < 0.35:
            action = ActionType.WAIT
        elif urgency < 0.65:
            action = ActionType.LIMIT
        elif urgency < 0.85:
            action = ActionType.TWAP
        else:
            action = ActionType.MARKET
        return ExecutionAction(action_type=action, urgency=urgency, limit_offset=float((0.5 - urgency) * 0.001))

    def save_model(self, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({'weights': self.weights}, path)

    def load_model(self, path: str) -> None:
        data = joblib.load(path)
        self.weights = np.asarray(data['weights'], dtype=float)
