import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { AgentQuality } from "../types";

const labels: Record<string, string> = {
  Tinj: "Injection temperature",
  tinj: "Injection time",
  Pinj: "Injection pressure",
  Ph: "Holding pressure",
  Bp: "Back pressure",
  th: "Holding time",
};

export default function AgentQualityPanel({ quality }: { quality: AgentQuality }) {
  const data = [
    { name: "Good", value: Math.round(quality.probabilities.G * 100) },
    { name: "Warning", value: Math.round(quality.probabilities.Y * 100) },
    { name: "Reject", value: Math.round(quality.probabilities.R * 100) },
  ];

  const max = Math.max(...quality.top_risk_factors.map((x) => Math.abs(x.impact)), 0.001);

  return (
    <section className="card">
      <div className="section-heading">
        <div>
          <span className="step">Quality Agent</span>
          <h2>Risk + explainability</h2>
        </div>
        <span className={`status-dot status-${quality.risk_level.toLowerCase()}`}>
          {quality.risk_level}
        </span>
      </div>

      <div className="risk-chart">
        <ResponsiveContainer width="100%" height={190}>
          <BarChart data={data} margin={{ left: -18, right: 4 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="name" />
            <YAxis domain={[0, 100]} unit="%" />
            <Tooltip formatter={(v) => `${v}%`} />
            <Bar dataKey="value" fill="currentColor" radius={[9, 9, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="driver-list compact-drivers">
        {quality.top_risk_factors.map((factor) => {
          const width = Math.max(8, Math.abs(factor.impact) / max * 100);
          return (
            <div className="driver-row" key={factor.feature}>
              <div className="driver-copy">
                <strong>{labels[factor.feature] || factor.feature}</strong>
                <span>{factor.direction} predicted-class score</span>
              </div>
              <div className="driver-track">
                <div
                  className={`driver-fill ${factor.impact >= 0 ? "positive" : "negative"}`}
                  style={{ width: `${width}%` }}
                />
              </div>
              <code>{factor.impact >= 0 ? "+" : ""}{factor.impact.toFixed(3)}</code>
            </div>
          );
        })}
      </div>
    </section>
  );
}
