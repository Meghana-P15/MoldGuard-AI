# UX v2 — Operator Decision Cockpit

The interface is intentionally not a generic analytics dashboard.

## Information hierarchy

1. **Decision first** — Low risk / Review required / High risk
2. **Can I trust this input?** — confidence + in/out-of-distribution
3. **Why?** — top model drivers
4. **What should change?** — before/after parameter differences
5. **What is the impact?** — energy + material-at-risk proxy
6. **What evidence supports the recommendation?** — retrieved SOP/material passages
7. **Human review** — recommendation is decision support, not automatic control

## UX rules

- Never hide uncertainty.
- Never present a recommendation as an automatic machine command.
- Show only changed parameters prominently.
- Keep all environmental impact claims traceable to a method.
- Use red only for states that require attention.
- Make demo data visibly marked as demo data.
