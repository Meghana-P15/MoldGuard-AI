from __future__ import annotations

from typing import Any, Dict

from ai.moldguard_ai.guardrails import decision_from_prediction
from agentic.runtime import get_bundle


def quality_assessment(params: Dict[str, float]) -> Dict[str, Any]:
    bundle = get_bundle()
    risk = bundle.predict_risk(params)
    distribution = bundle.distribution_check(params)
    decision = decision_from_prediction(
        risk["probabilities"],
        distribution["status"],
    )
    return {
        **risk,
        **decision,
        "distribution": distribution,
        "model_mode": bundle.model_mode,
    }
