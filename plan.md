# plan.md — ResQDrive (FARM) Development Plan

## 1) Objectives
- Deliver a **live, judge-demo-ready** prototype proving the end-to-end pipeline: **Simulated Vehicle → Observation → AI Hazard Detection (sim) → GPS/Time → Evidence Fusion → Confidence/Freshness → Road Risk → Live Map → Safe Route → Emergency Alert**.
- Implement **real backend logic** for multi-vehicle, confidence-aware **evidence fusion** (agreement boosts, conflicts reduce, freshness decays) and **risk-aware routing** on a Hyderabad road graph.
- Provide a **WebSocket-updated** Command Center (map + KPIs + feed) and role-based UI via **in-app role switcher** (no login).
- Ensure all metrics are **derived from backend state**; seed data so it looks alive on launch; label everything **SIMULATED/DEMO**.

## 2) Implementation Steps

### Phase 1 — Core POC (Isolation, must pass before app)
**Goal:** Prove fusion + freshness + risk + routing with deterministic tests.

User stories:
1. As an operator, I want 2–3 vehicles corroborating the same hazard to **increase confidence** visibly.
2. As an operator, I want a **road clear** report to **reduce confidence** and possibly mark incident **CONFLICTING/CAUTION**.
3. As an analyst, I want **stale** observations to decay so old incidents stop dominating risk.
4. As a driver, I want routing to **avoid risk>80** segments even if the route is longer.
5. As a judge, I want a deterministic “Cyclone + Urban Flood” script that repeats identically each run.

Steps:
1. **Web search (best practices)**: quick research on evidence aggregation / freshness decay patterns and risk-aware routing cost functions (no external services).
2. Implement `test_core.py` + core modules:
   - `fusion_engine.py`: spatial clustering (radius), independence weighting (vehicle uniqueness + spatial spread), conflict handling, verification states.
   - `freshness.py`: exponential decay + freshness buckets.
   - `risk_engine.py`: compute components + overall risk (0–100) using provided weights.
   - `route_engine.py`: Dijkstra/A* on small Hyderabad road graph with risk penalties.
3. Deterministic fixtures: 1→~82%, 2→~89%, 3→~94%, 4+→97–99 confidence behavior; conflict case; stale decay case; route avoidance case.
4. Run until green; tune parameters (reliability weights, decay constant, independence factor) until tests consistently pass.

Deliverable: passing POC script proving core innovation without UI.

### Phase 2 — V1 App Development (Full stack MVP around proven core)
**Goal:** Working end-to-end system with real-time simulation + dashboards.

User stories:
1. As a judge, I want to click **Launch Demo** and immediately see vehicles moving and hazards forming on the map.
2. As an operator, I want the **Command Center KPIs** to change as incidents appear/resolve.
3. As an authority, I want verified incidents to appear with **priority** and allow **ack/dispatch/resolve**.
4. As a citizen, I want a **safe route** that avoids verified flood segments with a clear explanation.
5. As a demo operator, I want manual buttons to inject **Flood/Landslide/Blockage/Tree/Pothole/Conflict/Road Clear** and see fusion update live.

Backend (FastAPI + MongoDB + WebSockets):
1. Data models + collections: vehicles, observations, incidents, roadSegments, infrastructure, routes, responseActions, simulationState, events.
2. Services:
   - `simulation_engine.py`: vehicle movement on road graph; offline buffering; deterministic scenario timeline.
   - `ai_detection_service.py` (sim): returns hazard/confidence/severity/latency/bbox metadata.
   - reuse POC `fusion_engine`, `risk_engine`, `route_engine`.
3. API routes:
   - Dashboard summary, vehicles list/detail, incidents list/detail, roads risk overlay, route planning, response actions, simulation controls, manual inject endpoints.
4. WebSockets:
   - Single event stream channel broadcasting diffs: vehicle updates, incident updates, road risk updates, events/feed, alerts.
5. Seed data (Hyderabad): 50+ vehicles, 30+ road segments, infra points (hospitals/fire/police/shelters), 10+ initial incidents with mixed states.

