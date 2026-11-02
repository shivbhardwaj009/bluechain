from datetime import datetime
from sqlalchemy import (
    Column, Integer, Float, String, DateTime, Text, JSON, Boolean, Index
)
from backend.app.db.session import Base


class Observation(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True)
    parameter = Column(String(64), index=True, nullable=False)  # sst, salinity, chlorophyll, etc.
    value = Column(Float, nullable=False)
    unit = Column(String(32), nullable=False)
    time = Column(DateTime, index=True, nullable=False)
    latitude = Column(Float, index=True, nullable=False)
    longitude = Column(Float, index=True, nullable=False)
    depth_m = Column(Float, default=0.0)
    source = Column(String(64), index=True, nullable=False)  # noaa_oisst, cmems, usgs, etc.
    qc_flag = Column(Integer, default=1)  # 1=Good, 2=Suspect, 3=Bad/Rejected
    is_ocean = Column(Boolean, default=True)
    metadata_json = Column(JSON, nullable=True)

    __table_args__ = (
        Index("idx_obs_param_time", "parameter", "time"),
        Index("idx_obs_lat_lon", "latitude", "longitude"),
    )


class OceanEvent(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(128), unique=True, index=True, nullable=False)
    type = Column(String(64), index=True, nullable=False)  # marine_heatwave, earthquake, cyclone, algal_bloom, sea_ice_loss
    title = Column(String(256), nullable=False)
    severity = Column(String(32), index=True, nullable=False)  # Moderate, Strong, Severe, Extreme, High
    severity_score = Column(Float, default=0.0)  # Normalized 0.0 - 1.0
    start_time = Column(DateTime, index=True, nullable=False)
    end_time = Column(DateTime, nullable=True)
    latitude = Column(Float, index=True, nullable=False)
    longitude = Column(Float, index=True, nullable=False)
    geojson_geometry = Column(JSON, nullable=True)  # Point or Polygon
    ocean_basin = Column(String(64), nullable=True)  # Pacific, Atlantic, Indian, Southern, Arctic
    explanation = Column(Text, nullable=False)  # Scientific rationale of why it was flagged
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_event_type_time", "type", "start_time"),
    )


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    parameter = Column(String(64), index=True, nullable=False)  # sst_anomaly, sea_ice_extent
    horizon_days = Column(Integer, index=True, nullable=False)  # 7, 14, 30
    forecast_made_time = Column(DateTime, default=datetime.utcnow)
    valid_time = Column(DateTime, index=True, nullable=False)
    latitude = Column(Float, index=True, nullable=False)
    longitude = Column(Float, index=True, nullable=False)
    predicted_value = Column(Float, nullable=False)
    uncertainty_lower = Column(Float, nullable=True)
    uncertainty_upper = Column(Float, nullable=True)
    baseline_value = Column(Float, nullable=True)  # Persistence / linear baseline
    model_version = Column(String(64), nullable=False)
    geojson_geometry = Column(JSON, nullable=True)


class RiskCell(Base):
    __tablename__ = "risk_cells"

    id = Column(Integer, primary_key=True, index=True)
    hazard = Column(String(64), index=True, nullable=False)  # heatwave_bleaching, algal_bloom_deox, acidification, cyclone_intensification, combined
    risk_score = Column(Float, index=True, nullable=False)  # 0 to 100
    time = Column(DateTime, index=True, nullable=False)
    latitude = Column(Float, index=True, nullable=False)
    longitude = Column(Float, index=True, nullable=False)
    ocean_basin = Column(String(64), nullable=True)
    explanation = Column(Text, nullable=False)
    contributing_factors = Column(JSON, nullable=True)
    geojson_geometry = Column(JSON, nullable=True)

    __table_args__ = (
        Index("idx_risk_hazard_time", "hazard", "time"),
    )


class SpillSimulation(Base):
    __tablename__ = "spill_simulations"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    origin_lat = Column(Float, nullable=False)
    origin_lon = Column(Float, nullable=False)
    volume_m3 = Column(Float, nullable=False)
    oil_type = Column(String(64), default="Medium Crude")
    start_time = Column(DateTime, nullable=False)
    duration_hours = Column(Integer, default=72)
    particle_count = Column(Integer, default=150)
    particle_tracks = Column(JSON, nullable=False)  # Array of timestep coordinates
    affected_polygon = Column(JSON, nullable=False)  # GeoJSON Polygon / MultiPolygon
    area_km2 = Column(Float, default=0.0)
    drift_distance_km = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class IngestionLog(Base):
    __tablename__ = "ingestion_log"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(64), index=True, nullable=False)
    parameter = Column(String(64), nullable=False)
    records_ingested = Column(Integer, default=0)
    records_rejected = Column(Integer, default=0)
    status = Column(String(32), default="SUCCESS")  # SUCCESS, PARTIAL, FAILED
    error_message = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
