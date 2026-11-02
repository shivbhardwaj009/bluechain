import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_events_geojson_endpoint():
    response = client.get("/api/events")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert "features" in data
    assert "total_count" in data


def test_parameter_timeseries_marine_coordinate():
    # Coral Sea marine coordinate (-18.25, 149.50)
    response = client.get("/api/parameters/sst/timeseries?lat=-18.25&lon=149.50")
    assert response.status_code == 200
    data = response.json()
    assert data["parameter"] == "sst"
    assert "data_points" in data


def test_parameter_timeseries_rejects_land_coordinate():
    # Kansas continental coordinate (39.0, -98.0)
    response = client.get("/api/parameters/sst/timeseries?lat=39.0&lon=-98.0")
    assert response.status_code == 400
    assert "Strictly marine scope enforced" in response.json()["detail"]


def test_forecast_sst_endpoint():
    response = client.get("/api/forecast/sst?horizon=7")
    assert response.status_code == 200
    data = response.json()
    assert data["parameter"] == "sst"
    assert data["horizon_days"] == 7
    assert len(data["data_points"]) > 0
    assert data["geojson"]["type"] == "FeatureCollection"


def test_gridded_risk_endpoint():
    response = client.get("/api/risk")
    assert response.status_code == 200
    data = response.json()
    assert data["mean_risk_score"] > 0
    assert "geojson" in data
    assert len(data["top_risk_regions"]) > 0


def test_ecosystem_stress_summary_endpoint():
    response = client.get("/api/risk/ecosystem-summary")
    assert response.status_code == 200
    data = response.json()
    assert "mhw_bleaching_stress" in data
    assert "top_stressed_marine_ecoregions" in data


def test_sea_ice_extent_endpoint():
    response = client.get("/api/ice/extent?basin=arctic")
    assert response.status_code == 200
    data = response.json()
    assert data["basin"] == "Arctic"
    assert "latest_extent_million_km2" in data
    assert "monthly_projection" in data


def test_oil_spill_simulation_api():
    payload = {
        "latitude": 24.5,
        "longitude": -45.0,
        "volume_m3": 3000.0,
        "duration_hours": 72,
        "particle_count": 60
    }
    response = client.post("/api/spill/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["area_km2"] > 0
    assert "affected_polygon" in data
