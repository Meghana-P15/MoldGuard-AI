from __future__ import annotations

import json
from strands import Agent, tool

from agentic.prompts import OPTIMIZATION_PROMPT
from agentic.tools.optimization_tools import optimization_assessment


@tool
def optimize_batch_settings(
    Tinj: float,
    tinj: float,
    Pinj: float,
    Ph: float,
    Bp: float,
    th: float,
    cycles: int,
    part_weight_g: float | None = None,
) -> str:
    """Run constrained MoldGuard optimization and environmental impact analysis."""
    result = optimization_assessment(
        {
            "Tinj": Tinj,
            "tinj": tinj,
            "Pinj": Pinj,
            "Ph": Ph,
            "Bp": Bp,
            "th": th,
        },
        cycles,
        part_weight_g,
    )
    return json.dumps(result)


def build_optimization_agent(model=None) -> Agent:
    kwargs = {
        "name": "optimization_specialist",
        "system_prompt": OPTIMIZATION_PROMPT,
        "tools": [optimize_batch_settings],
    }
    if model is not None:
        kwargs["model"] = model
    return Agent(**kwargs)
