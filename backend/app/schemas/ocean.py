from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ObservationBase(BaseModel):
    parameter: str
    value: float
    unit: str
    time: datetime
    latitude: float
    longitude: float
    depth_m: Optional[float] = 0.0
    source: str
    qc_flag: int = 1
    is_ocean: bool = True
    metadata_json: Optional[Dict[str, Any]] = None


class ObservationResponse(ObservationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class TimeSeriesPoint(BaseModel):
    time: datetime
    value: float
    parameter: str
    unit: str
    source: str
    qc_flag: int


class ParameterTimeSeriesResponse(BaseModel):
    parameter: str
    unit: str
    latitude: float
    longitude: float
    ocean_basin: Optional[str] = "Ocean Basin"
    data_points: List[TimeSeriesPoint]


class GridCell(BaseModel):
    latitude: float
    longitude: float
    value: float
    unit: str
    anomaly: Optional[float] = None


class ParameterGridResponse(BaseModel):
    parameter: str
    unit: str
    timestamp: datetime
    grid_cells: List[GridCell]
    geojson: Dict[str, Any]
