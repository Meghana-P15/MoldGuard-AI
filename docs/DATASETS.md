# Datasets

Only two raw real-world datasets are used.

## `ai/data/modelo.xlsx`

Used for the defect-rate XGBoost regressor and Isolation Forest OOD model. The target is the measured `%Defectuosos` field; no synthetic G/Y/R target is created.

| API feature | Real source column |
|---|---|
| `Tinj` | `Temp_mat_fundido` |
| `tinj` | `Tiempo_ciclo` |
| `Pinj` | `Presion_inyeccion_bares` |
| `Ph` | `Presion_retencion_bares` |
| `Tmold` | `Temp_molde_centigrados ` |
| `th` | `Tiempo_retencion_inyeccion_seg` |

After predicting the real defect rate, the application applies configurable operational thresholds: GOOD ≤ 5%, WARNING >5% to ≤6%, HIGH RISK >6%.

## `ai/data/test_dataset.csv`

Used for the real electrical-power XGBoost regressor. Target: `TOTAL_ACT_POWER`.

Features: total current, average phase voltage, average power factor, average frequency, `MOLD_SPEED`, and `PRODUCTION_STATUS`.

The energy and molding datasets are independent and are not row-wise paired.

## Data policy

`synthetic_data_used=false` is written to model metadata. No generated compatibility CSV is created.
