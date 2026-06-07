"""
PPO-based adaptive order-execution agent.

The agent decides *how aggressively* to execute a parent order at each step,
trading off market impact (being aggressive moves the price against you) against
timing risk (waiting exposes you to adverse drift). It is trained with
Proximal Policy Optimisation (stable-baselines3) on a custom Gymnasium
environment that simulates implementation shortfall.

Three layers, in priority order:
1. A trained PPO policy (loaded from a stable-baselines3 ``.zip``) — the real RL.
2. A linear policy parameterised by ``self.weights`` (loaded from joblib) —
   lightweight, deterministic, used when no PPO model is present.
3. The same linear policy with default weights — guarantees the agent always
   returns a valid action even with no artefacts on disk.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import joblib
import numpy as np

try:  # pragma: no cover - optional heavy deps
    import gymnasium as gym
    from gymnasium import spaces

    _GYM_AVAILABLE = True
except Exception:  # pragma: no cover
    _GYM_AVAILABLE = False

try:  # pragma: no cover
    from stable_baselines3 import PPO

    _SB3_AVAILABLE = True
except Exception:  # pragma: no cover
    _SB3_AVAILABLE = False


OBS_DIM = 9


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


# ---------------------------------------------------------------------------
# Gymnasium environment: optimal execution / implementation shortfall
# ---------------------------------------------------------------------------

if _GYM_AVAILABLE:

    class TradingExecutionEnv(gym.Env):
        """Simulates executing a parent order over a finite horizon.

        Observation (9-d, all roughly in [0, 1] or small):
            0 remaining_qty_pct   1 time_remaining_pct  2 spread
            3 volatility          4 trend (0..1, .5=flat) 5 bid_depth
            6 ask_depth           7 momentum            8 urgency
        Action: continuous scalar in [0, 1] = aggressiveness.
        Reward: negative implementation shortfall (impact + timing cost).
        """

        metadata: dict = {}

        def __init__(self, horizon: int = 20, seed: int | None = None) -> None:
            super().__init__()
            self.horizon = horizon
            self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(OBS_DIM,), dtype=np.float32)
            self.action_space = spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)
            self._rng = np.random.default_rng(seed)
            self._reset_state()

        def _reset_state(self) -> None:
            self.t = 0
            self.remaining = 1.0          # fraction of parent order left
            self.arrival_price = 100.0
            self.price = self.arrival_price
            self.volatility = float(self._rng.uniform(0.05, 0.5))
            # drift sign known to the agent via the trend feature; for a BUY,
            # rising price => execute sooner.
            self.drift = float(self._rng.normal(0.0, 0.02))
            self.spread = float(self._rng.uniform(0.01, 0.1))
            self.impact_coef = 0.02

        def reset(self, *, seed: int | None = None, options: dict | None = None):
            if seed is not None:
                self._rng = np.random.default_rng(seed)
            self._reset_state()
            return self._obs(), {}

        def _obs(self) -> np.ndarray:
            time_rem = 1.0 - self.t / self.horizon
            trend = float(np.clip(0.5 + self.drift * 10.0, 0.0, 1.0))
            momentum = float(np.clip(0.5 + (self.price - self.arrival_price), 0.0, 1.0))
            urgency = float(np.clip(1.0 - time_rem + self.remaining, 0.0, 1.0))
            return np.array([
                self.remaining,
                time_rem,
                self.spread,
                self.volatility,
                trend,
                0.5, 0.5,            # static depth proxies
                momentum,
                urgency,
            ], dtype=np.float32)

        def step(self, action):
            a = float(np.clip(np.asarray(action).reshape(-1)[0], 0.0, 1.0))
            self.t += 1
            terminal = self.t >= self.horizon

            # Price evolves with drift + noise.
            self.price *= (1.0 + self.drift + self._rng.normal(0.0, self.volatility * 0.1))

            # Fill a fraction of what's left, more if aggressive.
            fill = a * self.remaining
            if terminal:
                fill = self.remaining          # force-complete at the end
            fill = float(np.clip(fill, 0.0, self.remaining))
            self.remaining -= fill

            # Cost = temporary impact (∝ aggressiveness) + half-spread, vs arrival.
            impact = self.impact_coef * a + (self.spread * 0.5 if terminal else 0.0)
            exec_price = self.price * (1.0 + impact)
            shortfall = (exec_price - self.arrival_price) / self.arrival_price * fill
            reward = -shortfall * 100.0  # scale for learning signal

            done = terminal or self.remaining <= 1e-6
            return self._obs(), float(reward), bool(done), False, {'fill': fill}

else:  # pragma: no cover - gym not installed
    class TradingExecutionEnv:  # type: ignore
        def __init__(self, *a, **k) -> None:
            raise RuntimeError('gymnasium is required for TradingExecutionEnv')


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

# Default linear-policy weights. Positive sum => monotonic in aggressiveness
# w.r.t. uniformly larger state (used by the heuristic fallback).
_DEFAULT_WEIGHTS = np.array([0.2, 0.1, -0.1, -0.15, 0.2, 0.05, 0.05, 0.15, 0.35], dtype=float)


class PPOExecutionAgent:
    def __init__(self, model_path: str | None = None) -> None:
        self.weights = _DEFAULT_WEIGHTS.copy()
        self._ppo = None                 # stable-baselines3 model if loaded
        self._mode = 'linear'
        if model_path:
            self.load_model(model_path)

    # -- training -----------------------------------------------------------

    def train(
        self,
        env: "TradingExecutionEnv | None" = None,
        total_timesteps: int = 100_000,
        save_path: str | None = None,
    ) -> "PPOExecutionAgent":
        """Train a real PPO policy. Requires stable-baselines3 + gymnasium."""
        if not (_SB3_AVAILABLE and _GYM_AVAILABLE):
            raise RuntimeError('stable-baselines3 and gymnasium are required to train PPO')
        env = env or TradingExecutionEnv()
        model = PPO(
            'MlpPolicy', env,
            learning_rate=3e-4, n_steps=2048, batch_size=64, n_epochs=10,
            gamma=0.99, gae_lambda=0.95, clip_range=0.2, ent_coef=0.0, verbose=0,
        )
        model.learn(total_timesteps=total_timesteps)
        self._ppo = model
        self._mode = 'ppo'
        if save_path:
            self.save_ppo(save_path)
        return self

    # -- inference ----------------------------------------------------------

    def predict_action(self, state: np.ndarray) -> ExecutionAction:
        obs = np.asarray(state, dtype=np.float32).reshape(-1)
        if obs.shape[0] < OBS_DIM:
            obs = np.pad(obs, (0, OBS_DIM - obs.shape[0]))
        else:
            obs = obs[:OBS_DIM]

        if self._mode == 'ppo' and self._ppo is not None:
            action, _ = self._ppo.predict(obs, deterministic=True)
            urgency = float(np.clip(np.asarray(action).reshape(-1)[0], 0.0, 1.0))
        else:
            score = float(np.dot(self.weights, obs))
            urgency = float(np.clip(0.5 + score, 0.0, 1.0))

        if urgency < 0.35:
            action_type = ActionType.WAIT
        elif urgency < 0.65:
            action_type = ActionType.LIMIT
        elif urgency < 0.85:
            action_type = ActionType.TWAP
        else:
            action_type = ActionType.MARKET
        return ExecutionAction(
            action_type=action_type,
            urgency=urgency,
            limit_offset=float((0.5 - urgency) * 0.001),
        )

    # -- persistence --------------------------------------------------------

    def save_model(self, path: str) -> None:
        """Persist the linear-policy weights (joblib)."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({'weights': self.weights}, path)

    def load_model(self, path: str) -> None:
        """Load a PPO ``.zip`` if present, else linear weights from joblib."""
        p = Path(path)
        zip_path = p if p.suffix == '.zip' else p.with_suffix('.zip')
        if _SB3_AVAILABLE and zip_path.exists():
            try:
                self._ppo = PPO.load(str(zip_path))
                self._mode = 'ppo'
                return
            except Exception:
                pass
        if p.exists():
            data = joblib.load(p)
            if 'weights' in data:
                self.weights = np.asarray(data['weights'], dtype=float)
                self._mode = 'linear'

    def save_ppo(self, path: str) -> None:
        if self._ppo is not None:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            self._ppo.save(path)
