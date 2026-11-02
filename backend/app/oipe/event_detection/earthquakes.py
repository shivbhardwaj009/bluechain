"""Offshore Subduction Earthquake & Tsunami Candidate Detection Module.
Monitors marine seismic activity to detect shallow megathrust events capable of seafloor displacement.
Criteria:
- Strictly offshore / marine location.
- Magnitude M >= 6.5.
- Hypocenter depth < 70 km (shallow oceanic lithosphere).
"""
from typing import Dict, Any, Optional
from datetime import datetime
from backend.app.oipe.data_collection.ocean_mask import is_ocean_point, get_ocean_basin


class OffshoreEarthquakeDetector:
    """Evaluates seismic events for offshore tsunami and marine displacement hazard."""

    @classmethod
    def evaluate_quake(cls, quake_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Evaluate a seismic record for offshore tsunami risk.
        
        Args:
            quake_data: Dictionary containing latitude, longitude, magnitude, depth_km, time, place
        """
        lat = quake_data.get("latitude")
        lon = quake_data.get("longitude")
        mag = quake_data.get("magnitude", 0.0)
        depth_km = quake_data.get("depth_km", 100.0)

        # 1. Strict marine-only scope
        if not is_ocean_point(lat, lon):
            return None

        # 2. Tsunami candidate criteria: M >= 6.5 and depth < 70 km
        if mag < 6.5 or depth_km >= 70.0:
            return None

        # Severity categorization
        if mag >= 7.8:
            severity = "Extreme"
            severity_score = 0.98
        elif mag >= 7.2:
            severity = "Severe"
            severity_score = 0.85
        elif mag >= 6.8:
            severity = "Strong"
            severity_score = 0.70
        else:
            severity = "Moderate"
            severity_score = 0.55

        basin = get_ocean_basin(lat, lon)
        place = quake_data.get("place", f"Offshore {basin}")
        t = quake_data.get("time", datetime.utcnow())

        explanation = (
            f"Offshore Subduction Quake: Magnitude {mag:.1f} at shallow marine depth of {depth_km:.1f} km. "
            f"Located in the {basin} ({place}). Shallow marine megathrust faulting has high potential for "
            f"vertical seafloor displacement and destructive tsunami wave generation."
        )

        # Radius approximation for acoustic / tsunami wavefront in marine zone
        r_deg = 0.8 * (mag - 5.0)
        geojson_geom = {
            "type": "Polygon",
            "coordinates": [[
                [round(lon - r_deg, 4), round(lat - r_deg, 4)],
                [round(lon + r_deg, 4), round(lat - r_deg, 4)],
                [round(lon + r_deg, 4), round(lat + r_deg, 4)],
                [round(lon - r_deg, 4), round(lat + r_deg, 4)],
                [round(lon - r_deg, 4), round(lat - r_deg, 4)]
            ]]
        }

        event_id = f"quake_{quake_data.get('event_id', f'{lat}_{lon}_{int(mag*10)}')}"

        return {
            "event_id": event_id,
            "type": "earthquake",
            "title": f"Tsunami Candidate: M{mag:.1f} Offshore Quake ({place})",
            "severity": severity,
            "severity_score": severity_score,
            "start_time": t,
            "end_time": None,
            "latitude": lat,
            "longitude": lon,
            "ocean_basin": basin,
            "explanation": explanation,
            "geojson_geometry": geojson_geom,
            "metadata_json": {
                "magnitude": mag,
                "depth_km": depth_km,
                "tsunami_potential": True,
                "epicenter_description": place
            }
        }
