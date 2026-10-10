# MoldGuard AI datasets

This project now keeps **only two raw real-world data files** in `ai/data/`.

## 1. `modelo.xlsx` — molding process + quality

Used directly at training time for the risk/quality model. The pipeline filters to injection-molding rows and uses measured process variables plus `%Defectuosos` to derive the G/Y/R quality-risk classes.

## 2. `test_dataset.csv` — machine electrical / energy telemetry

Used directly at training time for the energy component. `TOTAL_ACT_POWER` is the measured power source used to calibrate the energy distribution.

## Important integration rule

The two datasets are independent and have no verified common row key. MoldGuard does **not** claim that row N in `modelo.xlsx` corresponds to row N in `test_dataset.csv`.

To preserve the existing MoldGuard API, preprocessing and harmonization happen **in memory inside `ai/training/train_all.py`**. No third generated dataset is written to disk.

Run training with:

```bash
python -m ai.training.train_all
```

The command reads only `modelo.xlsx` and `test_dataset.csv` and writes model artifacts to `ai/models/`.
