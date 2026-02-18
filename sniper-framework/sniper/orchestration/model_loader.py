"""
Model Loader
Loads HMM, XGBoost meta-labeler, and PPO RL agent on startup.
Handles missing files gracefully (falls back to heuristics).
"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger("sniper.orchestration.model_loader")


class ModelLoader:
    """
    Loads all ML models at startup.

    Expected directory structure:
        models/
          hmm_regime.joblib
          meta_labeler.json        (XGBoost) or meta_labeler.npy (logistic)
          ppo_execution.zip        (stable-baselines3)
    """

    def __init__(self, models_dir: str = "models") -> None:
        self._dir = Path(models_dir)
        self.hmm:          object | None = None
        self.meta_labeler: object | None = None
        self.ppo_agent:    object | None = None
        self._loaded: list[str] = []
        self._failed: list[str] = []

    def load_all(self) -> dict[str, bool]:
        """Load all models. Returns {model_name: success}."""
        results = {
            "hmm":          self._load_hmm(),
            "meta_labeler": self._load_meta_labeler(),
            "ppo_agent":    self._load_ppo(),
        }
        logger.info(
            "Model loader: loaded=%s  failed=%s",
            self._loaded,
            self._failed,
        )
        return results

    # ------------------------------------------------------------------

    def _load_hmm(self) -> bool:
        from sniper.core.strategy_engine.regime_detector import HMMRegimeDetector

        detector = HMMRegimeDetector()
        path = self._dir / "hmm_regime.joblib"
        if path.exists():
            try:
                import joblib  # type: ignore
                detector._model = joblib.load(str(path))
                detector._trained = True
                self.hmm = detector
                self._loaded.append("hmm")
                logger.info("HMM model loaded from %s", path)
                return True
            except Exception as exc:
                logger.warning("HMM load failed (%s) — using heuristic fallback", exc)

        self.hmm = detector   # heuristic mode
        self._loaded.append("hmm (heuristic)")
        return True

    def _load_meta_labeler(self) -> bool:
        from sniper.core.strategy_engine.meta_labeler import MetaLabeler

        # Try XGBoost JSON model first
        for suffix in (".json", ".npy"):
            path = self._dir / f"meta_labeler{suffix}"
            if path.exists():
                try:
                    labeler = MetaLabeler(model_path=str(path))
                    self.meta_labeler = labeler
                    self._loaded.append("meta_labeler")
                    logger.info("MetaLabeler loaded from %s", path)
                    return True
                except Exception as exc:
                    logger.warning("MetaLabeler load failed (%s)", exc)

        # Fallback: heuristic
        self.meta_labeler = MetaLabeler()
        self._loaded.append("meta_labeler (heuristic)")
        return True

    def _load_ppo(self) -> bool:
        from sniper.core.execution_engine.ppo_agent import PPOExecutionAgent

        path = self._dir / "ppo_execution.zip"
        if path.exists():
            try:
                agent = PPOExecutionAgent(model_path=str(path))
                self.ppo_agent = agent
                self._loaded.append("ppo_agent")
                logger.info("PPO agent loaded from %s", path)
                return True
            except Exception as exc:
                logger.warning("PPO load failed (%s) — using heuristic fallback", exc)

        self.ppo_agent = PPOExecutionAgent()   # heuristic
        self._loaded.append("ppo_agent (heuristic)")
        return True

    @property
    def status(self) -> dict:
        return {"loaded": self._loaded, "failed": self._failed}
