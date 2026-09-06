# ResQDrive — Cooperative Vehicle-Based Disaster Intelligence Network

> **Every vehicle becomes a sensor. Every road becomes intelligence.**
>
> Prototype for the **Smart India Hackathon**. All vehicle, sensor and hazard data is **SIMULATED / DEMO DATA** — no real cameras, GPS, OBD-II or edge devices are connected.

ResQDrive turns participating vehicles into a cooperative mobile sensing network. Vehicles observe roads (camera / GPS / IMU / OBD), AI detects hazards, and the platform fuses **independent observations from many vehicles** into a **continuously updated, confidence-aware road-risk map** that powers **safe routing** and a **prioritised emergency-response dashboard**.

The differentiating idea is **not** "AI detects floods" — it is **cooperative, confidence-aware, multi-vehicle evidence fusion**:

```
Vehicle → Sense → AI Detect → GPS/Time → Evidence Fusion → Confidence/Freshness
        → Road Risk → Live Map → Safe Route → Emergency Response
```

---

## What is built

- **Live, WebSocket-driven Command Center** (map-first) with KPIs derived from real backend state.
- **Interactive Leaflet map** (OpenStreetMap, no API key) with risk-coloured road segments, moving vehicle markers, hazard incidents, safe-route polylines and infrastructure.
- **Evidence Fusion Engine** — the core innovation (real backend logic, not UI numbers).
- **Risk Engine**, **Freshness decay**, **Risk-aware Route Planner** (Dijkstra).
- **Simulation Engine** with a deterministic, repeatable **Cyclone + Urban Flood** scenario and **manual hazard injection**.
- **Emergency Response** dashboard with P1–P4 prioritisation and Acknowledge / Dispatch / Monitor / Resolve actions.
- **Citizen view** with safe routing + citizen hazard reporting (enters the same fusion pipeline at lower reliability).
- **System Architecture**, **Technology** and **About** pages with honest prototype disclaimers.

---

## How to run

Services are managed by **supervisor** (already running in this environment).

```bash
# Backend (FastAPI, port 8001)
sudo supervisorctl restart backend

# Frontend (React, port 3000)
sudo supervisorctl restart frontend

# Core algorithm POC (runs in isolation, no server needed)
cd /app/backend && python test_core.py     # -> 33/33 PASS
```

- Frontend calls the backend via `REACT_APP_BACKEND_URL` with an `/api` prefix.
- Real-time updates use a WebSocket at `/api/ws`.
- MongoDB connection is provided via `MONGO_URL` / `DB_NAME`.

**Demo flow (30-second judge story):** open **Command Center → Start** (or **Simulation → Launch Disaster Simulation**). Watch: one vehicle detects flood → a second corroborates → confidence rises → the road turns **UNSAFE** → a **safe route** is generated → the **Response** dashboard receives a **P1** alert → later a vehicle reports the road clear → confidence decays → road returns to **SAFE**.

---

## Architecture

```
frontend/  React + Tailwind + shadcn/ui + Leaflet + Recharts + WebSocket client
backend/
  server.py          FastAPI routes + WebSocket + MongoDB persistence + lifecycle
  world.py           In-memory World: Hyderabad road graph, fleet, infrastructure, incidents
  simulation.py      Simulation Engine: vehicle movement, ambient + scripted observations
  ws_manager.py      WebSocket connection manager / broadcaster
  models.py          Pydantic request models
  engines/
    fusion.py        Evidence Fusion Engine (CORE)
    risk.py          Risk + response-priority scoring
    freshness.py     Exponential temporal freshness decay
    routing.py       Risk-aware Dijkstra route planner (RoadGraph)
    ai_detection.py  Simulated AI detection abstraction (swap-in point for real YOLO)
    reliability.py   All tunable prototype parameters (sensor weights, thresholds, decay)
  test_core.py       Isolated POC test suite for the engines
```

The in-memory `World` is the runtime source of truth for the live simulation; a snapshot is persisted to MongoDB (`world_state`), and events / response actions / citizen reports are written to their own collections.

---

## Evidence Fusion (the core innovation)

Given a spatial cluster of observations for the same road, fusion computes a single confidence-aware assessment (`engines/fusion.py`):

1. **Weighted base confidence** of supporting observations — weighted by `sensor_reliability × freshness_weight` (not a simple average).
2. **Independence-driven corroboration boost** toward (but never reaching) certainty:
   `strength = k · (independent_vehicles − 1) · spatial_spread`, `boost = 1 − e^(−strength)`.
   → 1 vehicle ≈ 82%, 2 ≈ 89%, 3 ≈ 93%, 4+ approaches 97–99%.
3. **Conflict penalty** — contradictory "road clear" / disagreeing reports lower the fused confidence via an agreement ratio.
4. **Verification state**: `UNVERIFIED → CORROBORATED → VERIFIED`, plus `CONFLICTING` and `STALE`.
5. An explainable **"Why is confidence X%?"** additive breakdown (AI detection / vehicle corroboration / sensor corroboration / freshness / sensor reliability).

## Freshness

`freshness_weight = exp(−age_minutes / decay_constant)` with buckets Very Fresh → Fresh → Aging → Stale → Expired. Old incidents decay and can become `STALE`; a fresh observation restores confidence.

## Risk Engine

`risk = 0.35·severity + 0.25·confidence + 0.15·freshness + 0.20·agreement + 0.05·sensor_reliability` (0–100), classified `SAFE / CAUTION / UNSAFE`. Response priority additionally weights road importance and proximity to critical infrastructure → `P1–P4`.

## Routing

`RoadGraph` (intersections = nodes, segments = edges). `edge_cost = base_time + risk_penalty(risk)` where `risk > 80` is heavily penalised and `risk > 50` moderately. Dijkstra computes both the **fastest** and the **risk-aware safe** route and reports the **avoided** unsafe segments.

---

## Configurable prototype parameters

All tunable values (sensor reliability weights, freshness decay constant, corroboration strength, verification thresholds, risk/priority weights, cluster radius) live in **`engines/reliability.py`**. They are **illustrative prototype parameters**, not scientifically validated constants.

---

## Future production integration (clean extension points)

- Replace `engines/ai_detection.py` with real **YOLO / PyTorch** edge inference.
- Real **smartphone / Raspberry Pi / Jetson** edge nodes streaming over **MQTT / WebSocket / HTTPS**.
- **OBD-II** telemetry, live **traffic / weather** feeds, satellite imagery, official disaster feeds.
- Migrate the geospatial abstraction to **PostgreSQL + PostGIS**; add **OSRM / GraphHopper** routing.
- Federated learning and V2X communication.

---

## Honest prototype notice

This is a **prototype**. It does **not** claim production readiness, real-world accuracy, or live deployment. Confidence values are illustrative. Everything is labelled **SIMULATED / DEMO DATA** across the UI.
