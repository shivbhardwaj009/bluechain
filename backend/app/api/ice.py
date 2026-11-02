"""API endpoints for polar sea-ice extent and climate baseline comparisons."""
import os
import json
from typing import Optional
from fastapi import APIRouter, Query, HTTPException

from backend.app.schemas.forecast import SeaIceExtentResponse
from backend.app.core.config import settings

router = APIRouter(prefix="/ice", tags=["Polar Sea Ice"])


@router.get("/extent", response_model=SeaIceExtentResponse)
def get_sea_ice_extent(
    basin: str = Query("arctic", description="Polar basin: 'arctic' or 'antarctic'")
):
    """Retrieve polar sea-ice extent against the NSIDC 1991-2020 climatological baseline."""
    basin_lower = basin.lower()
    if basin_lower not in ("arctic", "antarctic"):
        raise HTTPException(status_code=400, detail="Basin must be either 'arctic' or 'antarctic'")

    sample_path = os.path.join(settings.SAMPLE_DATA_DIR, "nsidc_seaice_sample.json")
    with open(sample_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    bdata = data.get(basin_lower, {})

    desc = (
        f"Accelerated polar sea ice decline in the {basin_lower.capitalize()} basin. "
        f"Current anomaly of {bdata.get('anomaly_percent', 0.0):.1f}% relative to 1991-2020 mean."
    )

    return SeaIceExtentResponse(
        basin=basin_lower.capitalize(),
        latest_extent_million_km2=bdata.get("latest_extent_million_km2", 0.0),
        baseline_extent_million_km2=bdata.get("baseline_extent_million_km2", 0.0),
        anomaly_percent=bdata.get("anomaly_percent", 0.0),
        trend_description=desc,
        monthly_historical=bdata.get("monthly_records", []),
        monthly_projection=bdata.get("projections", [])
    )
