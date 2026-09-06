"""Road-risk scoring model.

risk = 0.35*severity + 0.25*confidence + 0.15*freshness
       + 0.20*agreement + 0.05*sensor_reliability   (all inputs 0-1)
normalised to 0-100.

Also provides response-priority scoring and risk-state classification.
"""
from .reliability import (
    PRIORITY_WEIGHTS,
    RISK_CAUTION,
    RISK_UNSAFE,
    RISK_WEIGHTS,
    SEVERITY_SCORE,
)


def severity_to_score(severity):
    return SEVERITY_SCORE.get(str(severity or "MODERATE").upper(), 0.60)


def compute_risk(severity, confidence, freshness, agreement, sensor_reliability):
    """Compute an overall 0-100 risk score from normalised (0-1) components.

    ``severity`` may be a label (LOW/MODERATE/HIGH/CRITICAL) or a 0-1 float.
    """
    if isinstance(severity, str):
        sev = severity_to_score(severity)
    else:
        sev = max(0.0, min(1.0, float(severity)))
    w = RISK_WEIGHTS
    r = (w["severity"] * sev
         + w["confidence"] * _c(confidence)
         + w["freshness"] * _c(freshness)
         + w["agreement"] * _c(agreement)
         + w["sensor_reliability"] * _c(sensor_reliability))
    return round(r * 100)


def risk_components(severity, confidence, freshness, agreement, sensor_reliability):
    """Return each weighted component contribution (0-100) plus the total."""
    if isinstance(severity, str):
        sev = severity_to_score(severity)
    else:
        sev = max(0.0, min(1.0, float(severity)))
    w = RISK_WEIGHTS
    comps = {
        "severity": round(w["severity"] * sev * 100),
        "confidence": round(w["confidence"] * _c(confidence) * 100),
        "freshness": round(w["freshness"] * _c(freshness) * 100),
        "agreement": round(w["agreement"] * _c(agreement) * 100),
        "sensor_reliability": round(w["sensor_reliability"] * _c(sensor_reliability) * 100),
    }
    comps["total"] = compute_risk(severity, confidence, freshness, agreement,
                                  sensor_reliability)
    return comps


def risk_state(risk):
    """Classify a 0-100 risk score into SAFE / CAUTION / UNSAFE."""
    if risk >= RISK_UNSAFE:
        return "UNSAFE"
    if risk >= RISK_CAUTION:
        return "CAUTION"
    return "SAFE"


def confidence_band(confidence_pct):
    """Map a 0-100 confidence into a qualitative band."""
    c = confidence_pct
    if c >= 90:
        return "VERY_HIGH"
    if c >= 70:
        return "HIGH"
    if c >= 40:
        return "MODERATE"
    return "LOW"


def compute_priority(risk, severity, traffic_impact, freshness, infrastructure):
    """Compute a 0-100 response-priority score and P1-P4 level.

    All inputs 0-1 except ``risk`` which is 0-100, and ``severity`` which may be
    a label or 0-1 float.
    """
    if isinstance(severity, str):
        sev = severity_to_score(severity)
    else:
        sev = max(0.0, min(1.0, float(severity)))
    w = PRIORITY_WEIGHTS
    score = (w["risk"] * (risk / 100.0)
             + w["severity"] * sev
             + w["traffic_impact"] * _c(traffic_impact)
             + w["freshness"] * _c(freshness)
             + w["infrastructure"] * _c(infrastructure))
    score100 = round(score * 100)
    if score100 >= 80:
        level = "P1"
    elif score100 >= 60:
        level = "P2"
    elif score100 >= 40:
        level = "P3"
    else:
        level = "P4"
    return {"score": score100, "level": level}


def _c(x):
    try:
        return max(0.0, min(1.0, float(x)))
    except (TypeError, ValueError):
        return 0.0
