"""Configurable prototype parameters for the ResQDrive intelligence engines.

EVERY value here is an ILLUSTRATIVE prototype parameter, NOT a scientifically
validated constant. Centralising them makes the fusion / risk behaviour easy to
tune and later replace with calibrated or learned values.
"""

# ---------------------------------------------------------------------------
# Sensor reliability weights (0-1): how much we trust each evidence source.
# ---------------------------------------------------------------------------
SENSOR_RELIABILITY = {
    "CAMERA": 0.90,        # high-quality edge AI camera detection
    "GPS": 0.95,           # positioning quality
    "IMU": 0.75,           # gyroscope / abnormal-motion inference
    "ACCELEROMETER": 0.72, # vibration / shock inference
    "OBD": 0.80,           # vehicle telemetry (e.g. abnormal speed drop)
    "CITIZEN": 0.55,       # manual citizen report (lower trust)
}
DEFAULT_SENSOR_RELIABILITY = 0.60

# ---------------------------------------------------------------------------
# Temporal freshness: exponential decay constant in minutes.
# freshness_weight = exp(-age_minutes / FRESHNESS_DECAY_MIN)
# ---------------------------------------------------------------------------
FRESHNESS_DECAY_MIN = 20.0

# ---------------------------------------------------------------------------
# Corroboration: independence strength added per additional INDEPENDENT vehicle.
# Tuned so fused confidence grows with diminishing returns:
#   1 veh ~82%, 2 ~89%, 3 ~93%, 4 ~96%, 5+ approaches 97-99%.
# ---------------------------------------------------------------------------
INDEPENDENCE_K = 0.5
MAX_CONFIDENCE = 0.99   # never claim absolute certainty

# ---------------------------------------------------------------------------
# Spatial clustering radius (meters). Observations within this radius are
# candidate evidence for the SAME incident.
# ---------------------------------------------------------------------------
CLUSTER_RADIUS_M = 200.0

# ---------------------------------------------------------------------------
# Verification-state thresholds.
# ---------------------------------------------------------------------------
CONFLICT_AGREEMENT_THRESHOLD = 0.75   # below this (with conflict) => CONFLICTING
STALE_FRESHNESS_THRESHOLD = 0.18      # incident recency below this => STALE
VERIFIED_MIN_VEHICLES = 3
VERIFIED_MIN_CONFIDENCE = 0.90
CORROBORATED_MIN_VEHICLES = 2
CORROBORATED_MIN_CONFIDENCE = 0.75

# ---------------------------------------------------------------------------
# Hazard severity -> base score (0-1) used by the risk engine.
# ---------------------------------------------------------------------------
SEVERITY_SCORE = {
    "LOW": 0.35,
    "MODERATE": 0.60,
    "HIGH": 0.85,
    "CRITICAL": 1.0,
}
DEFAULT_SEVERITY = "MODERATE"

# ---------------------------------------------------------------------------
# Risk model component weights (must sum to 1.0).
# risk = 0.35*severity + 0.25*confidence + 0.15*freshness
#        + 0.20*agreement + 0.05*sensor_reliability
# ---------------------------------------------------------------------------
RISK_WEIGHTS = {
    "severity": 0.35,
    "confidence": 0.25,
    "freshness": 0.15,
    "agreement": 0.20,
    "sensor_reliability": 0.05,
}

# Road / incident risk-state thresholds (0-100).
RISK_UNSAFE = 80
RISK_CAUTION = 50

# ---------------------------------------------------------------------------
# Response prioritisation weights (must sum to 1.0).
# priority = 0.45*risk + 0.25*severity + 0.15*traffic_impact
#            + 0.10*freshness + 0.05*infrastructure_importance
# ---------------------------------------------------------------------------
PRIORITY_WEIGHTS = {
    "risk": 0.45,
    "severity": 0.25,
    "traffic_impact": 0.15,
    "freshness": 0.10,
    "infrastructure": 0.05,
}

# Set of hazard labels that represent a "road is clear / passable" report.
CLEAR_MARKERS = {"CLEAR", "ROAD_CLEAR", "NONE", "SAFE", "PASSABLE"}
