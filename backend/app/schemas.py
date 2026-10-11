from typing import Dict, List
from pydantic import BaseModel, Field, model_validator

from ai.moldguard_ai.config import PARAM_BOUNDS


class BatchInput(BaseModel):
    Tinj: float = Field(..., description="Injection/melt temperature")
    tinj: float = Field(..., description="Injection time")
    Pinj: float = Field(..., description="Injection pressure")
    Ph: float = Field(..., description="Holding pressure")
    Bp: float = Field(..., description="Back pressure")
    th: float = Field(..., description="Holding time")

    cycles: int = Field(1000, ge=1, le=10_000_000)
    part_weight_g: float | None = Field(default=None, gt=0, le=100_000)

    machine_id: str | None = Field(default=None, max_length=80)
    material_code: str | None = Field(default=None, max_length=80)
    operator_note: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_process_bounds(self):
        values = self.model_dump()
        errors = []
        for key, (lo, hi) in PARAM_BOUNDS.items():
            value = float(values[key])
            if value < lo or value > hi:
                errors.append(f"{key} must be between {lo} and {hi}")
        if errors:
            raise ValueError("; ".join(errors))
        return self

    def model_params(self) -> Dict[str, float]:
        data = self.model_dump()
        keep = {k: data[k] for k in PARAM_BOUNDS}
        return {k: float(v) for k, v in keep.items()}


class RiskFactor(BaseModel):
    feature: str
    impact: float
    direction: str


class PredictResponse(BaseModel):
    prediction: str
    risk_level: str
    decision: str
    confidence: float
    reasons: List[str]
    probabilities: Dict[str, float]
    distribution: dict
    predicted_energy: float
    energy_interval: dict
    top_risk_factors: List[RiskFactor]
    projected_energy: float
    material_impact: dict
    model_mode: str
    note: str


class OptimizeResponse(BaseModel):
    current: dict
    recommended_parameters: dict
    optimized: dict
    improvement: dict
    projected: dict
    material_impact: dict
    guardrail: dict
    optimizer_note: str
    model_mode: str


class AnalyzeResponse(BaseModel):
    run_id: str
    prediction: PredictResponse
    optimization: OptimizeResponse
    evidence: list[dict]



class AgentRunRequest(BaseModel):
    objective: str = Field(
        default=(
            "Evaluate this planned injection-molding batch and recommend "
            "lower-waste, lower-energy settings only when justified."
        ),
        min_length=5,
        max_length=1000,
    )
    batch: BatchInput


class AgentRunResponse(BaseModel):
    run_id: str
    mode: str
    agent_session_id: str | None = None
    agent_trace_id: str | None = None
    agent_span_id: str | None = None
    agent_investigation_completed: bool | None = None
    objective: str
    decision: str
    human_review_required: bool
    quality: dict
    optimization: dict
    impact: dict
    evidence: list[dict]
    safety: dict
    supervisor_summary: str
    timeline: list[dict]
