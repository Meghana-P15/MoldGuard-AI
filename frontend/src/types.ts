export type BatchInput = {
  Tinj: number;
  tinj: number;
  Pinj: number;
  Ph: number;
  Bp: number;
  th: number;
  cycles: number;
  part_weight_g?: number;
  material_code?: string;
  machine_id?: string;
  operator_note?: string;
};

export type RiskFactor = {
  feature: string;
  impact: number;
  direction: string;
};

export type DistributionCheck = {
  status: "IN_DISTRIBUTION" | "OUT_OF_DISTRIBUTION" | "UNKNOWN";
  score: number | null;
  note: string;
};

export type MaterialImpact = {
  available: boolean;
  method?: string;
  planned_material_kg?: number;
  risk_equivalent?: number;
  material_at_risk_kg?: number;
  material_at_risk_reduction_kg?: number;
  material_at_risk_reduction_percent?: number;
  before?: MaterialImpact;
  after?: MaterialImpact;
  note?: string;
};

export type PredictResponse = {
  prediction: "G" | "Y" | "R";
  risk_level: string;
  decision: "LOW_RISK" | "REVIEW_REQUIRED" | "HIGH_RISK";
  confidence: number;
  reasons: string[];
  probabilities: Record<"G" | "Y" | "R", number>;
  distribution: DistributionCheck;
  predicted_energy: number;
  energy_interval: {
    low: number;
    high: number;
    validation_mae: number;
  };
  projected_energy: number;
  top_risk_factors: RiskFactor[];
  material_impact: MaterialImpact;
  model_mode: string;
  note: string;
};

export type AgentQuality = {
  prediction: "G" | "Y" | "R";
  risk_level: string;
  decision: string;
  confidence: number;
  reasons: string[];
  probabilities: Record<"G" | "Y" | "R", number>;
  distribution: DistributionCheck;
  top_risk_factors: RiskFactor[];
  model_mode: string;
};

export type OptimizeResponse = {
  current: {
    parameters: Record<string, number>;
    probabilities: Record<"G" | "Y" | "R", number>;
    good_probability: number;
    reject_probability: number;
    energy: number;
    distribution: DistributionCheck;
  };
  recommended_parameters: Record<string, number>;
  optimized: {
    probabilities: Record<"G" | "Y" | "R", number>;
    good_probability: number;
    reject_probability: number;
    energy: number;
  };
  improvement: {
    good_probability_change: number;
    reject_probability_change: number;
    energy_reduction_percent: number;
  };
  projected: {
    cycles: number;
    current_energy: number;
    optimized_energy: number;
    energy_saved: number;
  };
  material_impact: MaterialImpact;
  guardrail: {
    recommendation_available: boolean;
    accepted_candidates: number;
    skipped_out_of_distribution_candidates: number;
    note: string;
  };
  optimizer_note: string;
  model_mode?: string;
};

export type EvidenceItem = {
  source: string;
  section: string;
  snippet: string;
  score: number;
  retrieval_mode: string;
};

export type AnalyzeResponse = {
  run_id: string;
  prediction: PredictResponse;
  optimization: OptimizeResponse;
  evidence: EvidenceItem[];
};

export type AgentTimelineEvent = {
  step: number;
  actor: string;
  status: "DONE" | "BLOCKED" | "REVIEW";
  title: string;
  detail: string;
};

export type AgentRunResponse = {
  run_id: string;
  mode: string;
  agent_session_id?: string | null;
  agent_trace_id?: string | null;
  agent_span_id?: string | null;
  agent_investigation_completed?: boolean | null;
  objective: string;
  decision: string;
  human_review_required: boolean;
  quality: AgentQuality;
  optimization: OptimizeResponse;
  impact: {
    energy_reduction_percent?: number;
    energy_saved?: number;
    material_impact?: MaterialImpact;
  };
  evidence: EvidenceItem[];
  safety: {
    decision: string;
    blocked: boolean;
    human_review_required: boolean;
    reasons: string[];
    rule: string;
  };
  supervisor_summary: string;
  timeline: AgentTimelineEvent[];
};
