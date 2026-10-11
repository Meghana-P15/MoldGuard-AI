import type { PredictResponse } from "../types";

function labelForDecision(decision: PredictResponse["decision"]) {
  if (decision === "LOW_RISK") return "Low model risk";
  if (decision === "HIGH_RISK") return "High model risk";
  return "Review required";
}

export default function DecisionHero({ prediction }: { prediction: PredictResponse }) {
  return (
    <section className={`decision-hero decision-${prediction.decision.toLowerCase()}`}>
      <div>
        <span className="kicker">Model decision</span>
        <h2>{labelForDecision(prediction.decision)}</h2>
        <p>{prediction.reasons[0]}</p>
      </div>
      <div className="decision-metrics">
        <div>
          <span>Confidence</span>
          <strong>{Math.round(prediction.confidence * 100)}%</strong>
        </div>
        <div>
          <span>Distribution</span>
          <strong>{prediction.distribution.status.replaceAll("_", " ")}</strong>
        </div>
        <div>
          <span>Predicted class</span>
          <strong>{prediction.prediction}</strong>
        </div>
      </div>
    </section>
  );
}
