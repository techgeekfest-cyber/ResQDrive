"""ResQDrive Simulation Engine.

Drives the live cooperative-sensing simulation:
  * moves vehicles along the road graph,
  * generates sensor observations (ambient + scripted),
  * feeds them through the Evidence Fusion Engine (via World.add_observation),
  * emits live intelligence events, and
  * broadcasts the updated world snapshot over WebSockets each tick.

It also runs a DETERMINISTIC, repeatable "Cyclone + Urban Flood" scenario and
supports manual hazard injection for controlled demos.

All data produced is SIMULATED / DEMO data.
"""
import asyncio
import logging

from engines import ai_detection
from engines.geo import haversine_m
from engines.routing import RISK_CAUTION

logger = logging.getLogger("resqdrive.sim")

TICK_INTERVAL_SEC = 2.0          # real seconds between ticks
SIM_MIN_PER_SPEED = 1.0          # sim minutes advanced per tick per speed unit
AMBIENT_CORROBORATE_PROB = 0.40  # chance a passing vehicle corroborates
AMBIENT_NEW_HAZARD_PROB = 0.14   # chance of a brand-new ambient hazard per tick
MAX_ACTIVE_INCIDENTS = 26

# Deterministic Cyclone + Urban Flood scenario.
# Flood forms live on RS-19 (Public Gardens Road) which starts SAFE and has
# alternative routes, so the judge can watch UNVERIFIED -> VERIFIED -> UNSAFE
# -> safe route -> P1 alert -> road clears -> SAFE.
FLOOD_EDGE = "RS-19"
CYCLONE_FLOOD_SCRIPT = [
    (1, "weather", None),
    (2, "report", ("RQ-101", "FLOOD", "CAMERA", 0.86)),
    (4, "report", ("RQ-104", "FLOOD", "CAMERA", 0.79)),
    (6, "report", ("RQ-109", "FLOOD", "CAMERA", 0.93)),
    (7, "sensor", ("RQ-112", "FLOOD", "IMU", 0.74)),
    (9, "route", None),
    (10, "alert", None),
    (24, "clear", ("RQ-131", 0.82)),
    (28, "clear", ("RQ-145", 0.85)),
    (33, "resolve", None),
]


