"""Marine Heatwave (MHW) Event Detection Engine.
Implements the peer-reviewed Hobday et al. (2016, 2018) quantitative framework:
- Anomaly must exceed the 90th percentile threshold relative to local seasonal climatology.
- Duration must be >= 5 consecutive days.
- Severity Categorization based on multiples of local threshold difference (ΔT):
  * Category I (Moderate): 1x to 2x ΔT
  * Category II (Strong): 2x to 3x ΔT
  * Category III (Severe): 3x to 4x ΔT
  * Category IV (Extreme): >= 4x ΔT
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from backend.app.oipe.data_collection.ocean_mask import get_ocean_basin


class MarineHeatwaveDetector:
    """Detects and categorizes Marine Heatwaves using the Hobday criteria."""

    @staticmethod
    def classify_severity(anomaly: float, threshold_diff: float) -> str:
        """Categorize MHW severity according to Hobday et al. (2018)."""
        if threshold_diff <= 0:
            threshold_diff = 1.0  # safe fallback

        multiple = anomaly / threshold_diff
        if multiple >= 4.0:
            return "Extreme"
        elif multiple >= 3.0:
            return "Severe"
        elif multiple >= 2.0:
            return "Strong"
        elif multiple >= 1.0:
            return "Moderate"
        return "Sub-threshold"

    @classmethod
    def detect_mhw_from_timeseries(
        cls,
        region_name: str,
        lat: float,
        lon: float,
        timeseries: List[Dict[str, Any]],
        climatology_90th: float,
        climatology_mean: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """Evaluate a time series for Hobday MHW events.
        
        Args:
            region_name: Descriptive marine location
            lat: Latitude
            lon: Longitude
            timeseries: Sorted list of daily observations [{"time": dt, "sst": val, "anomaly": diff}, ...]
            climatology_90th: 90th percentile temperature threshold
            climatology_mean: Seasonal mean temperature
        """
        if climatology_mean is None:
            climatology_mean = climatology_90th - 1.2
        threshold_diff = max(0.5, climatology_90th - climatology_mean)

        # Count consecutive days above 90th percentile
        consecutive_days = 0
        max_anomaly = 0.0
        start_time = None
        end_time = None

        for entry in timeseries:
            sst = entry.get("sst", 0.0)
            t = entry.get("time")
            if isinstance(t, str):
                t = datetime.fromisoformat(t.replace("Z", "+00:00"))

            if sst >= climatology_90th:
                if consecutive_days == 0:
                    start_time = t
                consecutive_days += 1
                end_time = t
                anomaly = entry.get("anomaly", sst - climatology_mean)
                if anomaly > max_anomaly:
                    max_anomaly = anomaly
            else:
                if consecutive_days < 5:
                    consecutive_days = 0
                    start_time = None

        # Hobday criteria: minimum duration of 5 days
        if consecutive_days >= 5 and start_time and end_time:
            severity = cls.classify_severity(max_anomaly, threshold_diff)
            score_map = {"Moderate": 0.55, "Strong": 0.75, "Severe": 0.90, "Extreme": 1.0}
            severity_score = score_map.get(severity, 0.5)

            basin = get_ocean_basin(lat, lon)
            explanation = (
                f"Hobday et al. Marine Heatwave detected: SST exceeded 90th percentile climatology "
                f"({climatology_90th:.1f}°C) for {consecutive_days} consecutive days (peak anomaly +{max_anomaly:.2f}°C). "
                f"Classified as Category {severity} MHW with elevated coral bleaching and marine mortality risk."
            )

            # Generate GeoJSON bounding circle / polygon around hotspot
            geojson_geom = {
                "type": "Polygon",
                "coordinates": [[
                    [round(lon - 1.5, 4), round(lat - 1.5, 4)],
                    [round(lon + 1.5, 4), round(lat - 1.5, 4)],
                    [round(lon + 1.5, 4), round(lat + 1.5, 4)],
                    [round(lon - 1.5, 4), round(lat + 1.5, 4)],
                    [round(lon - 1.5, 4), round(lat - 1.5, 4)]
                ]]
            }

            return {
                "event_id": f"mhw_{region_name.lower().replace(' ', '_').replace('/', '_')}_{start_time.strftime('%Y%m%d')}",
                "type": "marine_heatwave",
                "title": f"Marine Heatwave: {region_name} (Category {severity})",
                "severity": severity,
                "severity_score": severity_score,
                "start_time": start_time,
                "end_time": end_time,
                "latitude": lat,
                "longitude": lon,
                "ocean_basin": basin,
                "explanation": explanation,
                "geojson_geometry": geojson_geom,
                "metadata_json": {
                    "duration_days": consecutive_days,
                    "max_anomaly_degc": round(max_anomaly, 2),
                    "climatology_90th_degc": climatology_90th,
                    "threshold_diff": round(threshold_diff, 2),
                    "scientific_reference": "Hobday et al. (2016, 2018) Progress in Oceanography"
                }
            }

        return None
