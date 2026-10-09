export type BatchInput = {
  Tinj: number;
  tinj: number;
  Pinj: number;
  Ph: number;
  Bp: number;
  th: number;
  cycles: number;
};

export type RiskFactor = {
  feature: string;
  impact: number;
  direction: string;
};

export type PredictResponse = {
  prediction: "G" | "Y" | "R";
  risk_level: string;
  probabilities: Record<"G" | "Y" | "R", number>;
  predicted_energy: number;
  projected_energy: number;
  top_risk_factors: RiskFactor[];
  model_mode: string;
  note: string;
};

export type OptimizeResponse = {
  current: {
    parameters: Record<string, number>;
    good_probability: number;
    energy: number;
  };
  recommended_parameters: Record<string, number>;
  optimized: {
    good_probability: number;
    energy: number;
  };
  improvement: {
    good_probability_change: number;
    energy_reduction_percent: number;
  };
  projected: {
    cycles: number;
    current_energy: number;
    optimized_energy: number;
    energy_saved: number;
  };
  optimizer_note: string;
  model_mode: string;
};
