"""Temporal freshness model.

Disaster road conditions change rapidly, so evidence must decay with time.
We use a simple exponential decay:  weight = exp(-age_minutes / decay_const).
Newer observations restore confidence because they have weight close to 1.
"""
import math
from datetime import datetime, timezone

from .reliability import FRESHNESS_DECAY_MIN


def age_minutes(timestamp, now=None):
    """Return age of a timestamp (datetime) in minutes, clamped at >= 0."""
    if now is None:
        now = datetime.now(timezone.utc)
    if timestamp is None:
        return 0.0
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    delta = (now - timestamp).total_seconds() / 60.0
    return max(0.0, delta)


def freshness_weight(age_min, decay_constant=FRESHNESS_DECAY_MIN):
    """Exponential freshness weight in (0, 1]. age 0 -> 1.0."""
    return math.exp(-max(0.0, float(age_min)) / decay_constant)


def freshness_score(age_min, decay_constant=FRESHNESS_DECAY_MIN):
    """Freshness as an integer 0-100 for UI display."""
    return round(freshness_weight(age_min, decay_constant) * 100)


def freshness_bucket(age_min):
    """Human-readable freshness bucket."""
    a = max(0.0, float(age_min))
    if a < 5:
        return "VERY_FRESH"
    if a < 15:
        return "FRESH"
    if a < 30:
        return "AGING"
    if a < 60:
        return "STALE"
    return "EXPIRED"
