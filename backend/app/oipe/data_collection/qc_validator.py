"""Quality Control (QC) & Ocean Parameter Normalization Validator.
Validates marine observations against physical oceanographic bounds, normalizes units,
verifies marine-only spatial scope, and flags/rejects invalid or terrestrial data.
"""
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
from backend.app.core.logging import logger
from backend.app.oipe.data_collection.ocean_mask import is_ocean_point


# Physically plausible oceanographic bounds
PARAM_PHYSICAL_BOUNDS: Dict[str, Dict[str, Any]] = {
    "sst": {
        "min": -2.5,
        "max": 36.0,
        "standard_unit": "degC",
        "description": "Sea Surface Temperature"
    },
    "salinity": {
        "min": 0.0,
        "max": 45.0,
        "standard_unit": "PSU",
        "description": "Practical Salinity Unit"
    },
    "chlorophyll": {
        "min": 0.001,
        "max": 80.0,
        "standard_unit": "mg/m3",
        "description": "Chlorophyll-a mass concentration"
    },
    "dissolved_oxygen": {
        "min": 0.0,
        "max": 18.0,
        "standard_unit": "mg/L",
        "description": "Dissolved Oxygen concentration"
    },
    "ph": {
        "min": 6.8,
        "max": 8.6,
        "standard_unit": "pH",
        "description": "Ocean surface water pH"
    },
    "wave_height": {
        "min": 0.0,
        "max": 32.0,
        "standard_unit": "m",
        "description": "Significant wave height"
    },
    "wind_speed": {
        "min": 0.0,
        "max": 85.0,
        "standard_unit": "m/s",
        "description": "Surface 10m wind speed"
    },
    "sea_ice_concentration": {
        "min": 0.0,
        "max": 100.0,
        "standard_unit": "%",
        "description": "Fractional sea ice cover"
    }
}


class QCValidator:
    """Rigorous Quality Control engine for oceanographic data."""

    @staticmethod
    def normalize_units(parameter: str, value: float, unit: str) -> Tuple[float, str]:
        """Normalize units to standard SI / oceanographic units."""
        param_lower = parameter.lower()
        unit_lower = unit.lower().strip()

        # Temperature: Kelvin to Celsius
        if param_lower in ("sst", "subsurface_temp", "temperature"):
            if "k" in unit_lower or value > 200.0:
                value = value - 273.15
                unit = "degC"
            elif "f" in unit_lower:
                value = (value - 32.0) * (5.0 / 9.0)
                unit = "degC"
            else:
                unit = "degC"

        # Wind / Current speed: knots or km/h to m/s
        elif "wind" in param_lower or "current" in param_lower:
            if "kt" in unit_lower or "knot" in unit_lower:
                value = value * 0.514444
                unit = "m/s"
            elif "km/h" in unit_lower or "kph" in unit_lower:
                value = value / 3.6
                unit = "m/s"

        # Chlorophyll: ug/L is identical to mg/m3
        elif "chlorophyll" in param_lower:
            unit = "mg/m3"

        return round(value, 4), unit

    @classmethod
    def validate_record(cls, record: Dict[str, Any]) -> Tuple[bool, int, Optional[str], Dict[str, Any]]:
        """Validate an oceanographic observation record.
        
        Returns:
            (is_valid, qc_flag, rejection_reason, normalized_record)
            qc_flag: 1 = Good, 2 = Suspect, 3 = Rejected
        """
        # 1. Coordinate check
        lat = record.get("latitude")
        lon = record.get("longitude")

        if lat is None or lon is None:
            return False, 3, "Missing latitude or longitude coordinates", record

        try:
            lat = float(lat)
            lon = float(lon)
        except (ValueError, TypeError):
            return False, 3, "Non-numeric coordinates provided", record

        if lat < -90.0 or lat > 90.0 or lon < -180.0 or lon > 180.0:
            return False, 3, f"Coordinates out of bounds: lat={lat}, lon={lon}", record

        # 2. Strict Marine-Only Check (Reject land / inland water)
        if not is_ocean_point(lat, lon):
            logger.warning(f"REJECTED non-marine point at lat={lat}, lon={lon} (Land/Inland water excluded)")
            return False, 3, "Point located on continental land or inland waters. Strictly marine scope enforced.", record

        # 3. Parameter and value check
        raw_param = record.get("parameter", "").lower()
        raw_val = record.get("value")
        raw_unit = record.get("unit", "")

        if raw_val is None:
            return False, 3, "Missing measurement value", record

        try:
            val = float(raw_val)
        except (ValueError, TypeError):
            return False, 3, f"Non-numeric value: {raw_val}", record

        # 4. Unit normalization
        norm_val, norm_unit = cls.normalize_units(raw_param, val, raw_unit)
        record["value"] = norm_val
        record["unit"] = norm_unit
        record["latitude"] = lat
        record["longitude"] = lon

        # 5. Physical bounds check
        bounds = PARAM_PHYSICAL_BOUNDS.get(raw_param)
        qc_flag = 1
        if bounds:
            if norm_val < bounds["min"] or norm_val > bounds["max"]:
                msg = f"Value {norm_val} {norm_unit} outside physical bounds [{bounds['min']}, {bounds['max']}] for {raw_param}"
                logger.warning(f"QC REJECTION: {msg}")
                return False, 3, msg, record

        # Passed all QC checks
        record["qc_flag"] = qc_flag
        return True, qc_flag, None, record
