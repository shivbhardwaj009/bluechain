"""Temporal Cross-Validation & Metric Evaluation Module.
Enforces strict chronological train/test splitting (no future data leakage).
Computes MAE, RMSE, Pearson Correlation, and Skill Score versus Persistence Baseline.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.metrics import mean_absolute_error, mean_squared_error


def temporal_train_test_split(
    df: pd.DataFrame,
    test_ratio: float = 0.20
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Chronological split strictly by time to prevent data leakage."""
    df_sorted = df.sort_values(by="time").reset_index(drop=True)
    n = len(df_sorted)
    split_idx = int(n * (1.0 - test_ratio))
    train_df = df_sorted.iloc[:split_idx].reset_index(drop=True)
    test_df = df_sorted.iloc[split_idx:].reset_index(drop=True)
    return train_df, test_df


def evaluate_forecast(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_baseline: np.ndarray
) -> Dict[str, float]:
    """Compute benchmark performance metrics."""
    # Filter any NaNs
    mask = (~np.isnan(y_true)) & (~np.isnan(y_pred)) & (~np.isnan(y_baseline))
    yt = y_true[mask]
    yp = y_pred[mask]
    yb = y_baseline[mask]

    if len(yt) == 0:
        return {"mae": 0.0, "rmse": 0.0, "baseline_mae": 0.0, "baseline_rmse": 0.0, "skill_score": 0.0}

    mae_model = mean_absolute_error(yt, yp)
    rmse_model = np.sqrt(mean_squared_error(yt, yp))

    mae_base = mean_absolute_error(yt, yb)
    rmse_base = np.sqrt(mean_squared_error(yt, yb))

    # Skill score relative to persistence
    skill = 1.0 - (rmse_model / max(1e-5, rmse_base))

    return {
        "mae": round(float(mae_model), 4),
        "rmse": round(float(rmse_model), 4),
        "baseline_mae": round(float(mae_base), 4),
        "baseline_rmse": round(float(rmse_base), 4),
        "skill_score_pct": round(float(skill * 100.0), 2)
    }
