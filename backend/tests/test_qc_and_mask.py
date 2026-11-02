import pytest
from backend.app.oipe.data_collection.ocean_mask import is_ocean_point, get_ocean_basin
from backend.app.oipe.data_collection.qc_validator import QCValidator


def test_ocean_mask_strictly_marine():
    # Continental land points must be rejected
    assert is_ocean_point(39.0, -98.0) is False   # Kansas, North America
    assert is_ocean_point(25.0, 15.0) is False    # Sahara Desert, Africa
    assert is_ocean_point(48.85, 2.35) is False   # Paris, Europe
    assert is_ocean_point(-25.0, 134.0) is False  # Central Australia
    assert is_ocean_point(-15.0, -55.0) is False  # Amazon Interior, South America

    # Oceanic marine points must be accepted
    assert is_ocean_point(0.0, -140.0) is True    # Central Pacific Ocean
    assert is_ocean_point(25.0, -45.0) is True    # North Atlantic Gyre
    assert is_ocean_point(-10.0, 75.0) is True    # Indian Ocean
    assert is_ocean_point(-65.0, 0.0) is True     # Southern Ocean
    assert is_ocean_point(85.0, 0.0) is True      # Arctic Ocean


def test_ocean_basin_classifier():
    assert get_ocean_basin(85.0, 10.0) == "Arctic Ocean"
    assert get_ocean_basin(-65.0, 10.0) == "Southern Ocean"
    assert get_ocean_basin(20.0, -40.0) == "Atlantic Ocean"
    assert get_ocean_basin(0.0, 80.0) == "Indian Ocean"
    assert get_ocean_basin(0.0, 160.0) == "Pacific Ocean"


def test_qc_validator_physical_bounds():
    # Valid SST record in Pacific Ocean
    valid_rec = {
        "parameter": "sst",
        "value": 28.5,
        "unit": "degC",
        "latitude": 0.0,
        "longitude": -140.0
    }
    is_valid, qc_flag, reason, norm_rec = QCValidator.validate_record(valid_rec)
    assert is_valid is True
    assert qc_flag == 1
    assert norm_rec["value"] == 28.5
    assert norm_rec["unit"] == "degC"

    # Extreme implausible SST (> 36 degC) must be rejected
    hot_rec = {
        "parameter": "sst",
        "value": 48.0,
        "unit": "degC",
        "latitude": 0.0,
        "longitude": -140.0
    }
    is_valid, qc_flag, reason, _ = QCValidator.validate_record(hot_rec)
    assert is_valid is False
    assert qc_flag == 3
    assert "outside physical bounds" in reason


def test_qc_validator_unit_normalization():
    # Kelvin conversion to Celsius
    kelvin_rec = {
        "parameter": "sst",
        "value": 301.15,
        "unit": "Kelvin",
        "latitude": 10.0,
        "longitude": -40.0
    }
    is_valid, qc_flag, _, norm_rec = QCValidator.validate_record(kelvin_rec)
    assert is_valid is True
    assert abs(norm_rec["value"] - 28.0) < 0.01
    assert norm_rec["unit"] == "degC"


def test_qc_validator_rejects_terrestrial_records():
    # Observation on land (Kansas) must be rejected
    land_rec = {
        "parameter": "sst",
        "value": 22.0,
        "unit": "degC",
        "latitude": 39.0,
        "longitude": -98.0
    }
    is_valid, qc_flag, reason, _ = QCValidator.validate_record(land_rec)
    assert is_valid is False
    assert qc_flag == 3
    assert "Strictly marine scope enforced" in reason
