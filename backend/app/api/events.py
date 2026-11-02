"""API endpoints for querying oceanic hazards and events."""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import OceanEvent
from backend.app.schemas.events import EventResponse, EventGeoJSONResponse, EventGeoJSONFeature

router = APIRouter(prefix="/events", tags=["Ocean Events"])


@router.get("", response_model=EventGeoJSONResponse)
def get_events(
    type: Optional[str] = Query(None, description="Event type: marine_heatwave, earthquake, cyclone, algal_bloom, sea_ice_loss"),
    severity: Optional[str] = Query(None, description="Filter by severity: Moderate, Strong, Severe, Extreme"),
    from_date: Optional[datetime] = Query(None, alias="from", description="Start timestamp filter (ISO 8601)"),
    to_date: Optional[datetime] = Query(None, alias="to", description="End timestamp filter (ISO 8601)"),
    bbox: Optional[str] = Query(None, description="Bounding box filter minLon,minLat,maxLon,maxLat"),
    db: Session = Depends(get_db)
):
    """Retrieve oceanic events formatted as GeoJSON FeatureCollection with scientific explanations."""
    query = db.query(OceanEvent)

    if type and type != "all":
        query = query.filter(OceanEvent.type == type)

    if severity and severity != "all":
        query = query.filter(OceanEvent.severity == severity)

    if from_date:
        query = query.filter(OceanEvent.start_time >= from_date)

    if to_date:
        query = query.filter(OceanEvent.start_time <= to_date)

    if bbox:
        try:
            parts = [float(p.strip()) for p in bbox.split(",")]
            if len(parts) == 4:
                min_lon, min_lat, max_lon, max_lat = parts
                query = query.filter(
                    OceanEvent.longitude >= min_lon,
                    OceanEvent.longitude <= max_lon,
                    OceanEvent.latitude >= min_lat,
                    OceanEvent.latitude <= max_lat
                )
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid bbox format. Expected: minLon,minLat,maxLon,maxLat")

    events = query.order_by(OceanEvent.start_time.desc()).limit(150).all()

    features = []
    for ev in events:
        geom = ev.geojson_geometry or {
            "type": "Point",
            "coordinates": [ev.longitude, ev.latitude]
        }
        props = {
            "id": ev.id,
            "event_id": ev.event_id,
            "type": ev.type,
            "title": ev.title,
            "severity": ev.severity,
            "severity_score": ev.severity_score,
            "start_time": ev.start_time.isoformat() if ev.start_time else None,
            "end_time": ev.end_time.isoformat() if ev.end_time else None,
            "latitude": ev.latitude,
            "longitude": ev.longitude,
            "ocean_basin": ev.ocean_basin,
            "explanation": ev.explanation,
            "metadata": ev.metadata_json or {}
        }
        features.append(EventGeoJSONFeature(
            type="Feature",
            geometry=geom,
            properties=props
        ))

    return EventGeoJSONResponse(
        type="FeatureCollection",
        features=features,
        total_count=len(features)
    )


@router.get("/{event_id}", response_model=EventResponse)
def get_event_detail(event_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed scientific metadata for a specific event."""
    ev = db.query(OceanEvent).filter(OceanEvent.event_id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Ocean event not found")
    return ev
