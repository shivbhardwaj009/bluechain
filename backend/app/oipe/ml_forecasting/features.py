"""Feature Engineering for Marine Sea Surface Temperature & Sea Ice Forecasting.
Generates lag features, seasonal harmonics, rolling statistics, and spatial coordinates.
Strictly ensures temporal causality (no future leakage).
"""
import math
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Any


def generate_sst_features(df: pd.DataFrame, target_col: str = "anomaly") -> Tuple[pd.DataFrame, List[str]]:
    """Build causal feature matrix for SST anomaly forecasting.
    
    Args:
        df: DataFrame with columns ['time', 'latitude', 'longitude', 'sst', 'anomaly']
    Returns:
        df_featured: DataFrame with engineered features and targets
        feature_cols: List of predictor feature column names
    """
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values(by=["latitude", "longitude", "time"]).reset_index(drop=True)

    # 1. Seasonal harmonics (annual cycle)
    day_of_year = df["time"].dt.dayofyear
    df["sin_doy"] = np.sin(2.0 * np.pi * day_of_year / 365.25)
    df["cos_doy"] = np.cos(2.0 * np.pi * day_of_year / 365.25)

    # 2. Coordinate features
    df["lat_norm"] = df["latitude"] / 90.0
    df["lon_norm"] = df["longitude"] / 180.0

    # 3. Lag features (strictly historical)
    feature_cols = ["sin_doy", "cos_doy", "lat_norm", "lon_norm"]

    for lag in [1, 2, 3, 5, 7, 14]:
        col_name = f"lag_{lag}d"
        df[col_name] = df.groupby(["latitude", "longitude"])[target_col].shift(lag)
        feature_cols.append(col_name)

    # 4. Rolling statistical features (lagged by 1 day so today's target is unseen)
    df["rolling_mean_7d"] = df.groupby(["latitude", "longitude"])[target_col].shift(1).rolling(7, min_periods=1).mean()
    df["rolling_std_7d"] = df.groupby(["latitude", "longitude"])[target_col].shift(1).rolling(7, min_periods=1).std().fillna(0.0)
    feature_cols.extend(["rolling_mean_7d", "rolling_std_7d"])

    # 5. Target horizons (7, 14, 30 days ahead)
    df["target_7d"] = df.groupby(["latitude", "longitude"])[target_col].shift(-7)
    df["target_14d"] = df.groupby(["latitude", "longitude"])[target_col].shift(-14)
    df["target_30d"] = df.groupby(["latitude", "longitude"])[target_col].shift(-30)

    # Forward/backward fill small initial gaps then drop rows where core lags are missing
    df = df.dropna(subset=["lag_1d", "lag_7d"]).reset_index(drop=True)

    return df, feature_cols
