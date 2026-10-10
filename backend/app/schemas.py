from typing import Dict, List, Literal
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
        data.pop("cycles", None)
        return {k: float(v) for k, v in data.items()}


class RiskFactor(BaseModel):
    feature: str
    impact: float
    direction: str


class PredictResponse(BaseModel):
    prediction: str
    risk_level: str
    probabilities: Dict[str, float]
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
    optimizer_note: str
    model_mode: str
