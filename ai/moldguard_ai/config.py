FEATURES = ["Tinj", "tinj", "Pinj", "Ph", "Bp", "th"]
CLASS_NAMES = ["G", "Y", "R"]

# Prototype bounds. Replace these with validated machine/material-specific limits
# before any real industrial deployment.
PARAM_BOUNDS = {
    "Tinj": (180.0, 260.0),
    "tinj": (0.5, 3.0),
    "Pinj": (15.0, 60.0),
    "Ph": (5.0, 40.0),
    "Bp": (5.0, 40.0),
    "th": (2.0, 12.0),
}

LOCAL_STEP_FRACTION = {
    "Tinj": 0.10,
    "tinj": 0.20,
    "Pinj": 0.20,
    "Ph": 0.20,
    "Bp": 0.20,
    "th": 0.20,
}

# Decision-support thresholds. These are prototype policy values, not universal
# industrial safety limits.
MIN_CONFIDENCE_FOR_AUTOMATED_RECOMMENDATION = 0.58
HIGH_REJECT_PROBABILITY = 0.50
MIN_GOOD_PROBABILITY_FOR_LOW_RISK = 0.65

# Proxy severity weights used only when a real waste-mass model is unavailable.
# Output is explicitly labeled "material-at-risk proxy".
MATERIAL_RISK_WEIGHTS = {"G": 0.0, "Y": 0.35, "R": 1.0}
