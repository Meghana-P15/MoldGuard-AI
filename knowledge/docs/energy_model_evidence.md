# Real energy-model evidence

The energy model is trained directly from `test_dataset.csv` using measured `TOTAL_ACT_POWER` as the regression target. Its predictors are measured/derived electrical telemetry: total current, average voltage, average power factor, average frequency, mold speed and production status.

`test_dataset.csv` and `modelo.xlsx` do not share a reliable cycle identifier, so MoldGuard does not create a synthetic row-wise merge. When live telemetry is unavailable, the API uses median real telemetry profiles for the selected product/energy profile and converts predicted watts to kWh per cycle using the planned cycle time.
