from __future__ import annotations

from typing import Any

from agentic.knowledge import get_knowledge_index


def retrieve_process_evidence(
    material_code: str | None,
    prediction: str,
    decision: str,
    top_features: list[str],
    k: int = 3,
) -> list[dict[str, Any]]:
    query = (
        f"Injection molding process guidance for material "
        f"{material_code or 'unknown'}; predicted class {prediction}; "
        f"decision {decision}; main risk drivers {', '.join(top_features)}. "
        f"Find validated guidance the operator should verify before changing settings."
    )
    return get_knowledge_index().search(query, k=k)
