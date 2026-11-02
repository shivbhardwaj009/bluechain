"""Forecasting Models: Persistence Baseline, Linear Regressor, and Gradient Boosted Tree Forecasters.
Provides unified interface for multi-horizon (7, 14, 30 days) oceanic anomaly prediction.
"""
from typing import Dict, Any, List, Optional
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.ensemble import GradientBoostingRegressor

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False


class PersistenceBaselineModel:
    """Predicts that future anomaly will equal the latest observed anomaly (t = 0)."""

    def fit(self, X: np.ndarray, y: np.ndarray):
        # Persistence has no parameters to fit
        return self

    def predict(self, X: np.ndarray, lag_1d_index: int = 4) -> np.ndarray:
        # X[:, lag_1d_index] is the latest observed lag_1d
        return X[:, lag_1d_index].copy()


class MultiHorizonForecaster:
    """Wraps ML and baseline models for 7, 14, and 30-day forecast horizons."""

    def __init__(self, use_xgboost: bool = True):
        self.horizons = [7, 14, 30]
        self.use_xgboost = use_xgboost and HAS_XGBOOST
        self.models: Dict[int, Any] = {}
        self.feature_names: List[str] = []

    def fit(self, X: np.ndarray, targets: Dict[int, np.ndarray], feature_names: List[str]):
        self.feature_names = feature_names
        for h in self.horizons:
            y = targets[h]
            # Valid non-nan indices
            valid_mask = ~np.isnan(y)
            X_valid = X[valid_mask]
            y_valid = y[valid_mask]

            if self.use_xgboost:
                model = xgb.XGBRegressor(
                    n_estimators=120,
                    learning_rate=0.06,
                    max_depth=4,
                    subsample=0.85,
                    colsample_bytree=0.85,
                    random_state=42
                )
            else:
                model = GradientBoostingRegressor(
                    n_estimators=100,
                    learning_rate=0.06,
                    max_depth=4,
                    random_state=42
                )

            model.fit(X_valid, y_valid)
            self.models[h] = model

    def predict(self, X: np.ndarray) -> Dict[int, np.ndarray]:
        predictions = {}
        for h in self.horizons:
            if h in self.models:
                predictions[h] = self.models[h].predict(X)
        return predictions
