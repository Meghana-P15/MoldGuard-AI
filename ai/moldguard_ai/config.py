FEATURES = ["Tinj", "tinj", "Pinj", "Ph", "Bp", "th"]
CLASS_NAMES = ["G", "Y", "R"]

# Prototype bounds. Replace with equipment/material validated bounds before any real deployment.
PARAM_BOUNDS = {
    "Tinj": (180.0, 260.0),
    "tinj": (0.5, 3.0),
    "Pinj": (15.0, 60.0),
    "Ph": (5.0, 40.0),
    "Bp": (5.0, 40.0),
    "th": (2.0, 12.0),
}

# Max local change explored by the optimizer from the operator's current setting.
LOCAL_STEP_FRACTION = {
    "Tinj": 0.10,
    "tinj": 0.20,
    "Pinj": 0.20,
    "Ph": 0.20,
    "Bp": 0.20,
    "th": 0.20,
}
