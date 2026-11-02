from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class RiskCellResponse(BaseModel):
    id: int
    hazard: str
    risk_score: float  # 0 to 100
    time: datetime
    latitude: float
    longitude: float
    ocean_basin: Optional[str] = None
    explanation: str
    contributing_factors: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(from_attributes=True)


class GriddedRiskResponse(BaseModel):
    hazard: str
    time: datetime
    mean_risk_score: float
    max_risk_score: float
    high_risk_cells_count: int
    geojson: Dict[str, Any]
    top_risk_regions: List[Dict[str, Any]]


class EcosystemStressSummary(BaseModel):
    overall_stress_index: float  # 0 to 100
    mhw_bleaching_stress: float
    algal_hypoxia_stress: float
    acidification_stress: float
    cyclone_hazard_stress: float
    top_stressed_marine_ecoregions: List[Dict[str, Any]]
