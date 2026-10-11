FEATURES = ["Tinj", "tinj", "Pinj", "Ph", "Tmold", "th"]
RISK_BANDS = ["G", "Y", "R"]

# Direct mapping to measured columns in the real molding dataset.
FEATURE_SOURCE_COLUMNS = {
    "Tinj": "Temp_mat_fundido",
    "tinj": "Tiempo_ciclo",
    "Pinj": "Presion_inyeccion_bares",
    "Ph": "Presion_retencion_bares",
    "Tmold": "Temp_molde_centigrados ",
    "th": "Tiempo_retencion_inyeccion_seg",
}

FEATURE_LABELS = {
    "Tinj": "Melt temperature",
    "tinj": "Cycle time",
    "Pinj": "Injection pressure",
    "Ph": "Holding pressure",
    "Tmold": "Mold temperature",
    "th": "Holding time",
}

FEATURE_UNITS = {
    "Tinj": "°C",
    "tinj": "s",
    "Pinj": "bar",
    "Ph": "bar",
    "Tmold": "°C",
    "th": "s",
}

# Operator validation bounds derived from observed real molding data and rounded
# for usability. They are not synthetic ranges.
PARAM_BOUNDS = {
    "Tinj": (220.0, 280.0),
    "tinj": (1.0, 50.0),
    "Pinj": (100.0, 180.0),
    "Ph": (40.0, 90.0),
    "Tmold": (60.0, 100.0),
    "th": (0.15, 25.5),
}

LOCAL_STEP_FRACTION = {
    "Tinj": 0.06,
    "tinj": 0.12,
    "Pinj": 0.08,
    "Ph": 0.08,
    "Tmold": 0.06,
    "th": 0.12,
}

# Configurable operational thresholds applied AFTER the real defect-rate model.
# Dataset values are fractions: 0.05 = 5% defective output.
GOOD_MAX_DEFECT_RATE = 0.05
WARNING_MAX_DEFECT_RATE = 0.06

# Energy regressor inputs are measured/derived only from test_dataset.csv.
ENERGY_FEATURES = [
    "TOTAL_CURRENT",
    "AVG_VOLTAGE",
    "AVG_PF",
    "AVG_FREQ",
    "MOLD_SPEED",
    "PRODUCTION_STATUS",
]
