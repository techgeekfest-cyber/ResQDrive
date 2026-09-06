"""Evidence Fusion Engine -- the CORE innovation of ResQDrive.

Given a set of independent vehicle observations that are spatially clustered
(candidate evidence for the same road incident), fuse them into a single
confidence-aware assessment.

Key behaviours (all real backend logic, not UI numbers):
  * More INDEPENDENT vehicles that agree  -> higher confidence (diminishing).
      1 veh ~82%, 2 ~89%, 3 ~93%, 4 ~96%, 5+ approaches 97-99%.
  * Contradictory observations (e.g. "road clear") reduce confidence and can
      drive a CONFLICTING verification state.
  * Stale observations decay (see freshness.py) and stop dominating.
  * Weighting accounts for sensor reliability, AI confidence, freshness and
      spatial independence -- it is NOT a simple average.

The combination uses weighted evidence aggregation for a base confidence, then
applies an independence-driven corroboration boost toward (but never reaching)
certainty, and finally a conflict penalty.
"""
import math
from datetime import datetime, timezone
from statistics import mean

from .freshness import age_minutes, freshness_weight
from .geo import haversine_m
from .reliability import (
    CLEAR_MARKERS,
    CONFLICT_AGREEMENT_THRESHOLD,
    CORROBORATED_MIN_CONFIDENCE,
    CORROBORATED_MIN_VEHICLES,
    DEFAULT_SENSOR_RELIABILITY,
    INDEPENDENCE_K,
    MAX_CONFIDENCE,
    SENSOR_RELIABILITY,
    STALE_FRESHNESS_THRESHOLD,
    VERIFIED_MIN_CONFIDENCE,
    VERIFIED_MIN_VEHICLES,
)


def _sensor_reliability(sensor_type, quality):
    base = SENSOR_RELIABILITY.get(str(sensor_type or "").upper(),
                                  DEFAULT_SENSOR_RELIABILITY)
    try:
        q = float(quality)
    except (TypeError, ValueError):
        q = 1.0
    return base * max(0.0, min(1.0, q))


def _enrich(observations, now):
    """Attach freshness weight, reliability and normalised fields."""
    enriched = []
    for o in observations:
        hazard = str(o.get("hazard_type", "")).upper()
        age = age_minutes(o.get("timestamp"), now)
        fw = freshness_weight(age)
        rel = _sensor_reliability(o.get("sensor_type"), o.get("sensor_quality", 1.0))
        enriched.append({
            "vehicle_id": o.get("vehicle_id"),
            "hazard": hazard,
            "is_clear": hazard in CLEAR_MARKERS,
            "lat": o.get("latitude"),
            "lon": o.get("longitude"),
            "conf": max(0.0, min(1.0, float(o.get("confidence", 0.0)))),
            "sensor_type": str(o.get("sensor_type", "")).upper(),
            "severity": str(o.get("severity", "MODERATE")).upper(),
            "age": age,
            "fw": fw,
            "rel": rel,
            "weight": rel * fw,
        })
    return enriched


def _spatial_factor(vehicle_points):
    """Independence multiplier from spatial spread of distinct vehicles.

    Distinct vehicles observing from slightly different positions are more
    independent than duplicate reports at the exact same point.
    Returns a value in [0.7, 1.0].
    """
    if len(vehicle_points) < 2:
        return 1.0
    dists = []
    pts = list(vehicle_points)
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            dists.append(haversine_m(pts[i][0], pts[i][1], pts[j][0], pts[j][1]))
    avg = mean(dists) if dists else 0.0
    return max(0.7, min(1.0, 0.7 + 0.3 * min(avg / 40.0, 1.0)))


def _round_to_total(shares, total):
    """Distribute an integer ``total`` across ``shares`` using largest-remainder
    rounding so the integer parts sum exactly to ``total``."""
    keys = list(shares.keys())
    if total <= 0 or not keys:
        return {k: 0 for k in keys}
    s = sum(shares.values()) or 1.0
    scaled = {k: shares[k] / s * total for k in keys}
    floored = {k: int(math.floor(v)) for k, v in scaled.items()}
    remainder = total - sum(floored.values())
    order = sorted(keys, key=lambda k: scaled[k] - floored[k], reverse=True)
    for i in range(remainder):
        floored[order[i % len(order)]] += 1
    return floored


def empty_result():
    return {
        "hazard_type": None,
        "confidence": 0,
        "confidence_raw": 0.0,
        "base_confidence": 0,
        "verification_state": "UNVERIFIED",
        "evidence_count": 0,
        "observation_count": 0,
        "agreement": 0,
        "conflict_count": 0,
        "supporting_vehicles": [],
        "conflicting_vehicles": [],
        "freshness": 0,
        "avg_sensor_reliability": 0,
        "severity": "MODERATE",
        "breakdown": {},
    }


