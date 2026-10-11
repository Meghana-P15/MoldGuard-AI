import type { PredictResponse } from "../types";

const readable: Record<string, string> = {
  Tinj: "Injection temperature",
  tinj: "Injection time",
  Pinj: "Injection pressure",
  Ph: "Holding pressure",
  Bp: "Back pressure",
  th: "Holding time",
};

export default function DriversPanel({ prediction }: { prediction: PredictResponse }) {
  const max = Math.max(...prediction.top_risk_factors.map((d) => Math.abs(d.impact)), 0.001);

  return (
    <section className="card">
      <div className="section-heading">
        <div>
          <span className="step">03 · Explainability</span>
          <h2>What drove this result?</h2>
        </div>
        <span className="subtle-pill">SHAP contributions</span>
      </div>

      <div className="driver-list">
        {prediction.top_risk_factors.map((factor) => {
          const width = Math.max(8, Math.abs(factor.impact) / max * 100);
          return (
            <div className="driver-row" key={factor.feature}>
              <div className="driver-copy">
                <strong>{readable[factor.feature] || factor.feature}</strong>
                <span>{factor.direction} the predicted-class score</span>
              </div>
              <div className="driver-track">
                <div className={`driver-fill ${factor.impact >= 0 ? "positive" : "negative"}`} style={{ width: `${width}%` }} />
              </div>
              <code>{factor.impact >= 0 ? "+" : ""}{factor.impact.toFixed(3)}</code>
            </div>
          );
        })}
      </div>
    </section>
  );
}
