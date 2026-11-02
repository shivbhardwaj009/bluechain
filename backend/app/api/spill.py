"""API endpoints for Lagrangian marine oil spill simulation."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import SpillSimulation
from backend.app.schemas.spill import SpillSimulationRequest, SpillSimulationResponse
from backend.app.oipe.geospatial_risk.spill_drift import LagrangianSpillSimulator
from backend.app.oipe.data_collection.ocean_mask import is_ocean_point

router = APIRouter(prefix="/spill", tags=["Oil Spill Drift Simulator"])


@router.post("/simulate", response_model=SpillSimulationResponse)
def run_spill_simulation(
    req: SpillSimulationRequest,
    db: Session = Depends(get_db)
):
    """Execute 72-hour Lagrangian oil spill trajectory simulation with advection, wind drift, and diffusion."""
    if not is_ocean_point(req.latitude, req.longitude):
        raise HTTPException(
            status_code=400,
            detail=f"Requested spill origin ({req.latitude}, {req.longitude}) is on continental land. Strictly marine scope enforced."
        )

    try:
        res = LagrangianSpillSimulator.simulate_spill(
            origin_lat=req.latitude,
            origin_lon=req.longitude,
            volume_m3=req.volume_m3,
            start_time=req.start_time or datetime.utcnow(),
            duration_hours=req.duration_hours or 72,
            particle_count=req.particle_count or 120,
            oil_type=req.oil_type or "Medium Crude"
        )

        # Save to database
        spill_record = SpillSimulation(
            simulation_id=res["simulation_id"],
            name=res["name"],
            origin_lat=res["origin_lat"],
            origin_lon=res["origin_lon"],
            volume_m3=res["volume_m3"],
            oil_type=res["oil_type"],
            start_time=res["start_time"],
            duration_hours=res["duration_hours"],
            particle_count=req.particle_count or 120,
            particle_tracks=res["hourly_particle_tracks"],
            affected_polygon=res["affected_polygon"],
            area_km2=res["area_km2"],
            drift_distance_km=res["drift_distance_km"]
        )
        db.add(spill_record)
        db.commit()

        return SpillSimulationResponse(**res)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")
