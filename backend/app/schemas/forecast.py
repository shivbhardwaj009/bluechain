from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class ForecastPoint(BaseModel):
    horizon_days: int
    valid_time: datetime
    predicted_value: float
    uncertainty_lower: Optional[float] = None
    uncertainty_upper: Optional[float] = None
    baseline_value: Optional[float] = None
    latitude: float
    longitude: float
    model_version: str


class ParameterForecastResponse(BaseModel):
    parameter: str
    target_region: Optional[str] = "Global Ocean"
    forecast_time: datetime
    horizon_days: int
    data_points: List[ForecastPoint]
    model_metadata: Dict[str, Any]
    geojson: Dict[str, Any]


class SeaIceExtentResponse(BaseModel):
    basin: str  # Arctic or Antarctic
    latest_extent_million_km2: float
    baseline_extent_million_km2: float
    anomaly_percent: float
    trend_description: str
    monthly_historical: List[Dict[str, Any]]
    monthly_projection: List[Dict[str, Any]]
