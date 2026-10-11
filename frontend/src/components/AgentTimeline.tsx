import type { AgentTimelineEvent } from "../types";

export default function AgentTimeline({ items }: { items: AgentTimelineEvent[] }) {
  return (
    <section className="card agent-timeline-card">
      <div className="section-heading">
        <div>
          <span className="step">Phase 4 · Agent orchestration</span>
          <h2>How MoldGuard investigated this batch</h2>
        </div>
        <span className="subtle-pill">Supervisor + specialists</span>
      </div>

      <div className="agent-timeline">
        {items.map((item) => (
          <div className="agent-step" key={`${item.step}-${item.actor}`}>
            <div className={`agent-status agent-${item.status.toLowerCase()}`}>
              {item.status === "DONE" ? "✓" : item.status === "BLOCKED" ? "!" : "↗"}
            </div>
            <div className="agent-step-copy">
              <div className="agent-step-head">
                <strong>{item.actor}</strong>
                <span>{item.status}</span>
              </div>
              <h3>{item.title}</h3>
              <p>{item.detail}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
