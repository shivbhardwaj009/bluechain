"""API endpoints for controlling and monitoring data ingestion pipelines."""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import IngestionLog, OceanEvent
from backend.app.oipe.data_collection.connectors import (
    OISSTConnector,
    CopernicusMarineConnector,
    USGSEarthquakeConnector,
    IBTrACSConnector,
    NSIDCSeaIceConnector,
    MarineMeteoConnector
)
from backend.app.oipe.event_detection.heatwaves import MarineHeatwaveDetector
from backend.app.oipe.event_detection.earthquakes import OffshoreEarthquakeDetector
from backend.app.oipe.event_detection.cyclones import TropicalCycloneDetector
from backend.app.oipe.event_detection.algal_blooms import AlgalBloomDetector
from backend.app.oipe.event_detection.sea_ice import SeaIceAnomalyDetector

router = APIRouter(prefix="/ingest", tags=["Data Ingestion & Event Sync"])

CONNECTOR_MAP = {
    "oisst": OISSTConnector,
    "copernicus": CopernicusMarineConnector,
    "usgs": USGSEarthquakeConnector,
    "ibtracs": IBTrACSConnector,
    "nsidc": NSIDCSeaIceConnector,
    "meteo": MarineMeteoConnector
}


def run_full_sync(db: Session) -> Dict[str, Any]:
    """Execute full ingestion pipeline across all connectors and trigger event detectors."""
    results = []

    # 1. Ingest observations
    for key, conn_cls in CONNECTOR_MAP.items():
        connector = conn_cls()
        res = connector.ingest_and_validate(db)
        results.append(res)

    # 2. Trigger Event Detectors and persist events
    events_created = 0

    # A. Marine Heatwaves from OISST sample
    import json, os
    from backend.app.core.config import settings
    oisst_file = os.path.join(settings.SAMPLE_DATA_DIR, "oisst_sst_sample.json")
    if os.path.exists(oisst_file):
        with open(oisst_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        for reg in data.get("regions", []):
            mhw = MarineHeatwaveDetector.detect_mhw_from_timeseries(
                region_name=reg["name"],
                lat=reg["lat"],
                lon=reg["lon"],
                timeseries=reg.get("timeseries", []),
                climatology_90th=reg.get("climatology_90th_pct", 28.0)
            )
            if mhw:
                existing = db.query(OceanEvent).filter(OceanEvent.event_id == mhw["event_id"]).first()
                if not existing:
                    db.add(OceanEvent(**mhw))
                    events_created += 1

    # B. Offshore Quakes from USGS
    usgs_file = os.path.join(settings.SAMPLE_DATA_DIR, "usgs_earthquakes_sample.json")
    if os.path.exists(usgs_file):
        with open(usgs_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        for feat in data.get("features", []):
            coords = feat.get("geometry", {}).get("coordinates", [0, 0, 0])
            props = feat.get("properties", {})
            q_res = OffshoreEarthquakeDetector.evaluate_quake({
                "latitude": coords[1],
                "longitude": coords[0],
                "depth_km": coords[2],
                "magnitude": props.get("mag", 0.0),
                "place": props.get("place"),
                "event_id": feat.get("id")
            })
            if q_res:
                existing = db.query(OceanEvent).filter(OceanEvent.event_id == q_res["event_id"]).first()
                if not existing:
                    db.add(OceanEvent(**q_res))
                    events_created += 1

    # C. Cyclones from IBTrACS
    ibtracs_file = os.path.join(settings.SAMPLE_DATA_DIR, "ibtracs_cyclones_sample.json")
    if os.path.exists(ibtracs_file):
        with open(ibtracs_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        for cyc in data.get("cyclones", []):
            c_res = TropicalCycloneDetector.evaluate_cyclone(cyc)
            if c_res:
                existing = db.query(OceanEvent).filter(OceanEvent.event_id == c_res["event_id"]).first()
                if not existing:
                    db.add(OceanEvent(**c_res))
                    events_created += 1

    # D. Harmful Algal Blooms from Copernicus
    cmems_file = os.path.join(settings.SAMPLE_DATA_DIR, "copernicus_ocean_sample.json")
    if os.path.exists(cmems_file):
        with open(cmems_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        for pt in data.get("points", []):
            b_res = AlgalBloomDetector.evaluate_bloom(pt)
            if b_res:
                existing = db.query(OceanEvent).filter(OceanEvent.event_id == b_res["event_id"]).first()
                if not existing:
                    db.add(OceanEvent(**b_res))
                    events_created += 1

    # E. Sea Ice Anomaly from NSIDC
    nsidc_file = os.path.join(settings.SAMPLE_DATA_DIR, "nsidc_seaice_sample.json")
    if os.path.exists(nsidc_file):
        with open(nsidc_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        i_res = SeaIceAnomalyDetector.evaluate_sea_ice_anomaly(data)
        if i_res:
            existing = db.query(OceanEvent).filter(OceanEvent.event_id == i_res["event_id"]).first()
            if not existing:
                db.add(OceanEvent(**i_res))
                events_created += 1

    db.commit()

    return {
        "status": "COMPLETED",
        "connectors_executed": len(results),
        "events_flagged_and_persisted": events_created,
        "details": results
    }


@router.post("/{source}")
def trigger_ingestion(source: str, db: Session = Depends(get_db)):
    """Trigger ingestion pipeline for a specific oceanic data source or 'all'."""
    src_clean = source.lower().strip()
    if src_clean == "all":
        return run_full_sync(db)

    conn_cls = CONNECTOR_MAP.get(src_clean)
    if not conn_cls:
        valid_sources = list(CONNECTOR_MAP.keys()) + ["all"]
        raise HTTPException(status_code=400, detail=f"Invalid source '{source}'. Valid options: {valid_sources}")

    connector = conn_cls()
    res = connector.ingest_and_validate(db)
    return res


@router.get("/logs")
def get_ingestion_logs(limit: int = 25, db: Session = Depends(get_db)):
    """Retrieve audit log of recent ingestion and QC rejection events."""
    logs = db.query(IngestionLog).order_by(IngestionLog.timestamp.desc()).limit(limit).all()
    return logs
