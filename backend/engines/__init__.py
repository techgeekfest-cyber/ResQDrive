"""ResQDrive core intelligence engines.

These modules implement the make-or-break backend logic of the ResQDrive
cooperative vehicle sensing network:

- freshness      : temporal decay of observations
- fusion         : multi-vehicle, confidence-aware evidence fusion (CORE)
- risk           : road-risk scoring model
- routing        : risk-aware graph route planner (Dijkstra)
- reliability    : configurable prototype parameters
- geo            : geospatial helpers

All numeric parameters are ILLUSTRATIVE PROTOTYPE VALUES, not scientifically
validated constants. They are centralised in ``reliability.py`` so they can be
tuned or later replaced with learned/calibrated values.
"""
