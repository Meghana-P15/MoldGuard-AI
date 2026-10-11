from __future__ import annotations

from ai.moldguard_ai.optimizer import optimize_settings
from backend.app.schemas import BatchInput
from backend.app.services.knowledge_service import KnowledgeService
from backend.app.services.model_service import ModelService
from backend.app.services.monitoring_service import MonitoringService


class OrchestrationService:
    @classmethod
    def analyze(cls, batch: BatchInput) -> dict:
        ModelService.validate_context(batch.machine, batch.material)
        bundle = ModelService.bundle()
        params = batch.model_params()

        risk = bundle.predict_risk(params)
        ood = bundle.predict_ood(params)
        energy = bundle.predict_energy(params, batch.material)
        optimization = optimize_settings(bundle, params, batch.material, n_candidates=1800)

        current_defect = float(risk["predicted_defect_rate"])
        optimized_defect = float(optimization["optimized"]["predicted_defect_rate"])
        total_material_kg = batch.part_weight_g * batch.cycles / 1000.0
        current_material_at_risk = total_material_kg * current_defect
        optimized_material_at_risk = total_material_kg * optimized_defect

        current_batch_energy = energy["kwh_per_cycle"] * batch.cycles
        optimized_batch_energy = (
            float(optimization["optimized"]["energy_kwh_per_cycle"]) * batch.cycles
        )
        energy_saved = current_batch_energy - optimized_batch_energy

        if not ood["in_distribution"]:
            decision = "REVIEW_REQUIRED"
        elif risk["prediction"] == "R":
            decision = "HIGH_RISK"
        elif risk["prediction"] == "Y":
            decision = "WARNING"
        else:
            decision = "GOOD"

        changes = []
        for key, new_value in optimization["recommended_parameters"].items():
            old = params[key]
            if abs(float(new_value) - float(old)) > 1e-9:
                changes.append(f"{key} {old:.2f} to {float(new_value):.2f}")
        driver_names = ", ".join(x["feature"] for x in risk["top_risk_factors"])
        query = (
            f"Injection molding process guidance for predicted defect rate {risk['predicted_defect_percent']:.2f}%. "
            f"Risk drivers: {driver_names}. Recommended changes: {', '.join(changes)}. "
            "Use holding pressure, mold temperature, cycle time, energy and human-review guidance."
        )
        evidence = KnowledgeService.retrieve(query, top_k=3)

        response = {
            "batch_decision": decision,
            "prediction": risk["prediction"],
            "risk_level": risk["risk_level"],
            "predicted_defect_rate": round(current_defect, 6),
            "predicted_defect_percent": round(float(risk["predicted_defect_percent"]), 4),
            "defect_uncertainty_percentage_points": round(
                float(risk["uncertainty_percentage_points"]), 4
            ),
            "defect_rate_range": [round(float(v), 6) for v in risk["range_defect_rate"]],
            "model_reliability_estimate": round(float(risk["model_reliability_estimate"]), 6),
            "risk_thresholds": {k: float(v) for k, v in risk["thresholds"].items()},
            "data_familiarity": {
                "label": ood["label"],
                "in_distribution": ood["in_distribution"],
                "score": round(float(ood["familiarity_score"]), 6),
                "raw_ood_score": round(float(ood["ood_score"]), 6),
            },
            "top_risk_factors": risk["top_risk_factors"],
            "energy": {
                "predicted_power_watts": round(float(energy["predicted_power_watts"]), 3),
                "kwh_per_cycle": round(float(energy["kwh_per_cycle"]), 8),
                "uncertainty_kwh_per_cycle": round(float(energy["uncertainty_kwh"]), 8),
                "range_kwh_per_cycle": [
                    round(float(energy["lower_kwh_per_cycle"]), 8),
                    round(float(energy["upper_kwh_per_cycle"]), 8),
                ],
                "current_batch_kwh": round(float(current_batch_energy), 5),
                "optimized_batch_kwh": round(float(optimized_batch_energy), 5),
            },
            "recommended_parameters": optimization["recommended_parameters"],
            "optimization": optimization,
            "impact": {
                "energy_reduction_kwh": round(float(energy_saved), 5),
                "energy_reduction_percent": round(
                    float((energy_saved / max(current_batch_energy, 1e-12)) * 100.0), 3
                ),
                "defect_rate_change_percentage_points": round(
                    float((optimized_defect - current_defect) * 100.0), 4
                ),
                "material_at_risk_current_kg": round(float(current_material_at_risk), 3),
                "material_at_risk_optimized_kg": round(float(optimized_material_at_risk), 3),
                "material_at_risk_reduction_kg": round(
                    float(current_material_at_risk - optimized_material_at_risk), 3
                ),
            },
            "evidence": evidence,
            "rag_backend": KnowledgeService.backend_name(),
            "human_review_note": (
                "Decision support only. A factory/process engineer must validate recommended settings "
                "against the machine, material datasheet and site SOP before use. MoldGuard AI never "
                "writes directly to machine controls."
            ),
            "model_mode": bundle.model_mode,
            "data_sources": bundle.metadata.get("raw_datasets", []),
        }

        MonitoringService.log(
            "analysis_completed",
            decision=decision,
            risk_band=risk["prediction"],
            predicted_defect_percent=round(risk["predicted_defect_percent"], 4),
            ood=not ood["in_distribution"],
            rag_backend=response["rag_backend"],
        )
        MonitoringService.metric("AnalysisCount", 1, Decision=decision)
        if not ood["in_distribution"]:
            MonitoringService.metric("OODCount", 1)
        if decision == "REVIEW_REQUIRED":
            MonitoringService.metric("ReviewRequiredCount", 1)
        if decision == "HIGH_RISK":
            MonitoringService.metric("HighRiskCount", 1)
        MonitoringService.metric(
            "PredictedDefectPercent", float(risk["predicted_defect_percent"]), unit="Percent"
        )
        return response
