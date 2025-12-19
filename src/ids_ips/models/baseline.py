from __future__ import annotations

from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


class BaselineAnomalyModel:
    """Простой baseline: IsolationForest поверх табличных фичей.

    Подходит для демонстрации экспериментов по аномалиям без разметки.
    """

    def __init__(self, model: Optional[IsolationForest] = None):
        self.model = model or IsolationForest(
            n_estimators=100,
            contamination=0.05,
            random_state=42,
        )

    def fit(self, X: pd.DataFrame) -> "BaselineAnomalyModel":
        self.model.fit(X.values)
        return self

    def score_samples(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.score_samples(X.values)

    def predict_labels(self, X: pd.DataFrame) -> np.ndarray:
        """Вернуть метки: 1 — норм, -1 — аномалия (как в sklearn)."""
        return self.model.predict(X.values)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)

    @classmethod
    def load(cls, path: Path) -> "BaselineAnomalyModel":
        model = joblib.load(path)
        return cls(model=model)


