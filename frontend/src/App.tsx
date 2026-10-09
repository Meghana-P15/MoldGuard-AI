import { useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { optimizeBatch, predictBatch } from "./api";
import type { BatchInput, OptimizeResponse, PredictResponse } from "./types";

const initial: BatchInput = {
  Tinj: 230,
  tinj: 1.5,
  Pinj: 32,
  Ph: 18,
  Bp: 22,
  th: 6,
  cycles: 10000,
};

const labels: Record<keyof BatchInput, string> = {
  Tinj: "Injection temperature",
  tinj: "Injection time",
  Pinj: "Injection pressure",
  Ph: "Holding pressure",
  Bp: "Back pressure",
  th: "Holding time",
  cycles: "Planned cycles",
};

const units: Partial<Record<keyof BatchInput, string>> = {
  Tinj: "°C",
  tinj: "s",
  Pinj: "bar",
  Ph: "bar",
  Bp: "bar",
  th: "s",
};

export default function App() {
  const [form, setForm] = useState<BatchInput>(initial);
  const [prediction, setPrediction] = useState<PredictResponse | null>(null);
  const [optimization, setOptimization] = useState<OptimizeResponse | null>(null);
  const [busy, setBusy] = useState<"predict" | "optimize" | null>(null);
  const [error, setError] = useState("");

  const probabilityData = useMemo(() => {
    if (!prediction) return [];
    return [
      { name: "Good", value: Math.round(prediction.probabilities.G * 100) },
      { name: "Warning", value: Math.round(prediction.probabilities.Y * 100) },
      { name: "Reject", value: Math.round(prediction.probabilities.R * 100) },
    ];
  }, [prediction]);

  function update(key: keyof BatchInput, raw: string) {
    const numeric = key === "cycles" ? Number.parseInt(raw || "0", 10) : Number(raw);
    setForm((prev) => ({ ...prev, [key]: Number.isFinite(numeric) ? numeric : 0 }));
  }

  async function runPrediction() {
    setBusy("predict");
    setError("");
    setOptimization(null);
    try {
      setPrediction(await predictBatch(form));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Prediction failed");
    } finally {
      setBusy(null);
    }
  }

  async function runOptimization() {
    setBusy("optimize");
    setError("");
    try {
      setOptimization(await optimizeBatch(form));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Optimization failed");
    } finally {
      setBusy(null);
    }
  }

  return (
    <main className="shell">
      <header className="hero">
        <div>
          <div className="eyebrow">AWS Environmental Hacks · Waste & Energy</div>
          <h1>MoldGuard AI</h1>
          <p>Predict scrap risk before production, explain the drivers, and recommend lower-risk, lower-energy settings.</p>
        </div>
        <div className="badge">Prevent waste before it happens</div>
      </header>

      <section className="grid two">
        <article className="card">
          <h2>Current machine settings</h2>
          <p className="muted">Enter the planned injection-molding process parameters.</p>
          <div className="form-grid">
            {(Object.keys(form) as (keyof BatchInput)[]).map((key) => (
              <label key={key}>
                <span>{labels[key]}</span>
                <div className="input-wrap">
                  <input
                    type="number"
                    step={key === "cycles" ? "1" : "0.1"}
                    value={form[key]}
                    onChange={(e) => update(key, e.target.value)}
                  />
                  {units[key] && <em>{units[key]}</em>}
                </div>
              </label>
            ))}
          </div>
          <div className="actions">
            <button onClick={runPrediction} disabled={busy !== null}>
              {busy === "predict" ? "Analyzing…" : "Analyze batch"}
            </button>
            <button className="secondary" onClick={runOptimization} disabled={busy !== null || !prediction}>
              {busy === "optimize" ? "Optimizing…" : "Optimize settings"}
            </button>
          </div>
          {error && <div className="error">{error}</div>}
        </article>

        <article className="card">
          <h2>Batch risk</h2>
          {!prediction ? (
            <div className="empty">Run <strong>Analyze batch</strong> to see the risk profile.</div>
          ) : (
            <>
              <div className={`risk ${prediction.risk_level.toLowerCase()}`}>
                <div>
                  <span>Predicted class</span>
                  <strong>{prediction.prediction}</strong>
                </div>
                <div>
                  <span>Risk level</span>
                  <strong>{prediction.risk_level}</strong>
                </div>
              </div>
              <div className="chart">
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={probabilityData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="name" />
                    <YAxis domain={[0, 100]} unit="%" />
                    <Tooltip formatter={(v) => `${v}%`} />
                    <Bar dataKey="value" fill="currentColor" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="stat-row">
                <div><span>Energy / cycle</span><strong>{prediction.predicted_energy.toFixed(3)}</strong></div>
                <div><span>Projected energy</span><strong>{prediction.projected_energy.toFixed(1)}</strong></div>
              </div>
              {prediction.model_mode === "demo" && (
                <div className="warning">Demo smoke-test model — synthetic data. Replace with the real trained artifacts before judging.</div>
              )}
            </>
          )}
        </article>
      </section>

      {prediction && (
        <section className="grid two">
          <article className="card">
            <h2>Why did the model predict this?</h2>
            <p className="muted">Top XGBoost SHAP contribution values for the predicted class.</p>
            <div className="drivers">
              {prediction.top_risk_factors.length === 0 && <div className="empty">Contribution details unavailable.</div>}
              {prediction.top_risk_factors.map((factor) => (
                <div className="driver" key={factor.feature}>
                  <span>{factor.feature}</span>
                  <strong>{factor.impact >= 0 ? "+" : ""}{factor.impact.toFixed(3)}</strong>
                  <small>{factor.direction} predicted score</small>
                </div>
              ))}
            </div>
          </article>

          <article className="card">
            <h2>Optimized settings</h2>
            {!optimization ? (
              <div className="empty">Click <strong>Optimize settings</strong> after analyzing the batch.</div>
            ) : (
              <>
                <div className="comparison">
                  <div>
                    <span>Good probability</span>
                    <strong>{Math.round(optimization.current.good_probability * 100)}%</strong>
                    <small>Current</small>
                  </div>
                  <div className="arrow">→</div>
                  <div>
                    <span>Good probability</span>
                    <strong>{Math.round(optimization.optimized.good_probability * 100)}%</strong>
                    <small>Recommended</small>
                  </div>
                </div>
                <div className="settings-table">
                  {Object.entries(optimization.recommended_parameters).map(([key, value]) => (
                    <div key={key}>
                      <span>{key}</span>
                      <span>{(form as unknown as Record<string, number>)[key]?.toFixed?.(2)}</span>
                      <span>→</span>
                      <strong>{Number(value).toFixed(2)}</strong>
                    </div>
                  ))}
                </div>
                <div className="impact">
                  <div><span>Energy reduction</span><strong>{optimization.improvement.energy_reduction_percent.toFixed(2)}%</strong></div>
                  <div><span>Projected energy saved</span><strong>{optimization.projected.energy_saved.toFixed(2)}</strong></div>
                </div>
                <p className="footnote">{optimization.optimizer_note}</p>
              </>
            )}
          </article>
        </section>
      )}
    </main>
  );
}
