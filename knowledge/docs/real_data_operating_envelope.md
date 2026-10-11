# Real-data operating envelope

Generated from measured injection-molding records in `modelo.xlsx`.
This is a data-familiarity reference, not an OEM or factory SOP.

## Observed process ranges

- **Melt temperature (Tinj)**: observed 220.020 to 280.000 °C; central 98% approximately 220.510 to 279.443 °C.
- **Cycle time (tinj)**: observed 1.000 to 49.400 s; central 98% approximately 17.893 to 47.600 s.
- **Injection pressure (Pinj)**: observed 100.010 to 179.970 bar; central 98% approximately 100.809 to 179.204 bar.
- **Holding pressure (Ph)**: observed 40.020 to 89.990 bar; central 98% approximately 40.569 to 89.491 bar.
- **Mold temperature (Tmold)**: observed 60.000 to 100.000 °C; central 98% approximately 60.300 to 99.700 °C.
- **Holding time (th)**: observed 0.172 to 25.484 s; central 98% approximately 3.773 to 19.071 s.

## Defect-rate decision thresholds

- GOOD: predicted defect rate ≤ 5.0%
- WARNING: > 5.0% and ≤ 6.0%
- HIGH RISK: > 6.0%

## Human-review rule

Settings flagged out-of-distribution by the Isolation Forest require process-engineer review.
Recommendations are decision support only and are never sent directly to machine controls.