from __future__ import annotations

import uuid
from typing import Any, Dict

from agentic.schemas import AgentRequest
from agentic.tools.quality_tools import quality_assessment
from agentic.tools.optimization_tools import optimization_assessment
from agentic.tools.knowledge_tools import retrieve_process_evidence
from agentic.tools.safety_tools import deterministic_safety_gate


def _timeline(
    quality: Dict[str, Any],
    optimization: Dict[str, Any],
    evidence: list[dict],
    safety: Dict[str, Any],
) -> list[dict]:
    return [
        {
            "step": 1,
            "actor": "Supervisor Agent",
            "status": "DONE",
            "title": "Production objective parsed",
            "detail": "Delegated risk, optimization and evidence checks.",
        },
        {
            "step": 2,
            "actor": "Quality Agent",
            "status": "DONE",
            "title": f"Batch classified as {quality['prediction']}",
            "detail": (
                f"Confidence {quality['confidence']:.0%}; "
                f"{quality['distribution']['status'].replace('_', ' ').lower()}."
            ),
        },
        {
            "step": 3,
            "actor": "Optimization Agent",
            "status": (
                "DONE"
                if optimization["guardrail"]["recommendation_available"]
                else "REVIEW"
            ),
            "title": "Constrained search completed",
            "detail": (
                f"Evaluated {optimization['guardrail']['accepted_candidates']} "
                f"in-distribution candidates and blocked "
                f"{optimization['guardrail']['skipped_out_of_distribution_candidates']} "
                f"OOD candidates."
            ),
        },
        {
            "step": 4,
            "actor": "Knowledge Agent",
            "status": "DONE" if evidence else "REVIEW",
            "title": "Process evidence retrieved",
            "detail": f"Retrieved {len(evidence)} relevant process-guidance passages.",
        },
        {
            "step": 5,
            "actor": "Safety Gate",
            "status": "BLOCKED" if safety["blocked"] else "REVIEW",
            "title": safety["decision"].replace("_", " ").title(),
            "detail": safety["reasons"][0],
        },
    ]


def run_local_agentic_analysis(request: AgentRequest) -> Dict[str, Any]:
    params = request.batch.model_params()

    quality = quality_assessment(params)
    optimization = optimization_assessment(
        params,
        request.batch.cycles,
        request.batch.part_weight_g,
    )

    top = [x["feature"] for x in quality.get("top_risk_factors", [])]
    evidence = retrieve_process_evidence(
        request.batch.material_code,
        quality["prediction"],
        quality["decision"],
        top,
        k=3,
    )

    safety = deterministic_safety_gate(quality, optimization)

    material = optimization.get("material_impact", {})
    energy_reduction = optimization.get("improvement", {}).get(
        "energy_reduction_percent",
        0.0,
    )

    if safety["blocked"]:
        summary = (
            "MoldGuard blocked an automatic recommendation and requires human review. "
            f"The predicted class is {quality['prediction']} with "
            f"{quality['confidence']:.0%} model confidence."
        )
    else:
        summary = (
            f"MoldGuard completed the batch investigation. "
            f"The predicted class is {quality['prediction']} with "
            f"{quality['confidence']:.0%} confidence. "
            f"The constrained optimizer estimates {energy_reduction:.1f}% energy "
            f"reduction for its recommended configuration. "
            "A qualified process engineer must review the recommendation before use."
        )

    return {
        "run_id": str(uuid.uuid4()),
        "mode": "local-deterministic-orchestrator",
        "objective": request.objective,
        "decision": safety["decision"],
        "human_review_required": True,
        "quality": quality,
        "optimization": optimization,
        "impact": {
            "energy_reduction_percent": energy_reduction,
            "energy_saved": optimization.get("projected", {}).get("energy_saved"),
            "material_impact": material,
        },
        "evidence": evidence,
        "safety": safety,
        "supervisor_summary": summary,
        "timeline": _timeline(quality, optimization, evidence, safety),
    }
