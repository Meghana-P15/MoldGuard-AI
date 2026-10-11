from __future__ import annotations

from typing import Any, Dict, List, Literal
from pydantic import BaseModel, Field, model_validator

from ai.moldguard_ai.config import PARAM_BOUNDS


class AgentBatch(BaseModel):
    Tinj: float
    tinj: float
    Pinj: float
    Ph: float
    Bp: float
    th: float

    cycles: int = Field(default=1000, ge=1, le=10_000_000)
    part_weight_g: float | None = Field(default=None, gt=0, le=100_000)
    machine_id: str | None = Field(default=None, max_length=80)
    material_code: str | None = Field(default=None, max_length=80)
    operator_note: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def check_ranges(self):
        values = self.model_dump()
        errors = []
        for key, (lo, hi) in PARAM_BOUNDS.items():
            value = float(values[key])
            if not lo <= value <= hi:
                errors.append(f"{key} must be between {lo} and {hi}")
        if errors:
            raise ValueError("; ".join(errors))
        return self

    def model_params(self) -> Dict[str, float]:
        return {k: float(getattr(self, k)) for k in PARAM_BOUNDS}


class AgentRequest(BaseModel):
    objective: str = Field(
        default=(
            "Evaluate this planned injection-molding batch and recommend "
            "lower-waste, lower-energy settings only when justified."
        ),
        min_length=5,
        max_length=1000,
    )
    batch: AgentBatch


class TimelineEvent(BaseModel):
    step: int
    actor: str
    status: Literal["DONE", "BLOCKED", "REVIEW"]
    title: str
    detail: str


class AgentResponse(BaseModel):
    run_id: str
    mode: str
    agent_session_id: str | None = None
    agent_trace_id: str | None = None
    agent_span_id: str | None = None
    agent_investigation_completed: bool | None = None
    objective: str
    decision: str
    human_review_required: bool

    quality: Dict[str, Any]
    optimization: Dict[str, Any]
    impact: Dict[str, Any]
    evidence: List[Dict[str, Any]]
    safety: Dict[str, Any]

    supervisor_summary: str
    timeline: List[TimelineEvent]
