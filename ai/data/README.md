# MoldGuard real datasets

This build contains the two real-world dataset files provided by the project team:

- `modelo.xlsx`
- `test_dataset.csv`

The previously packaged `demo_injection_molding.csv` synthetic dataset has been removed.

## Important

Including the real files does **not** automatically make the existing packaged
`.joblib` artifacts real-data-trained. Before final model-performance claims,
inspect/map the real dataset columns and rerun the training pipeline so the risk,
energy and OOD artifacts plus metrics are generated from the real data.

Do not fabricate a row-wise merge between independent datasets unless a genuine
shared key exists.
