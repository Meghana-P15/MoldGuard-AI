# Real datasets included in this build

The final repository now physically includes:

- `ai/data/modelo.xlsx`
- `ai/data/test_dataset.csv`

The old packaged synthetic file `ai/data/demo_injection_molding.csv` has been removed.

> Note: the existing packaged model artifacts must still be retrained on validated
> real-data mappings before claiming real-world performance metrics.

---

# Real datasets to use before final submission

## 1) Primary scrap / rejection dataset
**Data Model for Injection Molding and Blow Molding — Mendeley Data**

https://data.mendeley.com/datasets/gtnb4j7bfx/1

Use production/process variables and derive a defensible scrap/rejection target from measured rejected units or material loss. Verify the exact column names after download.

## 2) Energy dataset
**Data-Driven Energy Efficiency in Injection Molding — Zenodo**

https://zenodo.org/records/20338544

Useful for energy behavior / anomaly / efficiency modeling. Do not pretend this dataset is row-wise joinable with the Mendeley dataset unless a real common key exists.

## 3) Optional optimization dataset
**Optimizing the plastic injection molding process and reducing warpage — Figshare**

https://figshare.com/articles/dataset/Optimizing_the_plastic_injection_molding_process_and_reducing_warpage_through_response_surface_methodology/29039676

Useful as a process-parameter/quality optimization reference or auxiliary experiment.

## 4) Advanced sensor time series
**Cross-process-chain injection molding dataset — Zenodo**

https://zenodo.org/records/17240390

Large time-series dataset; use only after the MVP works.

## 5) Reference-only dataset
**1000-batch polypropylene process dataset — Zenodo record**

https://zenodo.org/records/20309380

Its metadata is useful, but the downloadable files may be embargoed. Do not depend on it without verifying access.

## Integration rule

Train models separately when datasets are independent. Combine their outputs at the application/decision layer. Never fabricate a merged dataset.
