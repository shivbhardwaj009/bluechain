import pytest
from backend.app.oipe.geospatial_risk.spill_drift import LagrangianSpillSimulator


def test_spill_drift_simulation_marine_success():
    res = LagrangianSpillSimulator.simulate_spill(
        origin_lat=25.0,
        origin_lon=-45.0,
        volume_m3=5000.0,
        duration_hours=72,
        particle_count=80,
        surface_current_u=0.20,
        surface_current_v=-0.10,
        wind_speed_ms=7.5
    )

    assert res["status"] == "COMPLETED"
    assert res["area_km2"] > 0.0
    assert res["drift_distance_km"] > 0.0
    assert len(res["hourly_particle_tracks"]) > 5
    assert res["affected_polygon"]["type"] == "Polygon"
    assert len(res["affected_polygon"]["coordinates"][0]) >= 3


def test_spill_drift_rejects_land_origin():
    # Attempting to start oil spill in the middle of Kansas (land) must raise ValueError
    with pytest.raises(ValueError):
        LagrangianSpillSimulator.simulate_spill(
            origin_lat=39.0,
            origin_lon=-98.0,
            volume_m3=1000.0
        )
