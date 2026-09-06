"""Simulated AI Detection Service.

In the prototype we do NOT run real YOLO/PyTorch inference. This service is a
clean abstraction that returns the SAME shape a real edge inference pipeline
would (hazard_type, confidence, bounding_box, severity, latency, model,
device), so it can later be swapped for genuine on-device inference.

Everything returned here is SIMULATED / DEMO data.
"""
import random

# Canonical hazard catalogue.
HAZARD_TYPES = [
    "FLOOD", "WATERLOGGING", "LANDSLIDE", "DEBRIS", "FALLEN_TREE",
    "POTHOLE", "ROAD_DAMAGE", "ACCIDENT", "ROAD_BLOCKAGE", "CONSTRUCTION",
]

# Default severity per hazard type.
HAZARD_SEVERITY = {
    "FLOOD": "HIGH",
    "WATERLOGGING": "MODERATE",
    "LANDSLIDE": "CRITICAL",
    "DEBRIS": "MODERATE",
    "FALLEN_TREE": "HIGH",
    "POTHOLE": "LOW",
    "ROAD_DAMAGE": "MODERATE",
    "ACCIDENT": "HIGH",
    "ROAD_BLOCKAGE": "HIGH",
    "CONSTRUCTION": "LOW",
}

HAZARD_LABEL = {
    "FLOOD": "Flood Water",
    "WATERLOGGING": "Waterlogging",
    "LANDSLIDE": "Landslide",
    "DEBRIS": "Road Debris",
    "FALLEN_TREE": "Fallen Tree",
    "POTHOLE": "Pothole Cluster",
    "ROAD_DAMAGE": "Damaged Road",
    "ACCIDENT": "Vehicle Accident",
    "ROAD_BLOCKAGE": "Road Blockage",
    "CONSTRUCTION": "Construction Obstacle",
    "CLEAR": "Road Clear",
}

# Plausible confidence ranges per sensor source.
_SENSOR_CONF = {
    "CAMERA": (0.80, 0.96),
    "IMU": (0.64, 0.82),
    "ACCELEROMETER": (0.62, 0.80),
    "OBD": (0.68, 0.85),
    "CITIZEN": (0.45, 0.72),
}

MODEL_NAME = "ResQDrive Vision v1 (SIMULATED)"


def severity_for(hazard_type):
    return HAZARD_SEVERITY.get(str(hazard_type).upper(), "MODERATE")


def label_for(hazard_type):
    return HAZARD_LABEL.get(str(hazard_type).upper(), str(hazard_type).title())


def detect(hazard_type, sensor_type="CAMERA", device="Edge Node", rng=None,
           confidence=None):
    """Return a simulated detection result for a given hazard + sensor.

    Parameters
    ----------
    hazard_type : str  (a HAZARD_TYPES value, or 'CLEAR' for a passable report)
    sensor_type : str  (CAMERA / IMU / ACCELEROMETER / OBD / CITIZEN)
    device      : str  (edge device label for display)
    rng         : random.Random, optional (for deterministic scenarios)
    confidence  : float, optional (force a specific confidence 0-1)
    """
    r = rng or random
    st = str(sensor_type).upper()
    lo, hi = _SENSOR_CONF.get(st, (0.60, 0.85))
    conf = confidence if confidence is not None else round(r.uniform(lo, hi), 3)

    x = round(r.uniform(0.08, 0.55), 3)
    y = round(r.uniform(0.35, 0.75), 3)
    w = round(r.uniform(0.25, 0.6), 3)
    h = round(r.uniform(0.15, 0.45), 3)

    return {
        "hazard_type": str(hazard_type).upper(),
        "label": label_for(hazard_type),
        "confidence": conf,
        "severity": severity_for(hazard_type) if hazard_type != "CLEAR" else "LOW",
        "bounding_box": {"x": x, "y": y, "w": w, "h": h},
        "bounding_region": "Road surface",
        "latency_ms": r.randint(46, 118),
        "model": MODEL_NAME,
        "device": device,
        "sensor_type": st,
    }
