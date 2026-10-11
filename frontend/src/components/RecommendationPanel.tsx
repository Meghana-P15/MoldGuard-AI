import type { BatchInput, OptimizeResponse } from "../types";

const labels: Record<string, string> = {
  Tinj: "Injection temp.",
  tinj: "Injection time",
  Pinj: "Injection pressure",
  Ph: "Holding pressure",
  Bp: "Back pressure",
  th: "Holding time",
};

export default function RecommendationPanel({
  input,
  optimization,
}: {
  input: BatchInput;
  optimization: OptimizeResponse;
}) {
  const changed = Object.entries(optimization.recommended_parameters).filter(([key, value]) => {
    const current = Number((input as unknown as Record<string, number>)[key]);
    return Math.abs(current - Number(value)) > 0.001;
  });

  return (
    <section className="card recommendation-card">
      <div className="section-heading">
        <div>
          <span className="step">04 · Recommendation</span>
          <h2>Smallest useful changes</h2>
        </div>
        <span className={optimization.guardrail.recommendation_available ? "status-dot status-low" : "status-dot status-medium"}>
          {optimization.guardrail.recommendation_available ? "AVAILABLE" : "NO CLEAR GAIN"}
        </span>
      </div>

      <div className="before-after-hero">
        <div>
          <span>Good probability</span>
          <strong>{Math.round(optimization.current.good_probability * 100)}%</strong>
          <small>Current</small>
        </div>
        <div className="flow-arrow">→</div>
        <div>
          <span>Good probability</span>
          <strong>{Math.round(optimization.optimized.good_probability * 100)}%</strong>
          <small>Recommended</small>
        </div>
      </div>

      <div className="change-table">
        <div className="table-head"><span>Parameter</span><span>Current</span><span>Recommended</span><span>Δ</span></div>
        {changed.length === 0 && <div className="empty-inline">No parameter change cleared the improvement threshold.</div>}
        {changed.map(([key, value]) => {
          const current = Number((input as unknown as Record<string, number>)[key]);
          const delta = Number(value) - current;
          return (
            <div className="change-row" key={key}>
              <strong>{labels[key] || key}</strong>
              <span>{current.toFixed(2)}</span>
              <span>{Number(value).toFixed(2)}</span>
              <span className={delta > 0 ? "delta-up" : "delta-down"}>{delta > 0 ? "+" : ""}{delta.toFixed(2)}</span>
            </div>
          );
        })}
      </div>

      <div className="impact-grid">
        <div>
          <span>Energy reduction</span>
          <strong>{optimization.improvement.energy_reduction_percent.toFixed(2)}%</strong>
        </div>
        <div>
          <span>Reject-probability change</span>
          <strong>{(optimization.improvement.reject_probability_change * 100).toFixed(1)} pp</strong>
        </div>
        <div>
          <span>OOD candidates blocked</span>
          <strong>{optimization.guardrail.skipped_out_of_distribution_candidates}</strong>
        </div>
      </div>

      {optimization.material_impact.available && (
        <div className="material-strip">
          <span>Material-at-risk reduction proxy</span>
          <strong>{optimization.material_impact.material_at_risk_reduction_kg?.toFixed(2)} kg</strong>
          <small>Use measured waste data for final industrial claims.</small>
        </div>
      )}

      <div className="human-loop">
        <strong>Human-in-the-loop checkpoint</strong>
        <p>{optimization.optimizer_note}</p>
      </div>
    </section>
  );
}
