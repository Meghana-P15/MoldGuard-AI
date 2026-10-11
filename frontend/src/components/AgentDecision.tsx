import type { AgentRunResponse } from "../types";

function short(value?: string | null) {
  if (!value) return "Available after AWS tracing";
  return value.length > 16 ? `${value.slice(0, 8)}…${value.slice(-6)}` : value;
}

export default function AgentDecision({ result }: { result: AgentRunResponse }) {
  const blocked = result.safety.blocked;
  const review = result.human_review_required;

  return (
    <section className={`agent-decision ${blocked ? "agent-decision-blocked" : "agent-decision-review"}`}>
      <div>
        <span className="kicker">Supervisor decision</span>
        <h2>{result.decision.replaceAll("_", " ")}</h2>
        <p>{result.supervisor_summary}</p>
        <div className="trace-strip">
          <span>Session <code>{short(result.agent_session_id)}</code></span>
          <span>Trace <code>{short(result.agent_trace_id)}</code></span>
        </div>
      </div>

      <div className="agent-decision-metrics">
        <div>
          <span>Model confidence</span>
          <strong>{Math.round(result.quality.confidence * 100)}%</strong>
        </div>
        <div>
          <span>Data familiarity</span>
          <strong>{result.quality.distribution.status.replaceAll("_", " ")}</strong>
        </div>
        <div>
          <span>Agent mode</span>
          <strong>{result.mode.includes("agentcore") ? "AgentCore" : "Local"}</strong>
        </div>
        <div>
          <span>Human approval</span>
          <strong>{review ? "Required" : "Not required"}</strong>
        </div>
      </div>
    </section>
  );
}
