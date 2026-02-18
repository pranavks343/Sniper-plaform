"""
PPO RL Execution Agent
Proximal Policy Optimisation agent for adaptive order execution.

Decides HOW to execute a given order (timing, aggressiveness, slicing)
based on real-time market micro-structure state.

Production path: stable-baselines3 PPO (if installed).
Fallback path:   rule-based heuristic execution policy.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class ExecutionAction:
    aggressiveness: float    # 0=passive/LIMIT … 1=aggressive/MARKET
    participation_rate: float  # fraction of volume to consume (0-1)
    delay_ms: int            # wait before submitting
    order_type: str          # "MARKET" | "LIMIT" | "TWAP" | "VWAP"
    limit_offset_bps: float  # for LIMIT orders: offset from mid (bps)
    model_type: str          # "ppo" | "heuristic"
    confidence: float


# ── Observation space ──────────────────────────────────────────────────────
# [spread_bps, bid_depth, ask_depth, volatility_1m, trend_direction,
#  remaining_qty_pct, time_remaining_pct, regime_code, urgency]
OBS_DIM = 9
ACT_DIM = 3   # [aggressiveness, participation_rate, delay_factor]


class PPOExecutionAgent:
    """
    RL agent that determines execution strategy for each order.

    Observation: market micro-structure features + order state
    Action:      continuous [aggressiveness, participation_rate, delay]

    Training:    offline on historical tick data via stable-baselines3
    Inference:   real-time, < 2ms per decision
    """

    def __init__(self, model_path: str | None = None) -> None:
        self._model: Any = None
        self._model_type = "heuristic"
        self._obs_mean: np.ndarray = np.zeros(OBS_DIM)
        self._obs_std:  np.ndarray = np.ones(OBS_DIM)

        if model_path and Path(model_path).exists():
            self._load(model_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def decide(
        self,
        order: dict,
        market_state: dict,
        regime_code: int = 0,
    ) -> ExecutionAction:
        """
        Args:
            order: {quantity, remaining_qty, start_time, deadline_s, urgency}
            market_state: {spread_bps, bid_depth, ask_depth, volatility_1m, trend}
            regime_code: 0=TRENDING 1=MEAN_REVERTING 2=VOLATILE
        Returns:
            ExecutionAction describing how to submit the order
        """
        obs = self._build_obs(order, market_state, regime_code)

        if self._model_type == "ppo" and self._model is not None:
            action, _ = self._model.predict(obs, deterministic=True)
            agg   = float(np.clip(action[0], 0, 1))
            pr    = float(np.clip(action[1], 0.01, 0.3))
            delay = int(np.clip(action[2] * 2000, 0, 5000))
            confidence = 0.85
        else:
            agg, pr, delay, confidence = self._heuristic(obs, market_state, regime_code)

        order_type, offset = self._action_to_order(agg, market_state)

        return ExecutionAction(
            aggressiveness=round(agg, 3),
            participation_rate=round(pr, 3),
            delay_ms=delay,
            order_type=order_type,
            limit_offset_bps=round(offset, 2),
            model_type=self._model_type,
            confidence=round(confidence, 3),
        )

    def train(
        self,
        env: Any,
        total_timesteps: int = 500_000,
        save_path: str | None = None,
    ) -> None:
        """
        Train PPO on a trading environment.
        Requires stable-baselines3 and a gymnasium-compatible env.
        """
        try:
            from stable_baselines3 import PPO  # type: ignore
            from stable_baselines3.common.callbacks import EvalCallback  # type: ignore

            self._model = PPO(
                "MlpPolicy",
                env,
                learning_rate=3e-4,
                n_steps=2048,
                batch_size=64,
                n_epochs=10,
                gamma=0.99,
                gae_lambda=0.95,
                clip_range=0.2,
                ent_coef=0.01,
                verbose=1,
            )

            callbacks = []
            if hasattr(env, "eval_env"):
                callbacks.append(EvalCallback(env.eval_env, eval_freq=10_000))

            self._model.learn(
                total_timesteps=total_timesteps,
                callback=callbacks or None,
            )
            self._model_type = "ppo"

            if save_path:
                self.save(save_path)

        except ImportError:
            raise RuntimeError(
                "stable-baselines3 required for PPO training. "
                "Install with: pip install stable-baselines3"
            )

    def save(self, path: str) -> None:
        if self._model is not None and self._model_type == "ppo":
            self._model.save(path)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load(self, path: str) -> None:
        try:
            from stable_baselines3 import PPO  # type: ignore

            self._model = PPO.load(path)
            self._model_type = "ppo"
        except Exception:
            pass  # fall through to heuristic

    def _build_obs(self, order: dict, market: dict, regime_code: int) -> np.ndarray:
        qty        = order.get("quantity", 1)
        remaining  = order.get("remaining_qty", qty)
        deadline   = order.get("deadline_s", 300)
        elapsed    = time.time() - order.get("start_time", time.time())

        obs = np.array([
            market.get("spread_bps", 10.0) / 100,
            min(market.get("bid_depth", 1000) / 10000, 1.0),
            min(market.get("ask_depth", 1000) / 10000, 1.0),
            min(market.get("volatility_1m", 0.5) / 5.0, 1.0),
            (market.get("trend", 0.0) + 1.0) / 2.0,      # normalise -1..1 → 0..1
            remaining / max(qty, 1),
            max(0.0, 1.0 - elapsed / max(deadline, 1)),
            regime_code / 2.0,
            min(order.get("urgency", 0.5), 1.0),
        ], dtype=np.float32)

        # Normalise
        return (obs - self._obs_mean) / (self._obs_std + 1e-8)

    @staticmethod
    def _heuristic(
        obs: np.ndarray,
        market: dict,
        regime_code: int,
    ) -> tuple[float, float, int, float]:
        """Rule-based fallback execution policy."""
        spread   = market.get("spread_bps", 10.0)
        urgency  = obs[8]
        time_rem = obs[6]
        vol      = market.get("volatility_1m", 0.5)

        # High urgency or little time left → be aggressive
        if urgency > 0.75 or time_rem < 0.1:
            return 0.9, 0.15, 0, 0.7

        # Volatile regime → go passive to reduce market impact
        if regime_code == 2:
            return 0.25, 0.05, 500, 0.65

        # Tight spread → LIMIT order is cheap
        if spread < 5:
            return 0.35, 0.08, 200, 0.72

        # Default moderate aggression
        return 0.55, 0.10, 100, 0.68

    @staticmethod
    def _action_to_order(agg: float, market: dict) -> tuple[str, float]:
        """Map aggressiveness scalar to order type + limit offset."""
        if agg > 0.8:
            return "MARKET", 0.0
        if agg > 0.5:
            spread = market.get("spread_bps", 10.0)
            return "LIMIT", spread * 0.5
        if agg > 0.25:
            return "TWAP", 0.0
        return "VWAP", 0.0
