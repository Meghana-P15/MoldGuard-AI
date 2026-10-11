# MoldGuard ML Pipeline v2

## What materially improved

1. **Separate risk and energy training pipelines**
2. **Out-of-distribution detector** using IsolationForest
3. **Decision guardrail** that can return `REVIEW_REQUIRED`
4. **Constrained optimizer** that rejects OOD candidates
5. **Energy uncertainty interval** based on held-out validation MAE
6. **Risk-weighted material-at-risk proxy** when part weight is provided
7. **Optional Optuna tuning** for real data
8. **Grounded recommendation evidence** retrieved from SOP/material documents

## Recommended real-data order

- First make the real-data adapter correct.
- Use a production-run/time/group split when the dataset provides run IDs or timestamps.
- Only then tune hyperparameters.
- Report macro-F1, per-class recall, confusion matrix, MAE/RMSE/R², and OOD behavior.
- Never report synthetic-demo metrics as hackathon results.

## Why RAG is used

RAG is **not** used to predict defects.

It retrieves approved SOP/material guidance so the operator can see the
documents that should be checked before accepting a recommendation. This makes
the AI easier to audit and keeps the human in the loop.
