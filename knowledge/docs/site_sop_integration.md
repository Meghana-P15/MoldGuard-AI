# Site SOP integration and human-review policy

This repository does not pretend that public references are the factory's own SOP. Before production deployment, place approved plant SOP text or exported SOP documents in `knowledge/docs/` so the semantic retriever can cite site-specific instructions.

A recommendation must be reviewed when the Isolation Forest marks the setting OUT_OF_DISTRIBUTION, when the predicted defect rate is above the high-risk threshold, when a proposed setting conflicts with an OEM/material limit, or when the retrieved evidence is not specific enough for the actual machine/material combination.

MoldGuard AI is advisory only. It must not bypass machine interlocks, OEM limits, material datasheets, validation procedures, or authorized process-engineer approval.