Frontend (React + TS + Tailwind + Leaflet):
1. Global shell: top nav (Overview/Live Map/Vehicles/Hazards/Routes/Response/Simulation/System), top-right status bar (WS connected, sim status, time), **role switcher**.
2. Core pages (all functional):
   - **Landing** (Launch Demo / Explore Live Map / View Architecture)
   - **Command Center (Overview)**: big map + KPIs + live feed + alerts
   - **Live Map**: full-screen map with filters + incident detail drawer
   - **Vehicles**: fleet table + vehicle detail drawer
   - **Hazards**: incident list + verification/conflict/freshness + evidence timeline
   - **Routes**: start/destination → fastest vs safe route; show avoided segments
   - **Response**: priority table + actions (ack/dispatch/resolve)
   - **Simulation**: start/pause/reset, speed, scenario select, manual inject panel
   - **System/Technology/About**: architecture diagram + prototype disclaimers
3. Map overlays:
   - road segments colored by risk state; incident markers; moving vehicle markers; route polyline.
4. UI explainability blocks:
   - “Why confidence is X%” and “Evidence count/agreement/conflict/freshness”.
5. WebSocket client:
   - single store (e.g., Zustand/Redux-light) applying server events to UI state; graceful degraded mode.

Conclude Phase 2: Run 1 end-to-end test pass with the deterministic cyclone+flood scenario (start → verify → unsafe road → safe route changes → authority alert → clear → risk drops).

### Phase 3 — Stabilization + Feature Completeness (no placeholders)
User stories:
1. As a demo operator, I want a **Reset** that restores the exact initial seeded world.
2. As an authority, I want to filter incidents by **verification state** and **priority**.
3. As an operator, I want the live feed to show fusion steps (82→94) clearly.
4. As a citizen, I want to submit a **manual report** that enters the same fusion pipeline.
5. As a judge, I want obvious **SIMULATED/DEMO** labeling across UI and data panels.

Steps:
1. Add citizen reporting (lower reliability) + conflict scenarios.
2. Add incident confidence timeline + evidence graph (lightweight UI).
3. Add analytics charts (hazards by type, verified vs unverified, risk distribution) backed by API.
4. Improve resilience: empty states, reconnect logic, map tile failure fallback, sim pause handling.
5. Testing agent run + fix integration/perf issues (throttle marker updates, avoid leaks).

### Phase 4 — Optional polish (only if time)
User stories:
1. As a judge, I want the “30-second innovation story” to be visually unmistakable.
2. As an operator, I want keyboard-friendly controls in Simulation panel.
3. As an authority, I want printable incident summary for briefing.
4. As a citizen, I want a quick “near me” hazards view.
5. As an admin, I want a config panel for reliability/decay/risk thresholds.

Steps:
- Microinteractions, improved iconography, minor UX refinements; keep performance stable.

## 3) Status — Phase 1 & Phase 2 COMPLETE
- **Phase 1 POC**: `engines/` (fusion, risk, freshness, routing) + `test_core.py` — **33/33 PASS** in isolation.
- **Phase 2 Backend**: FastAPI + MongoDB + WebSocket broadcaster, `world.py` (Hyderabad graph, 60 vehicles, 11 infra, 12 seeded incidents with all verification states), `simulation.py` (movement + ambient corroboration + deterministic Cyclone+Flood script + manual injects + edge buffering), all `/api` routes + response actions + citizen reporting + analytics.
- **Phase 2 Frontend**: dark command-center design system, WebSocket live store, 12 pages (Landing, Command Center, Live Map, Vehicles, Hazards, Routes, Response, Simulation, System, Technology, About, Citizen), Leaflet map (OSM dark tiles, no key), reusable components (RiskBadge, VerificationBadge, ConfidenceRing/Breakdown, KpiCard, LiveEventFeed, MapView, IncidentDrawer, SimulationControls).
- **Testing**: `testing_agent_v3` — Backend 23/23 (100%), Frontend 100%, no bugs. README.md written.

## 3b) Next Actions (immediate)
1. (DONE) Phase 1 POC engines + `test_core.py` green.
2. (DONE) Hyderabad road graph + deterministic Cyclone+Urban Flood scenario.
3. (DONE) FastAPI app with WebSocket broadcaster + MongoDB persistence + seed.
4. (DONE) React app with Leaflet map + WS client + all pages.

## 4) Success Criteria
- **POC**: deterministic tests pass for corroboration, conflict, freshness decay, risk scoring, and route avoidance.
- **Live demo**: one vehicle detects → second corroborates → confidence rises → road turns UNSAFE → safe route changes → authority dashboard shows P1 alert (all in real time via WebSocket).
- **No hardcoded KPIs**: dashboard numbers match backend state; simulation changes propagate everywhere.
- **Manual inject controls** work and visibly affect fusion/risk/routing.
- **Clear disclaimers**: SIMULATED/DEMO labels; no paid APIs; no false claims.
