from backend.app.oipe.relationship_engine.engine import RelationshipEngine


def test_relationship_engine_rules():
    engine = RelationshipEngine()
    assert len(engine.rules) >= 5

    # 1. Marine heatwave + coral bleaching risk trigger
    cell_mhw = {
        "sst": 30.5,
        "sst_anomaly": 2.2,
        "wind_speed": 2.5,
        "chlorophyll": 0.3,
        "dissolved_oxygen": 6.2,
        "ph": 8.05
    }
    res = engine.evaluate_cell(cell_mhw)
    assert res["composite_risk_score"] >= 0.70
    assert res["dominant_hazard"] == "marine_heatwave"
    assert "thermal stratification" in res["summary_explanation"].lower()

    # 2. Acidification risk trigger
    cell_acid = {
        "sst": 22.0,
        "sst_anomaly": 0.2,
        "wind_speed": 8.0,
        "chlorophyll": 0.5,
        "dissolved_oxygen": 6.5,
        "ph": 7.82  # Low pH
    }
    res_acid = engine.evaluate_cell(cell_acid)
    assert res_acid["dominant_hazard"] == "acidification"
    assert "acidification stress" in res_acid["summary_explanation"].lower()
