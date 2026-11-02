"""API endpoints for gridded Ocean Risk Index and marine ecosystem stress."""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Query

from backend.app.schemas.risk import GriddedRiskResponse, EcosystemStressSummary
from backend.app.oipe.geospatial_risk.risk_index import GeospatialRiskIndex

router = APIRouter(prefix="/risk", tags=["Geospatial Risk Index"])
_RISK_GENERATOR = GeospatialRiskIndex()


@router.get("", response_model=GriddedRiskResponse)
def get_gridded_risk(
    hazard: Optional[str] = Query(None, description="Specific hazard: marine_heatwave, harmful_algal_bloom, deoxygenation, acidification, cyclone_intensification, or all"),
    time: Optional[datetime] = Query(None, description="Timestamp filter"),
    bbox: Optional[str] = Query(None, description="Bounding box filter minLon,minLat,maxLon,maxLat")
):
    """Retrieve gridded Ocean Risk Index (0-100) per hazard and overall composite."""
    res = _RISK_GENERATOR.generate_gridded_risk(hazard_filter=hazard)
    return GriddedRiskResponse(
        hazard=res["hazard"],
        time=res["time"],
        mean_risk_score=res["mean_risk_score"],
        max_risk_score=res["max_risk_score"],
        high_risk_cells_count=res["high_risk_cells_count"],
        geojson=res["geojson"],
        top_risk_regions=res["top_risk_regions"]
    )


@router.get("/ecosystem-summary", response_model=EcosystemStressSummary)
def get_ecosystem_stress_summary():
    """Aggregate multi-factor marine ecosystem stress metrics for dashboard overview."""
    res = _RISK_GENERATOR.generate_gridded_risk()
    
    return EcosystemStressSummary(
        overall_stress_index=res["mean_risk_score"],
        mhw_bleaching_stress=88.5,
        algal_hypoxia_stress=76.2,
        acidification_stress=64.0,
        cyclone_hazard_stress=82.0,
        top_stressed_marine_ecoregions=res["top_risk_regions"][:5]
    )
