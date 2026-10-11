from __future__ import annotations

from typing import Dict, List, Literal

from pydantic import BaseModel, Field, model_validator

from ai.moldguard_ai.config import PARAM_BOUNDS


class BatchInput(BaseModel):
    machine: str = Field("I-10", min_length=1, max_length=100)
    material: str = Field("A-PROD", min_length=1, max_length=100)
    Tinj: float = Field(..., description="Melt temperature (°C)")
    tinj: float = Field(..., description="Cycle time (s)")
    Pinj: float = Field(..., description="Injection pressure (bar)")
    Ph: float = Field(..., description="Holding pressure (bar)")
    Tmold: float = Field(..., description="Mold temperature (°C)")
    th: float = Field(..., description="Holding time (s)")
    cycles: int = Field(1000, ge=1, le=10_000_000)
    part_weight_g: float = Field(100.0, gt=0, le=5000)

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
        return {
            key: float(getattr(self, key))
            for key in ["Tinj", "tinj", "Pinj", "Ph", "Tmold", "th"]
        }


class RiskFactor(BaseModel):
    feature: str
    impact: float
    direction: str


class EvidenceItem(BaseModel):
    source: str
    excerpt: str
    score: float
    retrieval_backend: str | None = None


class AnalyzeResponse(BaseModel):
    batch_decision: Literal["GOOD", "WARNING", "HIGH_RISK", "REVIEW_REQUIRED"]
    prediction: Literal["G", "Y", "R"]
    risk_level: str
    predicted_defect_rate: float
    predicted_defect_percent: float
    defect_uncertainty_percentage_points: float
    defect_rate_range: List[float]
    model_reliability_estimate: float
    risk_thresholds: Dict[str, float]
    data_familiarity: dict
    top_risk_factors: List[RiskFactor]
    energy: dict
    recommended_parameters: Dict[str, float]
    optimization: dict
    impact: dict
    evidence: List[EvidenceItem]
    rag_backend: str
    human_review_note: str
    model_mode: str
    data_sources: List[str]


class PredictResponse(BaseModel):
    prediction: str
    risk_level: str
    predicted_defect_rate: float
    predicted_defect_percent: float
    defect_uncertainty_percentage_points: float
    predicted_energy: float
    top_risk_factors: List[RiskFactor]
    projected_energy: float
    model_mode: str
    note: str


class OptimizeResponse(BaseModel):
    current: dict
    recommended_parameters: dict
    optimized: dict
    improvement: dict
    projected: dict
    candidate_search: dict
    optimizer_note: str
    model_mode: str
