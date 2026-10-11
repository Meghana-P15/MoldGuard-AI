# MoldGuard Model Card

Complete this with your **real-data** results before submission.

## Intended use
Decision support for pre-production injection-molding parameter review.

## Not intended for
- automatic machine control
- safety certification
- use outside validated materials/machines without revalidation

## Training data
- dataset:
- license:
- rows:
- production sites/machines represented:
- date range:

## Features
`Tinj,tinj,Pinj,Ph,Bp,th`

## Targets
- risk:
- energy:

## Split strategy
Explain whether the split is random, time-based, machine-based or production-run-based.

## Metrics
### Risk
- macro F1:
- per-class recall:
- confusion matrix:
- calibration/uncertainty notes:

### Energy
- MAE:
- RMSE:
- R²:

## OOD behavior
- method: IsolationForest
- contamination setting:
- examples rejected:

## Limitations
Document material/machine coverage and known failure modes.
