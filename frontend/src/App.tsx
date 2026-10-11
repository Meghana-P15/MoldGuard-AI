import { useEffect, useState } from "react";
import { analyzeBatch, getMeta } from "./api";
import type { AnalyzeResponse, BatchInput, MetaResponse, ProcessKey } from "./types";

const processKeys: ProcessKey[] = ["Tinj", "tinj", "Pinj", "Ph", "Tmold", "th"];

const fallback: BatchInput = {
  machine: "I-10",
  material: "A-PROD",
  Tinj: 250,
  tinj: 29,
  Pinj: 140,
  Ph: 65,
  Tmold: 80,
  th: 9,
  cycles: 1000,
  part_weight_g: 250,
};

const decisionTitle: Record<string, string> = {
  GOOD: "Good",
  WARNING: "Warning",
  HIGH_RISK: "High Risk",
  REVIEW_REQUIRED: "Review Required",
};

export default function App() {
  const [meta, setMeta] = useState<MetaResponse | null>(null);
  const [form, setForm] = useState<BatchInput>(fallback);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getMeta()
      .then((m) => {
        setMeta(m);
        setForm((prev) => ({
          ...prev,
          machine: m.machines[0] || prev.machine,
          material: m.materials[0] || prev.material,
          part_weight_g: m.part_weight.median_g || prev.part_weight_g,
          ...m.defaults,
        }));
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Could not load model metadata"));
  }, []);

  function setNumber(key: keyof BatchInput, value: string) {
    const parsed = key === "cycles" ? Number.parseInt(value || "0", 10) : Number(value);
    setForm((old) => ({ ...old, [key]: Number.isFinite(parsed) ? parsed : 0 }));
  }

  async function analyze() {
    setBusy(true);
    setError("");
    try {
      setResult(await analyzeBatch(form));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <div className="eyebrow">MoldGuard AI · Decision Cockpit</div>
          <h1>Prevent scrap before production.</h1>
          <p>Real defect-rate prediction, data-familiarity checks, real-energy estimation, constrained optimization and evidence-backed recommendations.</p>
        </div>
        <div className="real-data-pill">2 real datasets · no synthetic training data</div>
      </header>

      <section className="layout">
        <article className="card input-card">
          <div className="card-heading">
            <div><span className="step">1</span><h2>Machine parameters</h2></div>
            <small>Operator input</small>
          </div>

          <div className="form-grid">
            <label>
              <span>Machine</span>
              <select value={form.machine} onChange={(e) => setForm((x) => ({ ...x, machine: e.target.value }))}>
                {(meta?.machines || [form.machine]).map((x) => <option key={x}>{x}</option>)}
              </select>
            </label>
            <label>
              <span>Material / energy profile</span>
              <select value={form.material} onChange={(e) => setForm((x) => ({ ...x, material: e.target.value }))}>
                {(meta?.materials || [form.material]).map((x) => <option key={x}>{x}</option>)}
              </select>
            </label>

            {processKeys.map((key) => {
              const bounds = meta?.parameter_bounds?.[key];
              return (
                <label key={key}>
                  <span>{meta?.feature_labels?.[key] || key}</span>
                  <div className="input-wrap">
                    <input
                      type="number"
                      step="0.1"
                      min={bounds?.[0]}
                      max={bounds?.[1]}
                      value={form[key]}
                      onChange={(e) => setNumber(key, e.target.value)}
                    />
                    <em>{meta?.feature_units?.[key] || ""}</em>
                  </div>
                </label>
              );
            })}

            <label>
              <span>Production cycles</span>
              <input type="number" min="1" value={form.cycles} onChange={(e) => setNumber("cycles", e.target.value)} />
            </label>
            <label>
              <span>Part weight</span>
              <div className="input-wrap">
                <input type="number" min="0.1" step="0.1" value={form.part_weight_g} onChange={(e) => setNumber("part_weight_g", e.target.value)} />
                <em>g</em>
              </div>
            </label>
          </div>

          <button className="primary" onClick={analyze} disabled={busy}>{busy ? "Analyzing…" : "Analyze Before Production"}</button>
          {error && <div className="error">{error}</div>}
          <p className="tiny">Risk is predicted as a real defect rate from <b>modelo.xlsx</b>; G/Y/R is assigned only after prediction using explicit thresholds.</p>
        </article>

        <article className="card result-card">
          <div className="card-heading">
            <div><span className="step purple">2</span><h2>Interactive result</h2></div>
            <small>/api/analyze</small>
          </div>

          {!result ? <div className="empty">Enter the planned batch settings and run the analysis.</div> : <>
            <div className={`decision ${result.batch_decision.toLowerCase()}`}>
              <div>
                <small>Batch decision</small>
                <strong>{decisionTitle[result.batch_decision]}</strong>
              </div>
              <div>
                <small>Predicted defects</small>
                <strong>{result.predicted_defect_percent.toFixed(2)}%</strong>
              </div>
              <div>
                <small>Data familiarity</small>
                <strong>{result.data_familiarity.in_distribution ? "IN" : "OUT"}</strong>
              </div>
            </div>

            <div className="mini-grid">
              <div><span>Defect uncertainty</span><b>±{result.defect_uncertainty_percentage_points.toFixed(2)} pp</b></div>
              <div><span>Risk thresholds</span><b>{(result.risk_thresholds.good_max * 100).toFixed(0)}% / {(result.risk_thresholds.warning_max * 100).toFixed(0)}%</b></div>
              <div><span>Power estimate</span><b>{result.energy.predicted_power_watts.toFixed(0)} W</b></div>
              <div><span>Energy / cycle</span><b>{result.energy.kwh_per_cycle.toFixed(5)} kWh</b></div>
              <div><span>Batch energy</span><b>{result.energy.current_batch_kwh.toFixed(2)} kWh</b></div>
              <div><span>RAG backend</span><b>{result.rag_backend}</b></div>
            </div>
          </>}
        </article>
      </section>

      {result && <>
        <section className="layout three">
          <article className="card">
            <h2>Top defect-rate drivers</h2>
            <div className="drivers">
              {result.top_risk_factors.map((x) => <div className="driver" key={x.feature}>
                <span>{meta?.feature_labels?.[x.feature as ProcessKey] || x.feature}</span>
                <b>{x.impact >= 0 ? "+" : ""}{x.impact.toFixed(3)} pp</b>
                <small>{x.direction} predicted defect rate</small>
              </div>)}
            </div>
          </article>

          <article className="card">
            <h2>Recommended settings</h2>
            <div className="settings-table">
              {processKeys.map((key) => <div key={key}>
                <span>{key}</span><span>{form[key].toFixed(2)}</span><i>→</i><b>{result.recommended_parameters[key].toFixed(2)}</b>
              </div>)}
            </div>
            <p className="tiny">{result.optimization.candidate_search.generated} candidates searched; {result.optimization.candidate_search.ood_filtered} OOD candidates filtered.</p>
          </article>

          <article className="card">
            <h2>Impact calculation</h2>
            <div className="impact-list">
              <div><span>Energy reduction</span><b>{result.impact.energy_reduction_percent.toFixed(2)}%</b></div>
              <div><span>Energy saved</span><b>{result.impact.energy_reduction_kwh.toFixed(2)} kWh</b></div>
              <div><span>Defect-rate change</span><b>{result.impact.defect_rate_change_percentage_points.toFixed(2)} pp</b></div>
              <div><span>Material-at-risk reduction</span><b>{result.impact.material_at_risk_reduction_kg.toFixed(2)} kg</b></div>
            </div>
          </article>
        </section>

        <section className="layout">
          <article className="card">
            <h2>Evidence from knowledge service</h2>
            <div className="evidence-list">
              {result.evidence.map((e, i) => <div key={`${e.source}-${i}`}>
                <b>{e.source}</b><p>{e.excerpt}</p><small>{e.retrieval_backend || result.rag_backend} · score {e.score.toFixed(3)}</small>
              </div>)}
            </div>
          </article>
          <article className="card review-card">
            <h2>Human review</h2>
            <p>{result.human_review_note}</p>
            <div className="source-box"><b>Training sources</b>{result.data_sources.map((x) => <span key={x}>{x}</span>)}</div>
            <p className="tiny">The energy telemetry model is trained directly on measured electrical data; it is not row-wise paired with the molding dataset.</p>
          </article>
        </section>
      </>}
    </main>
  );
}
