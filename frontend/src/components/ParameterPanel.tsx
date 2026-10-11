import type { BatchInput } from "../types";

const processLabels: Record<string, { label: string; unit: string }> = {
  Tinj: { label: "Injection temperature", unit: "°C" },
  tinj: { label: "Injection time", unit: "s" },
  Pinj: { label: "Injection pressure", unit: "bar" },
  Ph: { label: "Holding pressure", unit: "bar" },
  Bp: { label: "Back pressure", unit: "bar" },
  th: { label: "Holding time", unit: "s" },
};

type Props = {
  value: BatchInput;
  onChange: (value: BatchInput) => void;
  onAnalyze: () => void;
  busy: boolean;
};

export default function ParameterPanel({ value, onChange, onAnalyze, busy }: Props) {
  const set = (key: keyof BatchInput, raw: string) => {
    if (key === "material_code" || key === "machine_id" || key === "operator_note") {
      onChange({ ...value, [key]: raw });
      return;
    }
    const num = Number(raw);
    onChange({ ...value, [key]: Number.isFinite(num) ? num : 0 });
  };

  return (
    <section className="card setup-card">
      <div className="section-heading">
        <div>
          <span className="step">01 · Batch setup</span>
          <h2>Describe the planned run</h2>
        </div>
        <span className="subtle-pill">No machine control</span>
      </div>

      <div className="context-grid">
        <label>
          <span>Machine ID</span>
          <input value={value.machine_id || ""} onChange={(e) => set("machine_id", e.target.value)} placeholder="DEMO-01" />
        </label>
        <label>
          <span>Material</span>
          <input value={value.material_code || ""} onChange={(e) => set("material_code", e.target.value)} placeholder="PP" />
        </label>
        <label>
          <span>Planned cycles</span>
          <input type="number" value={value.cycles} onChange={(e) => set("cycles", e.target.value)} />
        </label>
        <label>
          <span>Part weight (g)</span>
          <input type="number" step="0.1" value={value.part_weight_g ?? ""} onChange={(e) => set("part_weight_g", e.target.value)} placeholder="Optional" />
        </label>
      </div>

      <div className="divider" />

      <div className="parameter-grid">
        {Object.entries(processLabels).map(([key, meta]) => (
          <label className="parameter-field" key={key}>
            <span>{meta.label}</span>
            <div className="input-with-unit">
              <input
                type="number"
                step="0.1"
                value={value[key as keyof BatchInput] as number}
                onChange={(e) => set(key as keyof BatchInput, e.target.value)}
              />
              <em>{meta.unit}</em>
            </div>
          </label>
        ))}
      </div>

      <button className="primary-cta" onClick={onAnalyze} disabled={busy}>
        {busy ? "Agents are investigating…" : "Run Agentic Analysis"}
      </button>
      <p className="microcopy">
        Supervisor + specialist agents coordinate the analysis. The deterministic safety gate remains final; no direct machine control.
      </p>
    </section>
  );
}
