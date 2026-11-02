"""Geospatial Risk Index Generator.
Combines scientific relationship rules, event anomalies, and spatial data into
a gridded Ocean Risk Index (0-100) delivered as standards-compliant GeoJSON.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.app.oipe.relationship_engine.engine import RelationshipEngine
from backend.app.oipe.data_collection.ocean_mask import is_ocean_point, get_ocean_basin


class GeospatialRiskIndex:
    """Computes and formats gridded ocean hazard risk indices."""

    def __init__(self):
        self.engine = RelationshipEngine()

    def generate_gridded_risk(
        self,
        grid_points: Optional[List[Dict[str, Any]]] = None,
        hazard_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compute the gridded Ocean Risk Index across ocean basins.
        
        Args:
            grid_points: Optional list of oceanic observation cells. If None, default benchmark grid is evaluated.
            hazard_filter: Optional filter ('marine_heatwave', 'harmful_algal_bloom', 'deoxygenation', 'acidification', 'cyclone_intensification')
        """
        if grid_points is None:
            grid_points = [
                # Coral Sea / Great Barrier Reef
                {"lat": -18.25, "lon": 149.50, "sst": 31.2, "sst_anomaly": 2.9, "wind_speed": 2.8, "chlorophyll": 0.4, "dissolved_oxygen": 6.1, "ph": 7.98, "name": "Coral Sea / GBR Reef"},
                # North Atlantic Gyre
                {"lat": 26.50, "lon": -45.00, "sst": 28.0, "sst_anomaly": 2.8, "wind_speed": 4.5, "chlorophyll": 0.2, "dissolved_oxygen": 6.4, "ph": 8.08, "name": "North Atlantic Subtropical Gyre"},
                # Gulf of Oman / Arabian Sea Bloom
                {"lat": 24.50, "lon": 58.50, "sst": 29.8, "sst_anomaly": 1.8, "wind_speed": 3.8, "chlorophyll": 14.8, "dissolved_oxygen": 2.1, "ph": 8.02, "name": "Arabian Sea Eutrophic Zone"},
                # California Current Upwelling
                {"lat": 36.50, "lon": -123.50, "sst": 14.2, "sst_anomaly": 0.6, "wind_speed": 8.2, "chlorophyll": 5.2, "dissolved_oxygen": 2.6, "ph": 7.82, "name": "California Current Hypoxia Zone"},
                # Western Pacific Cyclone Alley
                {"lat": 16.50, "lon": 133.00, "sst": 30.6, "sst_anomaly": 1.7, "wind_speed": 18.0, "is_cyclone_present": True, "chlorophyll": 0.3, "dissolved_oxygen": 6.3, "ph": 8.12, "name": "Western Pacific Mariana Basin"},
                # Southern Ocean Polar Front
                {"lat": -56.00, "lon": -40.00, "sst": 3.2, "sst_anomaly": 0.4, "wind_speed": 12.0, "chlorophyll": 0.8, "dissolved_oxygen": 8.2, "ph": 8.04, "name": "Southern Ocean Polar Front"},
                # Equatorial Indian Ocean
                {"lat": 0.00, "lon": 78.50, "sst": 31.4, "sst_anomaly": 2.2, "wind_speed": 3.2, "chlorophyll": 0.35, "dissolved_oxygen": 5.9, "ph": 8.06, "name": "Equatorial Indian Ocean"},
                # Barents Sea / Arctic
                {"lat": 74.00, "lon": 36.00, "sst": 5.7, "sst_anomaly": 2.8, "wind_speed": 6.5, "chlorophyll": 1.1, "dissolved_oxygen": 7.8, "ph": 8.02, "name": "Barents Sea Opening"},
                # Mediterranean Basin
                {"lat": 38.00, "lon": 15.00, "sst": 24.5, "sst_anomaly": 2.4, "wind_speed": 4.1, "chlorophyll": 0.6, "dissolved_oxygen": 5.8, "ph": 8.05, "name": "Central Mediterranean"}
            ]

        geojson_features = []
        scores = []
        high_risk_cells = 0
        top_regions = []

        for pt in grid_points:
            lat = pt["lat"]
            lon = pt["lon"]
            if not is_ocean_point(lat, lon):
                continue

            eval_res = self.engine.evaluate_cell(pt)
            idx_100 = eval_res["ocean_risk_index_100"]
            dom_hazard = eval_res["dominant_hazard"]

            # Filter if hazard specified
            if hazard_filter and hazard_filter != "all" and dom_hazard != hazard_filter:
                continue

            scores.append(idx_100)
            if idx_100 >= 65.0:
                high_risk_cells += 1

            basin = get_ocean_basin(lat, lon)
            name = pt.get("name", f"{basin} ({lat:.1f}, {lon:.1f})")

            # Create bounding grid polygon (approx 1x1 degree)
            polygon_coords = [[
                [round(lon - 0.7, 4), round(lat - 0.7, 4)],
                [round(lon + 0.7, 4), round(lat - 0.7, 4)],
                [round(lon + 0.7, 4), round(lat + 0.7, 4)],
                [round(lon - 0.7, 4), round(lat + 0.7, 4)],
                [round(lon - 0.7, 4), round(lat - 0.7, 4)]
            ]]

            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": polygon_coords
                },
                "properties": {
                    "region_name": name,
                    "ocean_basin": basin,
                    "latitude": lat,
                    "longitude": lon,
                    "risk_index": idx_100,
                    "severity_category": "Extreme" if idx_100 >= 80 else ("High" if idx_100 >= 60 else ("Moderate" if idx_100 >= 40 else "Low")),
                    "dominant_hazard": dom_hazard,
                    "explanation": eval_res["summary_explanation"],
                    "parameters": {
                        "sst": pt.get("sst"),
                        "sst_anomaly": pt.get("sst_anomaly"),
                        "wind_speed": pt.get("wind_speed"),
                        "chlorophyll": pt.get("chlorophyll"),
                        "dissolved_oxygen": pt.get("dissolved_oxygen"),
                        "ph": pt.get("ph")
                    }
                }
            }
            geojson_features.append(feature)

            top_regions.append({
                "region_name": name,
                "ocean_basin": basin,
                "risk_score": idx_100,
                "dominant_hazard": dom_hazard,
                "latitude": lat,
                "longitude": lon
            })

        top_regions.sort(key=lambda x: x["risk_score"], reverse=True)
        mean_score = round(sum(scores) / max(1, len(scores)), 1) if scores else 0.0
        max_score = round(max(scores), 1) if scores else 0.0

        return {
            "hazard": hazard_filter or "all_composite",
            "time": datetime.utcnow(),
            "mean_risk_score": mean_score,
            "max_risk_score": max_score,
            "high_risk_cells_count": high_risk_cells,
            "geojson": {
                "type": "FeatureCollection",
                "features": geojson_features
            },
            "top_risk_regions": top_regions[:10]
        }
