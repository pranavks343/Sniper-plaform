"""Train real models used by the platform.

- PPO execution agent (stable-baselines3) on the order-execution env.
- HMM regime detector + XGBoost meta-labeler artefacts (best-effort).

Run:  python scripts/train_models.py [--timesteps N]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np


def _evaluate(agent, env, episodes: int = 300) -> float:
    """Mean episode reward (negative implementation shortfall) for a policy."""
    total = 0.0
    for _ in range(episodes):
        obs, _ = env.reset()
        done = False
        ep = 0.0
        while not done:
            action = agent(obs)
            obs, reward, done, trunc, _ = env.step(action)
            ep += reward
            done = done or trunc
        total += ep
    return total / episodes


def train_ppo(out_dir: Path, timesteps: int) -> None:
    from app.core.execution_engine.rl_agent import PPOExecutionAgent, TradingExecutionEnv

    print(f'[PPO] training for {timesteps} timesteps ...')
    agent = PPOExecutionAgent()
    agent.train(env=TradingExecutionEnv(seed=0), total_timesteps=timesteps,
                save_path=str(out_dir / 'ppo_execution.zip'))
    # Save linear fallback weights too (keeps legacy contract).
    joblib.dump({'weights': agent.weights}, out_dir / 'ppo_execution.joblib')

    # Benchmark trained PPO vs naive baselines on fresh episodes.
    eval_env = TradingExecutionEnv(seed=123)

    def ppo_policy(obs):
        a, _ = agent._ppo.predict(obs, deterministic=True)
        return a

    immediate = _evaluate(lambda o: np.array([1.0], dtype=np.float32), eval_env)
    twap = _evaluate(lambda o: np.array([0.5], dtype=np.float32), eval_env)
    rng = np.random.default_rng(1)
    random_p = _evaluate(lambda o: rng.uniform(0, 1, size=(1,)).astype(np.float32), eval_env)
    ppo = _evaluate(ppo_policy, eval_env)

    print('\n[PPO] mean reward (higher = lower execution shortfall):')
    print(f'   immediate-market : {immediate:8.3f}')
    print(f'   TWAP (a=0.5)     : {twap:8.3f}')
    print(f'   random           : {random_p:8.3f}')
    print(f'   PPO (trained)    : {ppo:8.3f}')
    best_base = max(immediate, twap, random_p)
    if best_base != 0:
        impr = (ppo - best_base) / abs(best_base) * 100.0
        print(f'   PPO vs best baseline: {impr:+.1f}%')


def train_research_models(out_dir: Path) -> None:
    """Train HMM regime detector + XGBoost meta-labeler on simulated data."""
    try:
        from app.core.strategy_engine.regime_detector import HMMRegimeDetector
        rng = np.random.default_rng(42)
        prices = 18000 + np.cumsum(rng.normal(0, 30, size=1500))
        det = HMMRegimeDetector(lookback=100)
        det.train(prices)
        joblib.dump({'trained': det._trained, 'lookback': det.lookback}, out_dir / 'hmm_regime.joblib')
        print('[HMM] regime detector trained.')
    except Exception as exc:  # pragma: no cover
        print(f'[HMM] skipped: {exc}')

    try:
        from app.core.strategy_engine.meta_labeler import MetaLabeler
        rng = np.random.default_rng(7)
        n = 2000
        # 5 features: signal_strength, regime_confidence, volatility, spread, time_of_day
        X = np.column_stack([
            rng.uniform(0, 1, n), rng.uniform(0, 1, n), rng.uniform(0, 1, n),
            rng.uniform(0, 1, n), rng.uniform(0, 1, n),
        ])
        logit = 2.0 * X[:, 0] + 1.5 * X[:, 1] - 1.5 * X[:, 2] - 1.2 * X[:, 3] - 1.0
        y = (1 / (1 + np.exp(-logit)) > rng.uniform(size=n)).astype(int)
        ml = MetaLabeler()
        ml.train(X, y)
        joblib.dump({'threshold': ml.threshold, 'trained': ml._trained}, out_dir / 'meta_labeler.joblib')
        print(f'[MetaLabeler] trained (xgboost={ml.model is not None}).')
    except Exception as exc:  # pragma: no cover
        print(f'[MetaLabeler] skipped: {exc}')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--timesteps', type=int, default=60_000)
    args = parser.parse_args()

    out_dir = Path(__file__).resolve().parents[1] / 'models'
    out_dir.mkdir(parents=True, exist_ok=True)

    train_ppo(out_dir, args.timesteps)
    train_research_models(out_dir)
    print(f'\nModels saved in {out_dir}')


if __name__ == '__main__':
    main()
