"""Polar Sea-Ice Extent & Calving Anomaly Detection Module.
Detects significant sea ice retreat relative to the NSIDC 1991-2020 climatological baseline.
"""
from typing import Dict, Any, Optional
from datetime import datetime


class SeaIceAnomalyDetector:
    """Detects abnormal polar sea ice extent retreat in Arctic and Antarctic basins."""

    @classmethod
    def evaluate_sea_ice_anomaly(cls, ice_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        arctic = ice_data.get("arctic", {})
        extent = arctic.get("latest_extent_million_km2", 0.0)
        baseline = arctic.get("baseline_extent_million_km2", 6.0)
        anom_pct = arctic.get("anomaly_percent", 0.0)

        # Flag if anomaly is worse than -15% relative to 1991-2020 baseline
        if anom_pct > -15.0:
            return None

        if anom_pct <= -30.0:
            severity = "Severe"
            severity_score = 0.88
        elif anom_pct <= -20.0:
            severity = "Strong"
            severity_score = 0.72
        else:
            severity = "Moderate"
            severity_score = 0.55

        explanation = (
            f"Arctic Sea-Ice Extent Deficit: Current extent is {extent:.2f} million km² vs 1991-2020 "
            f"baseline of {baseline:.2f} million km² (anomaly {anom_pct:.1f}%). Accelerated polar amplification "
            f"and open-water albedo feedback actively degrading multi-year ice pack."
        )

        geojson_geom = {
            "type": "Polygon",
            "coordinates": [[
                [-180.0, 75.0], [180.0, 75.0], [180.0, 90.0], [-180.0, 90.0], [-180.0, 75.0]
            ]]
        }

        return {
            "event_id": f"seaice_arctic_{datetime.utcnow().strftime('%Y%m')}",
            "type": "sea_ice_loss",
            "title": f"Polar Sea-Ice Deficit: Arctic Basin ({anom_pct:.1f}% vs baseline)",
            "severity": severity,
            "severity_score": severity_score,
            "start_time": datetime.utcnow(),
            "end_time": None,
            "latitude": 82.0,
            "longitude": 0.0,
            "ocean_basin": "Arctic Ocean",
            "explanation": explanation,
            "geojson_geometry": geojson_geom,
            "metadata_json": {
                "latest_extent_mil_km2": extent,
                "baseline_extent_mil_km2": baseline,
                "anomaly_percent": anom_pct,
                "baseline_period": "1991-2020"
            }
        }
