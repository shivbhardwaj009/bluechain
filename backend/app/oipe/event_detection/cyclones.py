"""Tropical Cyclone Marine Event Detection & Tracking Module.
Parses IBTrACS tracks, identifies category intensity and marine sea-state hazards.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.app.oipe.data_collection.ocean_mask import is_ocean_point, get_ocean_basin


class TropicalCycloneDetector:
    """Detects and categorizes active tropical cyclones in ocean basins."""

    @classmethod
    def evaluate_cyclone(cls, cyclone_raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        sid = cyclone_raw.get("sid", "unknown")
        name = cyclone_raw.get("name", "Unnamed Cyclone")
        track = cyclone_raw.get("track", [])
        if not track:
            return None

        # Latest track point
        latest_pt = track[-1]
        lat = latest_pt.get("lat", 0.0)
        lon = latest_pt.get("lon", 0.0)
        wind_kt = latest_pt.get("wind_kt", 0.0)
        pressure_mb = latest_pt.get("pressure_mb", 1010.0)

        # Marine verification
        if not is_ocean_point(lat, lon):
            return None

        # Saffir-Simpson / BOM Scale
        if wind_kt >= 137:
            severity = "Extreme"
            severity_score = 1.0
            category_desc = "Category 5 Super Typhoon / Cyclone"
        elif wind_kt >= 113:
            severity = "Severe"
            severity_score = 0.90
            category_desc = "Category 4 Major Cyclone"
        elif wind_kt >= 96:
            severity = "Strong"
            severity_score = 0.78
            category_desc = "Category 3 Severe Tropical Cyclone"
        elif wind_kt >= 64:
            severity = "Moderate"
            severity_score = 0.60
            category_desc = "Category 1-2 Tropical Cyclone"
        else:
            severity = "Moderate"
            severity_score = 0.40
            category_desc = "Tropical Storm"

        basin = cyclone_raw.get("basin") or get_ocean_basin(lat, lon)
        t_str = latest_pt.get("time")
        t = datetime.fromisoformat(t_str.replace("Z", "+00:00")) if isinstance(t_str, str) else datetime.utcnow()

        explanation = (
            f"Active Marine Cyclone '{name}' ({category_desc}) traversing {basin}. "
            f"Sustained 1-min ocean winds of {wind_kt} knots ({round(wind_kt * 1.852)} km/h), central pressure {pressure_mb} mb. "
            f"Severe risk of catastrophic wave action, storm surge, and oceanic thermal mixing."
        )

        geojson_geom = {
            "type": "LineString",
            "coordinates": [[pt["lon"], pt["lat"]] for pt in track]
        }

        return {
            "event_id": f"cyclone_{sid}",
            "type": "cyclone",
            "title": f"Tropical Cyclone: {name} ({category_desc})",
            "severity": severity,
            "severity_score": severity_score,
            "start_time": datetime.fromisoformat(track[0]["time"].replace("Z", "+00:00")),
            "end_time": t,
            "latitude": lat,
            "longitude": lon,
            "ocean_basin": basin,
            "explanation": explanation,
            "geojson_geometry": geojson_geom,
            "metadata_json": {
                "sid": sid,
                "cyclone_name": name,
                "wind_kt": wind_kt,
                "pressure_mb": pressure_mb,
                "category": category_desc,
                "track_points_count": len(track)
            }
        }
