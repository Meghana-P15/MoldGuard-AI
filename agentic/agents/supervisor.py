from __future__ import annotations

import json

from strands import Agent
from strands.models.bedrock import BedrockModel

from agentic.config import settings
from agentic.prompts import SUPERVISOR_PROMPT
from agentic.agents.quality_agent import build_quality_agent
from agentic.agents.optimization_agent import build_optimization_agent
from agentic.agents.knowledge_agent import build_knowledge_agent


def build_supervisor() -> Agent:
    model = BedrockModel(
        model_id=settings.bedrock_model_id,
        region_name=settings.aws_region,
        temperature=0.0,
    )

    quality = build_quality_agent(model=model)
    optimization = build_optimization_agent(model=model)
    knowledge = build_knowledge_agent(model=model)

    return Agent(
        name="moldguard_supervisor",
        description="Coordinates MoldGuard quality, optimization and knowledge specialists.",
        model=model,
        system_prompt=SUPERVISOR_PROMPT,
        tools=[
            quality.as_tool(
                name="quality_agent",
                description=(
                    "Specialist for MoldGuard quality risk, confidence, OOD and SHAP. "
                    "Use for every planned batch."
                ),
            ),
            optimization.as_tool(
                name="optimization_agent",
                description=(
                    "Specialist for constrained process optimization, energy and material impact. "
                    "Use after quality analysis for every planned batch."
                ),
            ),
            knowledge.as_tool(
                name="knowledge_agent",
                description=(
                    "Specialist for retrieving SOP/material/process evidence. "
                    "Use for every planned batch before final synthesis."
                ),
            ),
        ],
    )


def _text_from_result(result) -> str:
    try:
        content = result.message.get("content", [])
        texts = [
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("text")
        ]
        return "\n".join(texts).strip()
    except Exception:
        return str(result)


def supervisor_investigation(payload: dict) -> str:
    """Run the real Strands supervisor before deterministic verification.

    The prompt requires all three specialist agents. Their calls exercise the same
    deterministic ML/RAG tools used by the verifier. The final safety decision is
    recomputed independently after this investigation and cannot be overridden.
    """
    supervisor = build_supervisor()
    prompt = (
        "Investigate this planned MoldGuard batch. You MUST delegate to all three "
        "specialists exactly for their domains: quality_agent, optimization_agent, "
        "and knowledge_agent. Do not invent any number, parameter, or source. "
        "After their responses, provide a concise operator-facing synthesis and "
        "explicitly state that the deterministic Safety Gate is authoritative.\n\n"
        + json.dumps(payload, default=str)
    )
    return _text_from_result(supervisor(prompt))
