from datetime import datetime, timedelta
from backend.app.oipe.event_detection.heatwaves import MarineHeatwaveDetector
from backend.app.oipe.event_detection.earthquakes import OffshoreEarthquakeDetector
from backend.app.oipe.event_detection.algal_blooms import AlgalBloomDetector


def test_hobday_mhw_detection_success():
    # 7 consecutive days above 90th percentile (28.0 C)
    timeseries = []
    start = datetime(2026, 10, 1)
    for i in range(7):
        t = start + timedelta(days=i)
        timeseries.append({
            "time": t,
            "sst": 29.5 + (i * 0.2),
            "anomaly": 1.5 + (i * 0.2)
        })

    mhw = MarineHeatwaveDetector.detect_mhw_from_timeseries(
        region_name="Test Reef",
        lat=-18.0,
        lon=150.0,
        timeseries=timeseries,
        climatology_90th=28.0,
        climatology_mean=26.5
    )

    assert mhw is not None
    assert mhw["type"] == "marine_heatwave"
    assert mhw["severity"] in ("Strong", "Moderate", "Severe")
    assert "Hobday et al." in mhw["explanation"]
    assert mhw["metadata_json"]["duration_days"] == 7


def test_hobday_mhw_detection_fails_under_5_days():
    # Only 3 consecutive days above threshold - fails Hobday criteria
    timeseries = [
        {"time": datetime(2026, 10, 1), "sst": 29.5, "anomaly": 1.5},
        {"time": datetime(2026, 10, 2), "sst": 29.8, "anomaly": 1.8},
        {"time": datetime(2026, 10, 3), "sst": 29.2, "anomaly": 1.2},
        {"time": datetime(2026, 10, 4), "sst": 27.5, "anomaly": -0.5},
    ]

    mhw = MarineHeatwaveDetector.detect_mhw_from_timeseries(
        region_name="Test Short Pulse",
        lat=-18.0,
        lon=150.0,
        timeseries=timeseries,
        climatology_90th=28.0
    )

    assert mhw is None


def test_offshore_earthquake_detection():
    # Offshore shallow megathrust quake (M7.2, depth 25km in Kermadec Trench)
    marine_quake = {
        "latitude": -30.0,
        "longitude": -178.0,
        "magnitude": 7.2,
        "depth_km": 25.0,
        "place": "Kermadec Trench Offshore",
        "event_id": "test_kermadec"
    }
    res = OffshoreEarthquakeDetector.evaluate_quake(marine_quake)
    assert res is not None
    assert res["type"] == "earthquake"
    assert res["severity"] == "Severe"
    assert "Tsunami Candidate" in res["title"]

    # Reject onshore quake (e.g., inside mainland continent)
    land_quake = {
        "latitude": 39.0,
        "longitude": -98.0,
        "magnitude": 7.0,
        "depth_km": 10.0,
        "place": "Continental Interior"
    }
    assert OffshoreEarthquakeDetector.evaluate_quake(land_quake) is None

    # Reject deep quake (> 70 km has minimal tsunami displacement potential)
    deep_marine_quake = {
        "latitude": -30.0,
        "longitude": -178.0,
        "magnitude": 7.2,
        "depth_km": 150.0,
        "place": "Deep Mantle"
    }
    assert OffshoreEarthquakeDetector.evaluate_quake(deep_marine_quake) is None


def test_algal_bloom_detection():
    # Warm waters + high chlorophyll z-score
    bloom_point = {
        "lat": 24.5,
        "lon": 58.5,
        "chlorophyll_mg_m3": 12.5,
        "chlorophyll_zscore": 3.2,
        "sst_degc": 29.0,
        "dissolved_oxygen_mg_l": 2.4,
        "name": "Arabian Sea Bloom"
    }
    res = AlgalBloomDetector.evaluate_bloom(bloom_point)
    assert res is not None
    assert res["type"] == "algal_bloom"
    assert res["severity"] in ("Strong", "Severe")
    assert "Harmful Algal Bloom" in res["title"]
