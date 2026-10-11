import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { PredictResponse } from "../types";

export default function RiskPanel({ prediction }: { prediction: PredictResponse }) {
  const data = [
    { name: "Good", value: Math.round(prediction.probabilities.G * 100) },
    { name: "Warning", value: Math.round(prediction.probabilities.Y * 100) },
    { name: "Reject", value: Math.round(prediction.probabilities.R * 100) },
  ];

  return (
    <section className="card">
      <div className="section-heading">
        <div>
          <span className="step">02 · Model view</span>
          <h2>Risk distribution</h2>
        </div>
        <span className={`status-dot status-${prediction.risk_level.toLowerCase()}`}>
          {prediction.risk_level}
        </span>
      </div>

      <div className="risk-chart">
        <ResponsiveContainer width="100%" height={210}>
          <BarChart data={data} margin={{ left: -18, right: 4 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="name" />
            <YAxis domain={[0, 100]} unit="%" />
            <Tooltip formatter={(v) => `${v}%`} />
            <Bar dataKey="value" fill="currentColor" radius={[10, 10, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="metric-grid three">
        <div>
          <span>Energy / cycle</span>
          <strong>{prediction.predicted_energy.toFixed(3)}</strong>
        </div>
        <div>
          <span>Expected interval</span>
          <strong>{prediction.energy_interval.low.toFixed(2)}–{prediction.energy_interval.high.toFixed(2)}</strong>
        </div>
        <div>
          <span>Projected energy</span>
          <strong>{prediction.projected_energy.toFixed(1)}</strong>
        </div>
      </div>

      {prediction.material_impact.available && (
        <div className="material-strip">
          <span>Material-at-risk proxy</span>
          <strong>{prediction.material_impact.material_at_risk_kg?.toFixed(2)} kg</strong>
          <small>Transparent proxy — not measured scrap mass.</small>
        </div>
      )}
    </section>
  );
}
