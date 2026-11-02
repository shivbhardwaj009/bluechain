"""Rule-based Scientific Relationship Engine.
Evaluates oceanographic state against YAML-configured rules to quantify physical and ecological risks.
Outputs risk scores [0.0 - 1.0] and detailed explanation strings.
"""
import os
import yaml
from typing import Dict, Any, List, Optional
from backend.app.core.logging import logger


class RelationshipEngine:
    """Config-driven scientific ocean hazard rule evaluator."""

    def __init__(self, config_path: Optional[str] = None):
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), "rules.yaml")
        self.config_path = config_path
        self.rules = self._load_rules()

    def _load_rules(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.config_path):
            logger.error(f"Rule file not found at {self.config_path}")
            return []
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("rules", [])

    def evaluate_cell(self, cell_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a gridded ocean point against all scientific rules.
        
        Args:
            cell_data: Dictionary of parameters at the cell, e.g.:
                {
                    "sst": 29.8,
                    "sst_anomaly": 2.1,
                    "wind_speed": 3.2,
                    "chlorophyll": 8.5,
                    "dissolved_oxygen": 2.8,
                    "ph": 7.92,
                    "is_cyclone_present": False
                }
        Returns:
            {
                "composite_risk_score": float [0.0 - 1.0],
                "evaluated_rules": [
                    {"rule_id": str, "risk_score": float, "triggered": bool, "explanation": str}
                ],
                "dominant_hazard": str,
                "summary_explanation": str
            }
        """
        evaluated = []
        sst = float(cell_data.get("sst", 20.0))
        sst_anomaly = float(cell_data.get("sst_anomaly", 0.0))
        wind = float(cell_data.get("wind_speed", 7.0))
        chl = float(cell_data.get("chlorophyll", 0.5))
        do = float(cell_data.get("dissolved_oxygen", 6.5))
        ph = float(cell_data.get("ph", 8.1))
        is_cyclone = bool(cell_data.get("is_cyclone_present", False))

        highest_score = 0.0
        dominant_hazard = "baseline_ocean"
        dominant_explanation = "Parameters remain within normal climatological baseline variations."
        total_weighted_risk = 0.0
        total_weight = 0.0

        for r in self.rules:
            rule_id = r["id"]
            cond = r["conditions"]
            scoring = r["scoring"]
            weight = r.get("weight", 0.2)
            triggered = False
            score = 0.0
            explanation = ""

            # 1. Marine Heatwave / Coral Bleaching Rule
            if rule_id == "mhw_coral_bleaching":
                if sst >= cond.get("sst_min", 28.5) and sst_anomaly >= cond.get("sst_anomaly_min", 1.2):
                    triggered = True
                    base = scoring.get("base_risk", 0.4)
                    bonus = scoring.get("low_wind_bonus", 0.2) if wind <= cond.get("wind_speed_max", 5.0) else 0.0
                    anom_contrib = sst_anomaly * scoring.get("sst_anomaly_factor", 0.3)
                    score = min(1.0, base + bonus + anom_contrib)
                    explanation = r["explanation_template"].format(
                        sst=sst, sst_anomaly=sst_anomaly, wind_speed=wind
                    )

            # 2. Harmful Algal Bloom Rule
            elif rule_id == "hab_eutrophication":
                if chl >= cond.get("chlorophyll_min", 4.0) and sst >= cond.get("sst_min", 18.0):
                    triggered = True
                    base = scoring.get("base_risk", 0.45)
                    score = min(1.0, base + (chl - 4.0) * scoring.get("chlorophyll_factor", 0.05))
                    explanation = r["explanation_template"].format(
                        chlorophyll=chl, sst=sst
                    )

            # 3. Deoxygenation Rule
            elif rule_id == "ocean_deoxygenation":
                if do <= cond.get("dissolved_oxygen_max", 3.5) and sst >= cond.get("sst_min", 20.0):
                    triggered = True
                    base = scoring.get("base_risk", 0.50)
                    deficit = max(0.0, 3.5 - do)
                    score = min(1.0, base + deficit * scoring.get("low_oxygen_factor", 0.15))
                    explanation = r["explanation_template"].format(
                        dissolved_oxygen=do, sst=sst
                    )

            # 4. Acidification Rule
            elif rule_id == "ocean_acidification":
                if ph <= cond.get("ph_max", 7.95):
                    triggered = True
                    base = scoring.get("base_risk", 0.40)
                    ph_deficit = max(0.0, 7.95 - ph)
                    score = min(1.0, base + ph_deficit * scoring.get("ph_deficit_factor", 1.5))
                    explanation = r["explanation_template"].format(ph=ph)

            # 5. Cyclone Rapid Intensification Rule
            elif rule_id == "cyclone_rapid_intensification":
                if is_cyclone and sst >= cond.get("sst_min", 27.5):
                    triggered = True
                    base = scoring.get("base_risk", 0.60)
                    sst_excess = max(0.0, sst - 27.5)
                    score = min(1.0, base + sst_excess * scoring.get("sst_excess_factor", 0.15))
                    explanation = r["explanation_template"].format(sst=sst)

            if triggered and score > highest_score:
                highest_score = score
                dominant_hazard = r["hazard_category"]
                dominant_explanation = explanation

            if triggered:
                total_weighted_risk += score * weight
                total_weight += weight

            evaluated.append({
                "rule_id": rule_id,
                "name": r["name"],
                "hazard_category": r["hazard_category"],
                "triggered": triggered,
                "risk_score": round(score, 3),
                "explanation": explanation
            })

        # Calculate composite risk score (0.0 to 1.0)
        composite = max(highest_score, total_weighted_risk / max(0.1, total_weight) if total_weight > 0 else 0.05)
        composite = round(min(1.0, composite), 3)

        return {
            "composite_risk_score": composite,
            "ocean_risk_index_100": round(composite * 100.0, 1),
            "dominant_hazard": dominant_hazard,
            "summary_explanation": dominant_explanation,
            "evaluated_rules": evaluated
        }
