import { useState } from "react";
import { runAgenticAnalysis } from "./api";
import type { AgentRunResponse, BatchInput } from "./types";

import ParameterPanel from "./components/ParameterPanel";
import RecommendationPanel from "./components/RecommendationPanel";
import EvidencePanel from "./components/EvidencePanel";
import AgentTimeline from "./components/AgentTimeline";
import AgentDecision from "./components/AgentDecision";
import AgentQualityPanel from "./components/AgentQualityPanel";

const initial: BatchInput = {
  Tinj: 230,
  tinj: 1.5,
  Pinj: 32,
  Ph: 18,
  Bp: 22,
  th: 6,
  cycles: 10000,
  part_weight_g: 18.5,
  material_code: "PP",
  machine_id: "DEMO-01",
  operator_note: "",
};

export default function App() {
  const [form, setForm] = useState<BatchInput>(initial);
  const [result, setResult] = useState<AgentRunResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function runAnalysis() {
    setBusy(true);
    setError("");
    try {
      setResult(await runAgenticAnalysis(form));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Agentic analysis failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-lockup">
          <div className="brand-mark">M</div>
          <div>
            <strong>MoldGuard AI</strong>
            <span>Agentic production decision cockpit</span>
          </div>
        </div>
        <div className="topbar-meta">
          <span>Strands Agents</span>
          <span>Amazon Bedrock AgentCore</span>
          <span>AWS Environmental Hacks</span>
        </div>
      </header>

      <section className="hero-copy">
        <div>
          <span className="eyebrow">Phase 4 · Agentic AI</span>
          <h1>Investigate the batch before it becomes waste.</h1>
          <p>
            A supervisor coordinates quality, optimization and knowledge specialists.
            Deterministic ML and safety rules remain the source of truth.
          </p>
        </div>
        <div className="hero-note">
          <strong>Autonomous investigation. Human-controlled action.</strong>
          <span>No agent can bypass process bounds, OOD checks or the final safety gate.</span>
        </div>
      </section>

      <ParameterPanel
        value={form}
        onChange={setForm}
        onAnalyze={runAnalysis}
        busy={busy}
      />

      {error && <div className="global-error">{error}</div>}

      {result && (
        <>
          <AgentTimeline items={result.timeline} />
          <AgentDecision result={result} />

          <section className="results-grid">
            <AgentQualityPanel quality={result.quality} />
            <section className="card">
              <div className="section-heading">
                <div>
                  <span className="step">Safety Gate</span>
                  <h2>Deterministic validation</h2>
                </div>
                <span className={result.safety.blocked ? "status-dot status-high" : "status-dot status-medium"}>
                  {result.safety.blocked ? "BLOCKED" : "HUMAN REVIEW"}
                </span>
              </div>

              <div className="safety-list">
                {result.safety.reasons.map((reason, idx) => (
                  <div key={idx}>
                    <span>{result.safety.blocked ? "!" : "✓"}</span>
                    <p>{reason}</p>
                  </div>
                ))}
              </div>
              <div className="human-loop">
                <strong>Non-overridable rule</strong>
                <p>{result.safety.rule}</p>
              </div>
            </section>
          </section>

          <RecommendationPanel
            input={form}
            optimization={result.optimization}
          />

          <EvidencePanel evidence={result.evidence} />

          {result.quality.model_mode === "demo" && (
            <div className="demo-banner">
              Demo smoke-test model — synthetic data. Replace model artifacts with
              real-data training results before making final performance claims.
            </div>
          )}

          <footer className="run-footer">
            Agent analysis ID: <code>{result.run_id}</code>
          </footer>
        </>
      )}
    </main>
  );
}
