from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class EventBase(BaseModel):
    event_id: str
    type: str  # marine_heatwave, earthquake, cyclone, algal_bloom, sea_ice_loss
    title: str
    severity: str  # Moderate, Strong, Severe, Extreme, High
    severity_score: float = Field(default=0.0, ge=0.0, le=1.0)
    start_time: datetime
    end_time: Optional[datetime] = None
    latitude: float
    longitude: float
    geojson_geometry: Optional[Dict[str, Any]] = None
    ocean_basin: Optional[str] = None
    explanation: str
    metadata_json: Optional[Dict[str, Any]] = None


class EventResponse(EventBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class EventGeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: Dict[str, Any]
    properties: Dict[str, Any]


class EventGeoJSONResponse(BaseModel):
    type: str = "FeatureCollection"
    features: List[EventGeoJSONFeature]
    total_count: int
