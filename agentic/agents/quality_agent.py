from __future__ import annotations

import json
from strands import Agent, tool

from agentic.prompts import QUALITY_PROMPT
from agentic.tools.quality_tools import quality_assessment


@tool
def assess_batch_quality(
    Tinj: float,
    tinj: float,
    Pinj: float,
    Ph: float,
    Bp: float,
    th: float,
) -> str:
    """Run MoldGuard quality ML, SHAP, confidence and OOD checks."""
    result = quality_assessment(
        {
            "Tinj": Tinj,
            "tinj": tinj,
            "Pinj": Pinj,
            "Ph": Ph,
            "Bp": Bp,
            "th": th,
        }
    )
    return json.dumps(result)


def build_quality_agent(model=None) -> Agent:
    kwargs = {
        "name": "quality_guardian",
        "system_prompt": QUALITY_PROMPT,
        "tools": [assess_batch_quality],
    }
    if model is not None:
        kwargs["model"] = model
    return Agent(**kwargs)
