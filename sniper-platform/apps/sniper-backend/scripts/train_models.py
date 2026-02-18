from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np


def train_placeholder_models() -> None:
    out_dir = Path(__file__).resolve().parents[1] / 'models'
    out_dir.mkdir(parents=True, exist_ok=True)

    # Placeholder artifacts to satisfy startup loading contracts.
    joblib.dump({'weights': np.random.randn(9)}, out_dir / 'ppo_execution.joblib')
    joblib.dump({'threshold': 0.7}, out_dir / 'meta_labeler.joblib')
    joblib.dump({'states': ['TRENDING', 'MEAN_REVERTING', 'VOLATILE']}, out_dir / 'hmm_regime.joblib')

    print(f'Models saved in {out_dir}')


if __name__ == '__main__':
    train_placeholder_models()
