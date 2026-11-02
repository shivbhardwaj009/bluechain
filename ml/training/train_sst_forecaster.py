"""Training Pipeline for SST Anomaly Multi-Horizon Forecaster.
Runs time-based train/validation split, fits XGBoost/GradientBoosting models for 7, 14, and 30-day horizons,
evaluates performance against persistence baseline, and serializes versioned artifacts.
"""
import os
import json
from datetime import datetime, timedelta
import joblib
import numpy as np
import pandas as pd

from backend.app.oipe.ml_forecasting.features import generate_sst_features
from backend.app.oipe.ml_forecasting.models import MultiHorizonForecaster, PersistenceBaselineModel
from backend.app.oipe.ml_forecasting.evaluate import temporal_train_test_split, evaluate_forecast


def generate_training_data() -> pd.DataFrame:
    """Generate multi-year daily oceanic time series across representative marine basins.
    Incorporates annual cycles, ENSO-like low frequency oscillations, and marine heatwave episodes.
    """
    np.random.seed(42)
    start_date = datetime(2023, 1, 1)
    n_days = 1000  # ~3 years of daily observations

    regions = [
        {"name": "Coral Sea / GBR", "lat": -18.25, "lon": 149.50, "base_sst": 26.5, "amp": 3.2},
        {"name": "North Atlantic Gyre", "lat": 26.50, "lon": -45.00, "base_sst": 23.0, "amp": 4.5},
        {"name": "Equatorial Indian Ocean", "lat": 0.00, "lon": 78.50, "base_sst": 28.5, "amp": 1.5},
        {"name": "Barents Sea / Arctic", "lat": 74.00, "lon": 36.00, "base_sst": 3.0, "amp": 2.5},
        {"name": "Central Mediterranean", "lat": 38.00, "lon": 15.00, "base_sst": 19.5, "amp": 6.0}
    ]

    all_rows = []
    for reg in regions:
        lat = reg["lat"]
        lon = reg["lon"]
        base = reg["base_sst"]
        amp = reg["amp"]

        # Low-frequency climate anomaly (e.g. warming trend + marine heatwave pulses)
        t_arr = np.arange(n_days)
        seasonal = amp * np.sin(2.0 * np.pi * t_arr / 365.25)
        climate_trend = 0.001 * t_arr  # slight warming
        # Autoregressive anomaly process: AR(1) with rho = 0.94
        anomaly = np.zeros(n_days)
        for i in range(1, n_days):
            anomaly[i] = 0.94 * anomaly[i - 1] + np.random.normal(0, 0.22)
            # Add synthetic heatwave pulse in year 2 and year 3
            if 450 < i < 490 or 800 < i < 835:
                anomaly[i] += 0.06

        sst = base + seasonal + climate_trend + anomaly

        for d_idx in range(n_days):
            cur_date = start_date + timedelta(days=d_idx)
            all_rows.append({
                "time": cur_date,
                "latitude": lat,
                "longitude": lon,
                "sst": round(float(sst[d_idx]), 3),
                "anomaly": round(float(anomaly[d_idx]), 3)
            })

    df = pd.DataFrame(all_rows)
    return df


def main():
    print("=" * 70)
    print("BLUECHAIN OIPE: Training SST Anomaly Multi-Horizon Forecaster")
    print("=" * 70)

    # 1. Generate & Load Data
    print(">> Generating multi-year marine climatological and anomaly time series...")
    raw_df = generate_training_data()
    print(f"   Total observation records: {len(raw_df)} across 5 major ocean basins.")

    # 2. Feature Engineering
    print(">> Engineering causal features (lags, annual harmonics, rolling stats)...")
    df_feat, feature_cols = generate_sst_features(raw_df, target_col="anomaly")
    print(f"   Features ({len(feature_cols)}): {feature_cols}")

    # 3. Temporal Train / Test Split (Strictly Chronological)
    print(">> Executing time-based train/test split (80% train, 20% test)...")
    train_df, test_df = temporal_train_test_split(df_feat, test_ratio=0.20)
    print(f"   Train samples: {len(train_df)}, Test samples: {len(test_df)}")
    print(f"   Train date range: {train_df['time'].min().strftime('%Y-%m-%d')} to {train_df['time'].max().strftime('%Y-%m-%d')}")
    print(f"   Test date range:  {test_df['time'].min().strftime('%Y-%m-%d')} to {test_df['time'].max().strftime('%Y-%m-%d')}")

    X_train = train_df[feature_cols].values
    X_test = test_df[feature_cols].values

    targets_train = {
        7: train_df["target_7d"].values,
        14: train_df["target_14d"].values,
        30: train_df["target_30d"].values
    }
    targets_test = {
        7: test_df["target_7d"].values,
        14: test_df["target_14d"].values,
        30: test_df["target_30d"].values
    }

    # 4. Fit MultiHorizon Model
    print(">> Training Gradient Boosted / XGBoost Forecasters (7, 14, 30-day horizons)...")
    forecaster = MultiHorizonForecaster(use_xgboost=True)
    forecaster.fit(X_train, targets_train, feature_cols)

    # 5. Evaluate Against Persistence Baseline
    print("\n" + "=" * 70)
    print("EVALUATION RESULTS (MODEL VS PERSISTENCE BASELINE)")
    print("=" * 70)
    print(f"{'Horizon':<10} | {'Model MAE':<10} | {'Base MAE':<10} | {'Model RMSE':<10} | {'Base RMSE':<10} | {'Skill Gain':<10}")
    print("-" * 70)

    # Persistence baseline (uses lag_1d, index 4 in feature_cols)
    lag_1d_idx = feature_cols.index("lag_1d")
    base_preds = X_test[:, lag_1d_idx]

    test_preds = forecaster.predict(X_test)
    metrics_summary = {}

    for h in [7, 14, 30]:
        y_true = targets_test[h]
        y_pred = test_preds[h]
        metrics = evaluate_forecast(y_true, y_pred, base_preds)
        metrics_summary[f"{h}d"] = metrics

        print(
            f"{f'{h} Days':<10} | "
            f"{metrics['mae']:<10.4f} | "
            f"{metrics['baseline_mae']:<10.4f} | "
            f"{metrics['rmse']:<10.4f} | "
            f"{metrics['baseline_rmse']:<10.4f} | "
            f"{metrics['skill_score_pct']:>8.2f}%"
        )
    print("=" * 70)

    # 6. Save Artifacts
    models_dir = os.path.join(os.getcwd(), "ml", "models")
    os.makedirs(models_dir, exist_ok=True)

    model_path = os.path.join(models_dir, "sst_xgboost_v1.joblib")
    meta_path = os.path.join(models_dir, "sst_xgboost_v1_meta.json")

    print(f">> Serializing model artifact to {model_path}...")
    joblib.dump(forecaster, model_path)

    metadata = {
        "model_version": "v1.0.0",
        "model_type": "MultiHorizon_GradientBoosting_SST_Forecaster",
        "trained_at": datetime.utcnow().isoformat(),
        "horizons_days": [7, 14, 30],
        "feature_columns": feature_cols,
        "metrics_test": metrics_summary,
        "scientific_framework": "Lagged Autoregressive + Seasonal Harmonics + Spatial Coordinate Normalization",
        "baseline_comparison": "Persistence (y_t+h = y_t)"
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f">> Metadata successfully saved to {meta_path}")
    print(">> Training complete!")


if __name__ == "__main__":
    main()
