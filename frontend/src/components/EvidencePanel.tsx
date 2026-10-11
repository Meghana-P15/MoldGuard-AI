import type { EvidenceItem } from "../types";

export default function EvidencePanel({ evidence }: { evidence: EvidenceItem[] }) {
  return (
    <section className="card evidence-card">
      <div className="section-heading">
        <div>
          <span className="step">05 · Grounding</span>
          <h2>What should the operator verify?</h2>
        </div>
        <span className="subtle-pill">RAG evidence</span>
      </div>

      {evidence.length === 0 ? (
        <div className="empty-inline">
          Add machine SOPs or material datasheets to <code>knowledge/</code>.
        </div>
      ) : (
        <div className="evidence-list">
          {evidence.map((item, idx) => (
            <article key={`${item.source}-${idx}`}>
              <div className="evidence-meta">
                <strong>{item.section}</strong>
                <span>{item.source}</span>
              </div>
              <p>{item.snippet}</p>
              <small>Retrieval: {item.retrieval_mode} · score {item.score.toFixed(3)}</small>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
