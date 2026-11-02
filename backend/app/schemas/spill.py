from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SpillSimulationRequest(BaseModel):
    name: Optional[str] = "Deepwater Spill Simulation"
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Spill release latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Spill release longitude")
    volume_m3: float = Field(..., gt=0.0, description="Estimated spill volume in cubic meters")
    oil_type: Optional[str] = "Medium Crude"
    start_time: Optional[datetime] = None
    duration_hours: Optional[int] = Field(default=72, ge=6, le=168)
    particle_count: Optional[int] = Field(default=120, ge=30, le=500)


class SpillParticleStep(BaseModel):
    particle_id: int
    hour: int
    latitude: float
    longitude: float


class SpillSimulationResponse(BaseModel):
    simulation_id: str
    name: str
    origin_lat: float
    origin_lon: float
    volume_m3: float
    oil_type: str
    start_time: datetime
    duration_hours: int
    area_km2: float
    drift_distance_km: float
    affected_polygon: Dict[str, Any]  # GeoJSON Polygon
    hourly_particle_tracks: List[Dict[str, Any]]
    beaching_risk: str
    status: str
