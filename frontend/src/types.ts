export type ProcessKey = "Tinj" | "tinj" | "Pinj" | "Ph" | "Tmold" | "th";

export type BatchInput = {
  machine: string;
  material: string;
  Tinj: number;
  tinj: number;
  Pinj: number;
  Ph: number;
  Tmold: number;
  th: number;
  cycles: number;
  part_weight_g: number;
};

export type MetaResponse = {
  machines: string[];
  materials: string[];
  part_weight: { median_g?: number; min_g?: number; max_g?: number };
  defaults: Partial<Record<ProcessKey, number>>;
  parameter_bounds: Record<ProcessKey, [number, number]>;
  feature_labels: Record<ProcessKey, string>;
  feature_units: Record<ProcessKey, string>;
  datasets: string[];
  energy_machine_names: string[];
  risk_model_type: string;
  risk_thresholds: { good_max: number; warning_max: number };
  defect_model_metrics: { mae_percentage_points: number; r2: number };
  energy_model_metrics: { mae_watts: number; r2: number };
  rag_backend: string;
  model_mode: string;
};

export type RiskFactor = {
  feature: string;
  impact: number;
  direction: string;
};

export type EvidenceItem = {
  source: string;
  excerpt: string;
  score: number;
  retrieval_backend?: string;
};

export type AnalyzeResponse = {
  batch_decision: "GOOD" | "WARNING" | "HIGH_RISK" | "REVIEW_REQUIRED";
  prediction: "G" | "Y" | "R";
  risk_level: string;
  predicted_defect_rate: number;
  predicted_defect_percent: number;
  defect_uncertainty_percentage_points: number;
  defect_rate_range: [number, number];
  model_reliability_estimate: number;
  risk_thresholds: { good_max: number; warning_max: number };
  data_familiarity: {
    label: string;
    in_distribution: boolean;
    score: number;
    raw_ood_score: number;
  };
  top_risk_factors: RiskFactor[];
  energy: {
    predicted_power_watts: number;
    kwh_per_cycle: number;
    uncertainty_kwh_per_cycle: number;
    range_kwh_per_cycle: [number, number];
    current_batch_kwh: number;
    optimized_batch_kwh: number;
  };
  recommended_parameters: Record<ProcessKey, number>;
  optimization: {
    current: { parameters: Record<ProcessKey, number>; predicted_defect_rate: number; predicted_defect_percent: number; energy_kwh_per_cycle: number };
    optimized: { predicted_defect_rate: number; predicted_defect_percent: number; energy_kwh_per_cycle: number };
    improvement: { defect_rate_change_percentage_points: number; energy_reduction_percent: number };
    candidate_search: { generated: number; ood_filtered: number; selected_is_in_distribution: boolean };
    optimizer_note: string;
  };
  impact: {
    energy_reduction_kwh: number;
    energy_reduction_percent: number;
    defect_rate_change_percentage_points: number;
    material_at_risk_current_kg: number;
    material_at_risk_optimized_kg: number;
    material_at_risk_reduction_kg: number;
  };
  evidence: EvidenceItem[];
  rag_backend: string;
  human_review_note: string;
  model_mode: string;
  data_sources: string[];
};