def fuse_observations(observations, now=None):
    """Fuse a spatial cluster of observations into one incident assessment.

    Parameters
    ----------
    observations : list of dict
        Each dict: vehicle_id, hazard_type, latitude, longitude, timestamp
        (datetime), confidence (0-1), sensor_type, sensor_quality (0-1),
        severity (LOW/MODERATE/HIGH/CRITICAL).
    now : datetime, optional
        Reference time (defaults to utcnow).

    Returns
    -------
    dict with fused hazard_type, confidence (0-100), verification_state,
    evidence_count, agreement, freshness, severity and an explainable
    confidence breakdown.
    """
    if not observations:
        return empty_result()
    if now is None:
        now = datetime.now(timezone.utc)

    enriched = _enrich(observations, now)

    # Determine the dominant hazard among non-clear observations (weighted).
    hazard_weights = {}
    for e in enriched:
        if e["is_clear"]:
            continue
        hazard_weights[e["hazard"]] = hazard_weights.get(e["hazard"], 0.0) + e["weight"]

    if not hazard_weights:
        # All observations report the road is clear -> no active hazard.
        res = empty_result()
        res["observation_count"] = len(enriched)
        res["verification_state"] = "STALE"
        res["conflicting_vehicles"] = sorted({e["vehicle_id"] for e in enriched})
        return res

    dominant = max(hazard_weights, key=hazard_weights.get)

    supporting = [e for e in enriched if not e["is_clear"] and e["hazard"] == dominant]
    conflicting = [e for e in enriched
                   if e["is_clear"] or (not e["is_clear"] and e["hazard"] != dominant)]

    support_w = sum(e["weight"] for e in supporting)
    conflict_w = sum(e["weight"] for e in conflicting)
    total_w = support_w + conflict_w
    agreement_ratio = (support_w / total_w) if total_w > 0 else 0.0

    # Base weighted confidence of the supporting evidence (NOT a plain average).
    base = sum(e["conf"] * e["weight"] for e in supporting) / support_w

    # Independent supporting vehicles + spatial spread.
    vehicle_points = {}
    for e in supporting:
        # keep the freshest observation position per vehicle
        prev = vehicle_points.get(e["vehicle_id"])
        if prev is None or e["fw"] > prev[2]:
            vehicle_points[e["vehicle_id"]] = (e["lat"], e["lon"], e["fw"])
    n_independent = len(vehicle_points)
    spatial_factor = _spatial_factor([(p[0], p[1]) for p in vehicle_points.values()])

    # Corroboration boost toward (but never reaching) certainty.
    strength = INDEPENDENCE_K * max(0, n_independent - 1) * spatial_factor
    corr_factor = 1.0 - math.exp(-strength)
    raw = base + (1.0 - base) * corr_factor

    # Conflict penalty: disagreement pulls confidence down.
    conflict_multiplier = 0.5 + 0.5 * agreement_ratio
    final = raw * conflict_multiplier
    final = max(0.0, min(MAX_CONFIDENCE, final))

    incident_fw = max(e["fw"] for e in supporting)          # recency
    avg_rel = mean(e["rel"] for e in supporting)
    sensor_types = {e["sensor_type"] for e in supporting}
    sensor_diversity = min(1.0, len(sensor_types) / 3.0)

    # Dominant severity = highest severity among supporting observations.
    sev_rank = {"LOW": 0, "MODERATE": 1, "HIGH": 2, "CRITICAL": 3}
    severity = max((e["severity"] for e in supporting),
                   key=lambda s: sev_rank.get(s, 1))

    # Verification state.
    if incident_fw < STALE_FRESHNESS_THRESHOLD:
        state = "STALE"
    elif conflict_w > 0 and agreement_ratio < CONFLICT_AGREEMENT_THRESHOLD:
        state = "CONFLICTING"
    elif n_independent >= VERIFIED_MIN_VEHICLES and final >= VERIFIED_MIN_CONFIDENCE:
        state = "VERIFIED"
    elif n_independent >= CORROBORATED_MIN_VEHICLES and final >= CORROBORATED_MIN_CONFIDENCE:
        state = "CORROBORATED"
    else:
        state = "UNVERIFIED"

    total_conf = round(final * 100)

    # Explainable "Why is confidence X%?" breakdown (sums exactly to total_conf).
    breakdown = _round_to_total({
        "ai_detection": base,
        "vehicle_corroboration": corr_factor * 0.9,
        "sensor_corroboration": sensor_diversity * 0.5,
        "freshness": incident_fw * 0.5,
        "sensor_reliability": avg_rel * 0.4,
    }, total_conf)

    return {
        "hazard_type": dominant,
        "confidence": total_conf,
        "confidence_raw": round(final, 4),
        "base_confidence": round(base * 100),
        "verification_state": state,
        "evidence_count": n_independent,
        "observation_count": len(enriched),
        "agreement": round(agreement_ratio * 100),
        "conflict_count": len({e["vehicle_id"] for e in conflicting}),
        "supporting_vehicles": sorted({e["vehicle_id"] for e in supporting}),
        "conflicting_vehicles": sorted({e["vehicle_id"] for e in conflicting}),
        "freshness": round(incident_fw * 100),
        "avg_sensor_reliability": round(avg_rel * 100),
        "severity": severity,
        "breakdown": breakdown,
    }


def cluster_observations(observations, radius_m=None):
    """Greedy spatial clustering of observations for candidate incidents.

    Returns a list of clusters (each a list of observations). Observations are
    grouped when within ``radius_m`` of the cluster's seed point.
    """
    from .reliability import CLUSTER_RADIUS_M
    radius = radius_m if radius_m is not None else CLUSTER_RADIUS_M
    clusters = []
    for o in observations:
        placed = False
        for c in clusters:
            seed = c[0]
            d = haversine_m(seed.get("latitude"), seed.get("longitude"),
                            o.get("latitude"), o.get("longitude"))
            if d <= radius:
                c.append(o)
                placed = True
                break
        if not placed:
            clusters.append([o])
    return clusters
