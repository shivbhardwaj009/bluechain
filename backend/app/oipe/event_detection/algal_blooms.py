"""Harmful Algal Bloom (HAB) & Marine Hypoxia Detection Module.
Identifies high-risk phytoplankton proliferation using chlorophyll-a z-score anomalies
coupled with warm sea surface temperatures.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from backend.app.oipe.data_collection.ocean_mask import is_ocean_point, get_ocean_basin


class AlgalBloomDetector:
    """Detects Harmful Algal Bloom anomalies from Copernicus biogeochemical parameters."""

    @classmethod
    def evaluate_bloom(cls, point_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        lat = point_data.get("lat")
        lon = point_data.get("lon")
        chl = point_data.get("chlorophyll_mg_m3", 0.0)
        zscore = point_data.get("chlorophyll_zscore", 0.0)
        sst = point_data.get("sst_degc", 0.0)
        do = point_data.get("dissolved_oxygen_mg_l", 6.0)

        if not is_ocean_point(lat, lon):
            return None

        # Bloom criteria: Chlorophyll z-score >= 2.0 (97.7th percentile) and warm SST >= 15.0 C
        if zscore < 2.0 or sst < 15.0:
            return None

        # Severity classification
        if zscore >= 3.5 or (chl > 12.0 and do < 3.0):
            severity = "Severe"
            severity_score = 0.90
        elif zscore >= 2.8 or do < 4.0:
            severity = "Strong"
            severity_score = 0.75
        else:
            severity = "Moderate"
            severity_score = 0.58

        basin = get_ocean_basin(lat, lon)
        name = point_data.get("name", f"Ecoregion ({lat:.1f}, {lon:.1f})")

        explanation = (
            f"Harmful Algal Bloom (HAB) anomaly in {name}: Chlorophyll-a concentration reached {chl:.2f} mg/m³ "
            f"(z-score +{zscore:.1f}σ above baseline) in warm {sst:.1f}°C surface waters. "
            f"Dissolved oxygen depressed to {do:.2f} mg/L, indicating active eutrophication, hypoxia, and marine die-off risk."
        )

        geojson_geom = {
            "type": "Polygon",
            "coordinates": [[
                [round(lon - 0.8, 4), round(lat - 0.8, 4)],
                [round(lon + 0.8, 4), round(lat - 0.8, 4)],
                [round(lon + 0.8, 4), round(lat + 0.8, 4)],
                [round(lon - 0.8, 4), round(lat + 0.8, 4)],
                [round(lon - 0.8, 4), round(lat - 0.8, 4)]
            ]]
        }

        return {
            "event_id": f"hab_{lat}_{lon}_{datetime.utcnow().strftime('%Y%m%d')}",
            "type": "algal_bloom",
            "title": f"Harmful Algal Bloom: {name} (z-score +{zscore:.1f}σ)",
            "severity": severity,
            "severity_score": severity_score,
            "start_time": datetime.utcnow(),
            "end_time": None,
            "latitude": lat,
            "longitude": lon,
            "ocean_basin": basin,
            "explanation": explanation,
            "geojson_geometry": geojson_geom,
            "metadata_json": {
                "chlorophyll_mg_m3": chl,
                "chlorophyll_zscore": zscore,
                "sst_degc": sst,
                "dissolved_oxygen_mg_l": do
            }
        }