class SimulationEngine:
    def __init__(self, world, manager, persist_cb=None):
        self.world = world
        self.manager = manager
        self.persist_cb = persist_cb
        self._task = None
        self._scenario_incident = None
        self._script_done = set()

    # -------------------------------------------------------------- controls
    async def start(self, scenario="CYCLONE_FLOOD", speed=2):
        w = self.world
        w.sim["scenario"] = scenario
        w.sim["speed"] = int(speed)
        if w.sim["status"] == "RUNNING":
            await self._broadcast()
            return
        w.sim["status"] = "RUNNING"
        if w.sim.get("scenario_started_tick") is None:
            w.sim["scenario_started_tick"] = w.sim["tick"]
            self._script_done = set()
            self._scenario_incident = None
        w._log_event("SYSTEM",
                     f"Simulation started — scenario {scenario.replace('_', ' ')} "
                     f"at {speed}x (SIMULATED).", "info")
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run())
        await self._broadcast()

    async def pause(self):
        w = self.world
        if w.sim["status"] == "RUNNING":
            w.sim["status"] = "PAUSED"
            w._log_event("SYSTEM", "Simulation paused.", "warning")
        await self._broadcast()

    async def reset(self):
        w = self.world
        w.sim["status"] = "STOPPED"
        if self._task and not self._task.done():
            self._task.cancel()
        self._task = None
        self._scenario_incident = None
        self._script_done = set()
        w.build()
        w.demo_route = None
        w._log_event("SYSTEM", "World reset to initial seeded state.", "info")
        if self.persist_cb:
            await self.persist_cb(w.snapshot())
        await self._broadcast()

    async def set_speed(self, speed):
        self.world.sim["speed"] = int(speed)
        await self._broadcast()

    # ------------------------------------------------------------- main loop
    async def _run(self):
        try:
            while self.world.sim["status"] == "RUNNING":
                await asyncio.sleep(TICK_INTERVAL_SEC)
                if self.world.sim["status"] != "RUNNING":
                    break
                try:
                    self._tick()
                except Exception:  # never let the loop die
                    logger.exception("tick error")
                await self._broadcast()
                if self.persist_cb and self.world.sim["tick"] % 4 == 0:
                    try:
                        await self.persist_cb(self.world.snapshot())
                    except Exception:
                        logger.exception("persist error")
        except asyncio.CancelledError:
            pass

    def _tick(self):
        from datetime import timedelta
        w = self.world
        w.sim["tick"] += 1
        sim_minutes = SIM_MIN_PER_SPEED * max(1, w.sim["speed"])
        w.sim_time = w.sim_time + timedelta(minutes=sim_minutes)

        self._move_vehicles(sim_minutes)
        self._refuse_all()          # freshness decay / state transitions
        self._run_scenario()
        self._ambient()

    # -------------------------------------------------------------- vehicles
    def _move_vehicles(self, sim_minutes):
        w, rng, g = self.world, self.world.rng, self.world.graph
        for v in w.vehicles.values():
            if v["status"] == "DISCONNECTED":
                v["buffered"] = min(v["buffered"] + rng.randint(0, 2), 40)
                if rng.random() < 0.06:   # reconnect + upload buffer
                    uploaded = v["buffered"]
                    v["buffered"] = 0
                    v["status"] = "ACTIVE"
                    v["network_quality"] = rng.choice(["GOOD", "FAIR"])
                    w.sim["observations_total"] += uploaded
                    w._log_event("VEHICLE",
                                 f"{v['id']} reconnected — {uploaded} buffered "
                                 f"edge observations uploaded.",
                                 "info", vehicle_id=v["id"])
                continue

            # occasionally drop offline (edge buffering demo)
            if rng.random() < 0.01:
                v["status"] = "DISCONNECTED"
                v["network_quality"] = "OFFLINE"
                w._log_event("VEHICLE",
                             f"{v['id']} network DEGRADED — buffering "
                             f"observations locally at the edge.",
                             "warning", vehicle_id=v["id"])
                continue

            e = g.edges[v["edge_id"]]
            length_km = max(0.05, e.get("length_km", 0.5))
            dpos = (v["speed"] * sim_minutes / 60.0) / length_km
            v["pos"] += dpos
            guard = 0
            while v["pos"] >= 1.0 and guard < 6:
                v["pos"] -= 1.0
                self._advance_edge(v)
                guard += 1
            v["pos"] = min(0.999, max(0.0, v["pos"]))
            w._place_vehicle(v)
            if v["status"] not in ("OBSERVING", "EMERGENCY"):
                v["status"] = rng.choice(
                    ["ACTIVE", "ACTIVE", "ACTIVE", "TRANSMITTING"])

    def _advance_edge(self, v):
        g, rng = self.world.graph, self.world.rng
        e = g.edges[v["edge_id"]]
        end_node = e["v"] if v["direction"] == 1 else e["u"]
        neighbors = g.adj[end_node]
        choices = [(nn, eid) for (nn, eid) in neighbors if eid != v["edge_id"]]
        if not choices:
            choices = list(neighbors)
        if not choices:
            v["direction"] *= -1
            return
        nn, neid = rng.choice(choices)
        ne = g.edges[neid]
        v["edge_id"] = neid
        v["direction"] = 1 if ne["u"] == end_node else -1
        v["speed"] = round(min(55, max(12, v["speed"] + rng.uniform(-6, 6))), 1)

    # ------------------------------------------------------------ fusion tick
    def _refuse_all(self):
        for inc in list(self.world.incidents.values()):
            if inc.get("response_status") == "RESOLVED":
                continue
            self.world.refuse_incident(inc)

    # --------------------------------------------------------------- ambient
    def _vehicles_on_edge(self, edge_id):
        return [v for v in self.world.vehicles.values()
                if v["edge_id"] == edge_id and v["status"] != "DISCONNECTED"
                and v["camera_status"] != "OFFLINE"]

    def _ambient(self):
        w, rng = self.world, self.world.rng

        # 1) Vehicles passing an active incident corroborate it.
        for inc in list(self.world.active_incidents()):
            if inc.get("clearing") or inc.get("hazard_type") in ("CLEAR",):
                continue
            eid = inc.get("road_segment_id")
            if not eid:
                continue
            passers = self._vehicles_on_edge(eid)
            if not passers or rng.random() > AMBIENT_CORROBORATE_PROB:
                continue
            v = rng.choice(passers)
            if v["id"] in inc.get("supporting_vehicles", []):
                continue  # already contributed
            sensor = rng.choice(["CAMERA", "CAMERA", "IMU"])
            obs = w._make_observation(
                v["id"], inc["hazard_type"], inc["latitude"], inc["longitude"],
                sensor, None, speed=v["speed"], heading=v["heading"])
            v["current_observation"] = obs["metadata"]["label"]
            v["observation_history"].append(self.world._serialize_obs(obs))
            _, is_new, prev_c, prev_s = w.add_observation(obs)
            self._log_fusion(inc, v["id"], sensor, obs["confidence"], prev_c,
                             prev_s, corroboration=True)

        # 2) Occasionally a brand-new ambient hazard appears.
        active_edges = {i.get("road_segment_id") for i in w.active_incidents()}
        if (len(w.active_incidents()) < MAX_ACTIVE_INCIDENTS
                and rng.random() < AMBIENT_NEW_HAZARD_PROB):
            from world import SCENARIO_HAZARDS
            free = [eid for eid in w.graph.edges if eid not in active_edges]
            if free:
                eid = rng.choice(free)
                haz = rng.choice(SCENARIO_HAZARDS.get(
                    w.sim["scenario"], SCENARIO_HAZARDS["MIXED"]))
                passers = self._vehicles_on_edge(eid)
                vid = passers[0]["id"] if passers else rng.choice(
                    list(w.vehicles.keys()))
                mlat, mlon = w.edge_midpoint(eid)
                obs = w._make_observation(vid, haz, mlat, mlon, "CAMERA", None)
                inc, is_new, _, _ = w.add_observation(obs)
                if inc and is_new:
                    w._log_event(
                        "DETECTION",
                        f"{vid} detected {ai_detection.label_for(haz)} on "
                        f"{inc['road_name']} — new candidate incident "
                        f"({inc['confidence']}% confidence).",
                        "warning", incident_id=inc["id"], vehicle_id=vid)

    def _log_fusion(self, inc, vid, sensor, conf, prev_c, prev_s,
                    corroboration=False):
        w = self.world
        state = inc.get("verification_status")
        det = f"{vid} {'IMU' if sensor == 'IMU' else 'camera'} evidence"
        if corroboration:
            w._log_event(
                "DETECTION",
                f"{det} corroborates {ai_detection.label_for(inc['hazard_type'])} "
                f"on {inc['road_name']}.",
                "info", incident_id=inc["id"], vehicle_id=vid)
        if prev_s and state != prev_s:
            level = "success" if state in ("VERIFIED", "CORROBORATED") else "warning"
            w._log_event(
                "FUSION",
                f"Evidence Fusion updated {inc['id']} — confidence "
                f"{prev_c}% -> {inc['confidence']}%, status {state} "
                f"({inc['evidence_count']} independent vehicles).",
                level, incident_id=inc["id"])
            if state == "VERIFIED" and inc["risk_state"] == "UNSAFE":
                w._log_event(
                    "ALERT",
                    f"{inc['road_name']} marked UNSAFE — verified "
                    f"{ai_detection.label_for(inc['hazard_type'])}, risk "
                    f"{inc['risk_score']}/100.",
                    "critical", incident_id=inc["id"])

    # -------------------------------------------------------------- scenario
    def _run_scenario(self):
        w = self.world
        if w.sim["scenario"] != "CYCLONE_FLOOD":
            return
        started = w.sim.get("scenario_started_tick")
        if started is None:
            return
        rel = w.sim["tick"] - started
        for step in CYCLONE_FLOOD_SCRIPT:
            offset, kind, payload = step
            if offset != rel or (offset, kind) in self._script_done:
                continue
            self._script_done.add((offset, kind))
            self._scenario_step(kind, payload)

    def _scenario_step(self, kind, payload):
        w = self.world
        mlat, mlon = w.edge_midpoint(FLOOD_EDGE)
        road_name = w.graph.edges[FLOOD_EDGE]["name"]

        if kind == "weather":
            w._log_event("SYSTEM",
                         "Cyclone warning — intense rainfall band over central "
                         "Hyderabad. Waterlogging likely (SIMULATED).",
                         "warning")
            return

        if kind in ("report", "sensor"):
            vid, haz, sensor, conf = payload
            v = w.vehicles.get(vid)
            if v:                      # drive the reporting vehicle to the scene
                v["latitude"] = round(mlat + w.rng.uniform(-0.0004, 0.0004), 6)
                v["longitude"] = round(mlon + w.rng.uniform(-0.0004, 0.0004), 6)
                v["edge_id"] = FLOOD_EDGE
                v["status"] = "OBSERVING"
                v["network_quality"] = ("GOOD" if v["network_quality"] == "OFFLINE"
                                        else v["network_quality"])
            obs = w._make_observation(vid, haz, mlat, mlon, sensor, conf,
                                      speed=(11 if kind == "sensor" else 18),
                                      heading=90)
            if v:
                v["current_observation"] = obs["metadata"]["label"]
                v["observation_history"].append(w._serialize_obs(obs))
            inc, is_new, prev_c, prev_s = w.add_observation(obs)
            self._scenario_incident = inc["id"]
            if kind == "sensor":
                w._log_event(
                    "DETECTION",
                    f"{vid} IMU reports abnormal vehicle motion + speed drop "
                    f"(42 -> 11 km/h) on {road_name} — sensor corroboration.",
                    "info", incident_id=inc["id"], vehicle_id=vid)
            else:
                w._log_event(
                    "DETECTION",
                    f"{vid} camera detected {ai_detection.label_for(haz)} on "
                    f"{road_name} ({obs['confidence']}% AI confidence).",
                    "warning", incident_id=inc["id"], vehicle_id=vid)
            if prev_s and prev_s != inc["verification_status"]:
                self._log_fusion(inc, vid, sensor, obs["confidence"], prev_c,
                                 prev_s)
            elif is_new:
                w._log_event("FUSION",
                             f"New incident {inc['id']} created — UNVERIFIED, "
                             f"{inc['confidence']}% confidence, awaiting "
                             f"corroboration.", "info", incident_id=inc["id"])
            return

        if kind == "route":
            self._suggest_demo_route()
            return

        if kind == "alert":
            inc = w.incidents.get(self._scenario_incident)
            if inc:
                w._log_event(
                    "ALERT",
                    f"P1 RESPONSE REQUIRED — verified flooding on {road_name} "
                    f"near emergency corridor. Risk {inc.get('risk_score', 0)}/100, "
                    f"{inc.get('evidence_count', 0)} independent vehicles.",
                    "critical", incident_id=inc["id"])
            return

        if kind == "clear":
            vid, conf = payload
            inc = w.incidents.get(self._scenario_incident)
            if not inc:
                return
            inc["clearing"] = True
            v = w.vehicles.get(vid)
            if v:
                v["latitude"] = round(mlat + w.rng.uniform(-0.0004, 0.0004), 6)
                v["longitude"] = round(mlon + w.rng.uniform(-0.0004, 0.0004), 6)
                v["edge_id"] = FLOOD_EDGE
                v["status"] = "OBSERVING"
                v["current_observation"] = "Road Clear"
            obs = w._make_observation(vid, "CLEAR", mlat, mlon, "CAMERA", conf,
                                      speed=34, heading=90)
            prev_c = inc.get("confidence", 0)
            w.add_observation(obs)
            w._log_event(
                "DETECTION",
                f"{vid} reports {road_name} now PASSABLE — water receding. "
                f"Confidence {prev_c}% -> {inc['confidence']}% "
                f"(status {inc['verification_status']}).",
                "info", incident_id=inc["id"], vehicle_id=vid)
            return

        if kind == "resolve":
            inc = w.incidents.get(self._scenario_incident)
            if inc and inc.get("response_status") != "RESOLVED":
                w._resolve_incident(inc)
            self._suggest_demo_route()
            return

    def _suggest_demo_route(self):
        """Compute a safe route that avoids the flooded corridor and log it."""
        w = self.world
        # From Gachibowli (west) to Koti (centre) crosses the Lakdikapul area.
        cmp = w.graph.plan_comparison("GACHI", "KOTI")
        w.demo_route = cmp
        fastest, safe, avoided = cmp["fastest"], cmp["safe"], cmp["avoided"]
        if safe and fastest and avoided:
            extra = round(safe["total_time"] - fastest["total_time"])
            names = ", ".join(a["name"] for a in avoided) or "high-risk roads"
            w._log_event(
                "ROUTE",
                f"Safe alternative route generated — avoids {names}; "
                f"+{max(0, extra)} min vs fastest but clears all verified "
                f"hazards.", "success")
        elif safe:
            w._log_event("ROUTE",
                         "Safe route recomputed on updated road-risk graph.",
                         "info")

    # ------------------------------------------------------------- injection
    def inject(self, inject_type, road_segment_id=None, incident_id=None):
        """Manual demo injection. Returns the affected incident dict or None."""
        w, rng = self.world, self.world.rng
        itype = inject_type.upper()

        if itype in ("ROAD_CLEAR", "CLEAR"):
            inc = (w.incidents.get(incident_id) if incident_id
                   else self._pick_active_incident())
            if not inc:
                return None
            inc["clearing"] = True
            mlat, mlon = inc["latitude"], inc["longitude"]
            vid = self._nearest_vehicle_code(mlat, mlon)
            obs = w._make_observation(vid, "CLEAR", mlat, mlon, "CAMERA",
                                      round(rng.uniform(0.78, 0.9), 3), speed=32)
            prev_c = inc.get("confidence", 0)
            w.add_observation(obs)
            w._log_event("DETECTION",
                         f"{vid} reports {inc['road_name']} now clear — "
                         f"confidence {prev_c}% -> {inc['confidence']}%.",
                         "info", incident_id=inc["id"], vehicle_id=vid)
            return inc

        if itype == "CONFLICTING":
            inc = (w.incidents.get(incident_id) if incident_id
                   else self._pick_active_incident(prefer_verified=True))
            if not inc:
                return None
            mlat, mlon = inc["latitude"], inc["longitude"]
            vid = self._nearest_vehicle_code(mlat, mlon)
            obs = w._make_observation(vid, "CLEAR", mlat, mlon, "CAMERA",
                                      round(rng.uniform(0.7, 0.85), 3), speed=30)
            prev_c = inc.get("confidence", 0)
            w.add_observation(obs)
            w._log_event("DETECTION",
                         f"CONFLICTING report — {vid} claims {inc['road_name']} "
                         f"is passable while others report a hazard. "
                         f"Confidence {prev_c}% -> {inc['confidence']}%, "
                         f"agreement {inc['agreement']}%.",
                         "warning", incident_id=inc["id"], vehicle_id=vid)
            return inc

        # New hazard injection.
        haz = itype
        eid = road_segment_id or self._pick_free_edge()
        mlat, mlon = w.edge_midpoint(eid)
        vid = self._nearest_vehicle_code(mlat, mlon)
        obs = w._make_observation(vid, haz, mlat, mlon, "CAMERA",
                                  round(rng.uniform(0.82, 0.93), 3), speed=16)
        inc, is_new, _, _ = w.add_observation(obs)
        # Add one corroborating observation so the incident is immediately
        # credible on the map.
        vid2 = self._nearest_vehicle_code(mlat, mlon, exclude=vid)
        obs2 = w._make_observation(vid2, haz, mlat + 0.0003, mlon + 0.0003,
                                   "CAMERA", round(rng.uniform(0.8, 0.9), 3),
                                   speed=14)
        w.add_observation(obs2)
        w._log_event("DETECTION",
                     f"Manual injection — {ai_detection.label_for(haz)} on "
                     f"{inc['road_name']} ({inc['confidence']}% confidence, "
                     f"{inc['evidence_count']} vehicles).",
                     "warning", incident_id=inc["id"])
        return inc

    def _pick_active_incident(self, prefer_verified=False):
        active = [i for i in self.world.active_incidents()
                  if not i.get("clearing")]
        if prefer_verified:
            verified = [i for i in active
                        if i.get("verification_status") == "VERIFIED"]
            if verified:
                return self.world.rng.choice(verified)
        return self.world.rng.choice(active) if active else None

    def _pick_free_edge(self):
        w = self.world
        active_edges = {i.get("road_segment_id") for i in w.active_incidents()}
        free = [eid for eid in w.graph.edges if eid not in active_edges]
        return w.rng.choice(free or list(w.graph.edges.keys()))

    def _nearest_vehicle_code(self, lat, lon, exclude=None):
        best, best_d = None, float("inf")
        for v in self.world.vehicles.values():
            if v["id"] == exclude or v["status"] == "DISCONNECTED":
                continue
            d = haversine_m(lat, lon, v["latitude"], v["longitude"])
            if d < best_d:
                best, best_d = v["id"], d
        return best or (exclude and next(iter(self.world.vehicles)))

    async def _broadcast(self):
        await self.manager.broadcast({"type": "state", **self.world.snapshot()})
