"""API endpoints for oceanic parameter grids and historical time-series."""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import Observation
from backend.app.schemas.ocean import ParameterTimeSeriesResponse, ParameterGridResponse, TimeSeriesPoint, GridCell
from backend.app.oipe.data_collection.ocean_mask import is_ocean_point, get_ocean_basin

router = APIRouter(prefix="/parameters", tags=["Ocean Parameters"])


@router.get("/{name}/timeseries", response_model=ParameterTimeSeriesResponse)
def get_parameter_timeseries(
    name: str,
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude"),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    db: Session = Depends(get_db)
):
    """Retrieve time-series of an ocean parameter at a specific oceanic coordinate."""
    if not is_ocean_point(lat, lon):
        raise HTTPException(
            status_code=400,
            detail=f"Requested coordinate ({lat}, {lon}) is located on continental land. Strictly marine scope enforced."
        )

    query = db.query(Observation).filter(
        Observation.parameter == name.lower(),
        Observation.latitude.between(lat - 2.5, lat + 2.5),
        Observation.longitude.between(lon - 2.5, lon + 2.5)
    )

    if from_date:
        query = query.filter(Observation.time >= from_date)
    if to_date:
        query = query.filter(Observation.time <= to_date)

    obs = query.order_by(Observation.time.asc()).limit(200).all()

    points = [
        TimeSeriesPoint(
            time=o.time,
            value=o.value,
            parameter=o.parameter,
            unit=o.unit,
            source=o.source,
            qc_flag=o.qc_flag
        )
        for o in obs
    ]

    unit = points[0].unit if points else ("degC" if "temp" in name or name == "sst" else "unit")
    basin = get_ocean_basin(lat, lon)

    return ParameterTimeSeriesResponse(
        parameter=name,
        unit=unit,
        latitude=lat,
        longitude=lon,
        ocean_basin=basin,
        data_points=points
    )


@router.get("/{name}/grid", response_model=ParameterGridResponse)
def get_parameter_grid(
    name: str,
    time: Optional[datetime] = Query(None, description="Observation timestamp"),
    db: Session = Depends(get_db)
):
    """Retrieve gridded oceanic observation field formatted as GeoJSON."""
    obs = db.query(Observation).filter(Observation.parameter == name.lower()).limit(300).all()

    grid_cells = []
    features = []
    unit = "degC" if name.lower() in ("sst", "temperature") else "standard_unit"

    for o in obs:
        unit = o.unit
        anom = o.metadata_json.get("anomaly") if o.metadata_json else None
        grid_cells.append(GridCell(
            latitude=o.latitude,
            longitude=o.longitude,
            value=o.value,
            unit=o.unit,
            anomaly=anom
        ))

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [o.longitude, o.latitude]
            },
            "properties": {
                "parameter": o.parameter,
                "value": o.value,
                "unit": o.unit,
                "anomaly": anom,
                "source": o.source,
                "time": o.time.isoformat()
            }
        }
        features.append(feature)

    return ParameterGridResponse(
        parameter=name,
        unit=unit,
        timestamp=time or datetime.utcnow(),
        grid_cells=grid_cells,
        geojson={
            "type": "FeatureCollection",
            "features": features
        }
    )
