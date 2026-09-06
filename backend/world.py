"""ResQDrive World State.

Builds and holds the deterministic in-memory world (source of truth for the
live simulation): a Hyderabad road-segment graph, a fleet of simulated
vehicles, critical infrastructure, and the set of active incidents produced by
the Evidence Fusion Engine.

All data is SIMULATED / DEMO data.
"""
import math
import random
import uuid
from datetime import datetime, timedelta, timezone

from engines import ai_detection
from engines.fusion import fuse_observations
from engines.geo import haversine_m
from engines.reliability import CLUSTER_RADIUS_M
from engines.risk import (
    compute_priority,
    compute_risk,
    risk_components,
    risk_state,
)
from engines.routing import RoadGraph

# ---------------------------------------------------------------------------
# Hyderabad road network definition (approximate real coordinates).
# Nodes = intersections / localities. Edges = road segments.
# ---------------------------------------------------------------------------
NODES = [
    ("MIYAP", "Miyapur", 17.4968, 78.3610),
    ("KUKAT", "Kukatpally", 17.4948, 78.3996),
    ("KONDAPUR", "Kondapur", 17.4615, 78.3676),
    ("HITEC", "Hitech City", 17.4483, 78.3915),
    ("RAIDURG", "Raidurg", 17.4356, 78.3822),
    ("GACHI", "Gachibowli", 17.4401, 78.3489),
    ("JUBILEE", "Jubilee Hills", 17.4310, 78.4070),
    ("BANJARA", "Banjara Hills", 17.4156, 78.4347),
    ("PANJA", "Panjagutta", 17.4270, 78.4489),
    ("AMEER", "Ameerpet", 17.4374, 78.4487),
    ("BEGUM", "Begumpet", 17.4437, 78.4678),
    ("SECBAD", "Secunderabad", 17.4399, 78.4983),
    ("HUSSAIN", "Tank Bund", 17.4239, 78.4738),
    ("KHAIR", "Khairatabad", 17.4139, 78.4631),
    ("LAKDI", "Lakdikapul", 17.4009, 78.4610),
    ("MASAB", "Masab Tank", 17.4040, 78.4520),
    ("MEHDI", "Mehdipatnam", 17.3958, 78.4370),
    ("NAMPALLY", "Nampally", 17.3925, 78.4665),
    ("ABIDS", "Abids", 17.3908, 78.4747),
    ("KOTI", "Koti", 17.3850, 78.4867),
    ("MGBS", "MG Bus Station", 17.3789, 78.4832),
    ("CHARM", "Charminar", 17.3616, 78.4747),
    ("DILSUKH", "Dilsukhnagar", 17.3687, 78.5247),
    ("LBNAGAR", "LB Nagar", 17.3457, 78.5522),
    ("UPPAL", "Uppal", 17.4058, 78.5590),
    ("TARNAKA", "Tarnaka", 17.4265, 78.5289),
]

# (edge_id, u, v, road name)
EDGES = [
    ("RS-01", "MIYAP", "KUKAT", "Miyapur Main Road"),
    ("RS-02", "KUKAT", "HITEC", "KPHB Road"),
    ("RS-03", "KONDAPUR", "HITEC", "Kondapur Road"),
    ("RS-04", "KONDAPUR", "GACHI", "Gachibowli Kondapur Link"),
    ("RS-05", "HITEC", "RAIDURG", "Hitech City Main Road"),
    ("RS-06", "RAIDURG", "GACHI", "Gachibowli Flyover"),
    ("RS-07", "HITEC", "JUBILEE", "Road No. 45"),
    ("RS-08", "GACHI", "JUBILEE", "Outer Ring Link"),
    ("RS-09", "JUBILEE", "BANJARA", "Road No. 12"),
    ("RS-10", "JUBILEE", "AMEER", "Yousufguda Road"),
    ("RS-11", "BANJARA", "PANJA", "Road No. 1"),
    ("RS-12", "PANJA", "AMEER", "Panjagutta Road"),
    ("RS-13", "AMEER", "BEGUM", "Ameerpet Begumpet Road"),
    ("RS-14", "BEGUM", "SECBAD", "SP Road"),
    ("RS-15", "BEGUM", "HUSSAIN", "Necklace Road"),
    ("RS-16", "HUSSAIN", "KHAIR", "Tank Bund Road"),
    ("RS-17", "PANJA", "KHAIR", "Raj Bhavan Road"),
    ("RS-18", "KHAIR", "LAKDI", "Khairatabad Flyover"),
    ("RS-19", "LAKDI", "NAMPALLY", "Public Gardens Road"),
    ("RS-20", "NAMPALLY", "ABIDS", "Nampally Station Road"),
    ("RS-21", "ABIDS", "KOTI", "Abids Road"),
    ("RS-22", "KOTI", "MGBS", "Koti Main Road"),
    ("RS-23", "MGBS", "CHARM", "Charminar Road"),
    ("RS-24", "BANJARA", "MASAB", "Masab Tank Road"),
    ("RS-25", "MASAB", "MEHDI", "Mehdipatnam Road"),
    ("RS-26", "MEHDI", "NAMPALLY", "Nehru Zoo Road"),
    ("RS-27", "MEHDI", "CHARM", "Aramghar Road"),
    ("RS-28", "KOTI", "DILSUKH", "Chaderghat Road"),
    ("RS-29", "DILSUKH", "LBNAGAR", "LB Nagar Road"),
    ("RS-30", "DILSUKH", "UPPAL", "Uppal Main Road"),
    ("RS-31", "UPPAL", "TARNAKA", "Tarnaka Road"),
    ("RS-32", "TARNAKA", "SECBAD", "Secunderabad East Road"),
    ("RS-33", "SECBAD", "HUSSAIN", "Rani Gunj Road"),
    ("RS-34", "CHARM", "DILSUKH", "Chandrayangutta Road"),
    ("RS-35", "LBNAGAR", "UPPAL", "Ring Road South"),
    ("RS-36", "KHAIR", "NAMPALLY", "Saifabad Road"),
]

# Critical infrastructure (hospitals, fire, police, shelters, emergency).
INFRASTRUCTURE = [
    ("INF-01", "Osmania General Hospital", "HOSPITAL", 17.3739, 78.4738, 1.0),
    ("INF-02", "NIMS Hospital Punjagutta", "HOSPITAL", 17.4275, 78.4506, 1.0),
    ("INF-03", "Gandhi Hospital Secunderabad", "HOSPITAL", 17.4416, 78.5010, 0.95),
    ("INF-04", "Care Hospital Banjara Hills", "HOSPITAL", 17.4139, 78.4360, 0.9),
    ("INF-05", "Central Fire Station Gunfoundry", "FIRE", 17.3971, 78.4720, 0.85),
    ("INF-06", "Kukatpally Fire Station", "FIRE", 17.4930, 78.4010, 0.8),
    ("INF-07", "Banjara Hills Police Station", "POLICE", 17.4180, 78.4380, 0.7),
    ("INF-08", "Abids Police Station", "POLICE", 17.3900, 78.4760, 0.7),
    ("INF-09", "NDRF Relief Shelter Necklace Road", "SHELTER", 17.4250, 78.4700, 0.75),
    ("INF-10", "GHMC Emergency Operations Centre", "EMERGENCY", 17.4045, 78.4560, 0.95),
    ("INF-11", "LB Nagar Community Shelter", "SHELTER", 17.3470, 78.5500, 0.7),
]

VEHICLE_COUNT = 60          # RQ-101 .. RQ-160
CITY_CENTER = (17.3980, 78.4700)

# Ambient scenario hazard weights (probability of a random new hazard by type).
SCENARIO_HAZARDS = {
    "CYCLONE_FLOOD": ["FLOOD", "FLOOD", "WATERLOGGING", "FALLEN_TREE", "DEBRIS"],
    "FLOOD": ["FLOOD", "WATERLOGGING", "FLOOD", "WATERLOGGING"],
    "CYCLONE": ["FALLEN_TREE", "DEBRIS", "FLOOD", "ROAD_BLOCKAGE"],
    "LANDSLIDE": ["LANDSLIDE", "DEBRIS", "ROAD_DAMAGE"],
    "URBAN_WATERLOGGING": ["WATERLOGGING", "FLOOD", "POTHOLE"],
    "ROAD_BLOCKAGE": ["ROAD_BLOCKAGE", "ACCIDENT", "CONSTRUCTION"],
    "MIXED": ["FLOOD", "LANDSLIDE", "ACCIDENT", "FALLEN_TREE", "POTHOLE",
              "ROAD_BLOCKAGE", "DEBRIS", "ROAD_DAMAGE"],
}


def _bearing(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(phi2)
    x = (math.cos(phi1) * math.sin(phi2)
         - math.sin(phi1) * math.cos(phi2) * math.cos(dl))
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def _interp(lat1, lon1, lat2, lon2, t):
    return (lat1 + (lat2 - lat1) * t, lon1 + (lon2 - lon1) * t)


def _new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:6].upper()}"


class World:
    """Holds all runtime state for the ResQDrive simulation."""

    def __init__(self):
        self.rng = random.Random(42)
        self.graph = RoadGraph()
        self.vehicles = {}
        self.infrastructure = []
        self.incidents = {}          # incident_id -> dict
        self.events = []             # live feed (most recent first, capped)
        self.response_actions = []
        self.sim_time = datetime.now(timezone.utc)
        self.sim = {
            "status": "STOPPED",     # STOPPED | RUNNING | PAUSED
            "scenario": "CYCLONE_FLOOD",
            "speed": 2,
            "tick": 0,
            "scenario_started_tick": None,
            "observations_total": 0,
            "fusions_total": 0,
        }
        self._edge_len_km = {}
        self._inc_counter = 1000
        self.demo_route = None
        self.build()

    # ------------------------------------------------------------------ build
    def build(self):
        """Deterministically (re)build the whole world."""
        self.rng = random.Random(42)
        self.graph = RoadGraph()
        self.vehicles = {}
        self.infrastructure = []
        self.incidents = {}
        self.events = []
        self.response_actions = []
        self._edge_len_km = {}
        self._inc_counter = 1000
        self.demo_route = None
        self.sim_time = datetime.now(timezone.utc)
        self.sim.update({
            "status": "STOPPED", "scenario": "CYCLONE_FLOOD", "speed": 2,
            "tick": 0, "scenario_started_tick": None,
            "observations_total": 0, "fusions_total": 0,
        })

        node_pos = {n[0]: (n[2], n[3]) for n in NODES}
        for nid, name, lat, lon in NODES:
            self.graph.add_node(nid, lat, lon, name)

        # Assign a road "importance" (traffic impact) per edge for prioritisation.
        for eid, u, v, name in EDGES:
            la1, lo1 = node_pos[u]
            la2, lo2 = node_pos[v]
            dist_km = haversine_m(la1, lo1, la2, lo2) / 1000.0
            base_time = max(1.0, round(dist_km * 2.2, 1))  # ~27 km/h avg
            self._edge_len_km[eid] = max(0.05, dist_km)
            importance = round(self.rng.uniform(0.4, 1.0), 2)
            self.graph.add_edge(eid, u, v, base_time=base_time, risk=0,
                                name=name, importance=importance,
                                length_km=dist_km)

        for iid, name, kind, lat, lon, importance in INFRASTRUCTURE:
            self.infrastructure.append({
                "id": iid, "name": name, "type": kind,
                "latitude": lat, "longitude": lon, "importance": importance,
            })

        self._seed_vehicles()
        self._seed_incidents()
        self._log_event("SYSTEM", "ResQDrive network initialised — Hyderabad "
                        "cooperative sensing grid online (SIMULATED).", "info")

    # --------------------------------------------------------------- vehicles
    def _seed_vehicles(self):
        edge_ids = list(self.graph.edges.keys())
        statuses = (["ACTIVE"] * 6 + ["OBSERVING"] * 2
                    + ["TRANSMITTING"] * 2 + ["DISCONNECTED"])
        for i in range(VEHICLE_COUNT):
            code = f"RQ-{101 + i}"
            eid = self.rng.choice(edge_ids)
            e = self.graph.edges[eid]
            direction = self.rng.choice([1, -1])
            pos = round(self.rng.uniform(0.05, 0.95), 3)
            status = self.rng.choice(statuses)
            connected = status != "DISCONNECTED"
            v = {
                "id": code,
                "vehicle_code": code,
                "status": status,
                "edge_id": eid,
                "pos": pos,
                "direction": direction,
                "speed": round(self.rng.uniform(14, 52), 1),
                "heading": 0,
                "latitude": 0.0,
                "longitude": 0.0,
                "camera_status": self.rng.choice(
                    ["ONLINE", "ONLINE", "ONLINE", "DEGRADED"]),
                "gps_status": self.rng.choice(
                    ["EXCELLENT", "EXCELLENT", "GOOD", "GOOD", "FAIR"]),
                "imu_status": self.rng.choice(["ONLINE", "ONLINE", "ONLINE", "OFFLINE"]),
                "network_quality": (self.rng.choice(["EXCELLENT", "GOOD", "FAIR"])
                                    if connected else "OFFLINE"),
                "battery": self.rng.randint(35, 100),
                "buffered": 0,
                "last_seen_tick": 0,
                "current_observation": None,
                "observation_history": [],
            }
            self._place_vehicle(v)
            self.vehicles[code] = v

    def _place_vehicle(self, v):
        e = self.graph.edges[v["edge_id"]]
        u_node, v_node = self.graph.nodes[e["u"]], self.graph.nodes[e["v"]]
        if v["direction"] == 1:
            a, b = u_node, v_node
        else:
            a, b = v_node, u_node
        lat, lon = _interp(a["lat"], a["lon"], b["lat"], b["lon"], v["pos"])
        v["latitude"] = round(lat, 6)
        v["longitude"] = round(lon, 6)
        v["heading"] = round(_bearing(a["lat"], a["lon"], b["lat"], b["lon"]))

    def edge_midpoint(self, edge_id):
        e = self.graph.edges[edge_id]
        u_node, v_node = self.graph.nodes[e["u"]], self.graph.nodes[e["v"]]
        return _interp(u_node["lat"], u_node["lon"], v_node["lat"], v_node["lon"], 0.5)

    # --------------------------------------------------------------- incidents
    def _next_incident_id(self):
        self._inc_counter += 1
        return f"INC-{self._inc_counter}"

    def _make_observation(self, vehicle_id, hazard_type, lat, lon, sensor_type,
                          confidence, severity=None, quality=1.0, source="SENSOR",
                          speed=None, heading=None):
        det = ai_detection.detect(
            hazard_type, sensor_type=sensor_type,
            device=f"Edge Node {vehicle_id}" if vehicle_id else "Citizen Device",
            rng=self.rng, confidence=confidence)
        return {
            "id": _new_id("OBS"),
            "vehicle_id": vehicle_id,
            "hazard_type": str(hazard_type).upper(),
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "timestamp": self.sim_time,
            "confidence": det["confidence"],
            "severity": (severity or det["severity"]),
            "sensor_type": sensor_type.upper(),
            "sensor_quality": quality,
            "source": source,
            "speed": speed,
            "heading": heading,
            "metadata": {
                "bounding_box": det["bounding_box"],
                "latency_ms": det["latency_ms"],
                "model": det["model"],
                "device": det["device"],
                "label": det["label"],
            },
        }

    def _nearest_edge(self, lat, lon):
        best, best_d = None, float("inf")
        for eid in self.graph.edges:
            mlat, mlon = self.edge_midpoint(eid)
            d = haversine_m(lat, lon, mlat, mlon)
            if d < best_d:
                best, best_d = eid, d
        return best

    def _nearby_infrastructure(self, lat, lon, radius_m=900):
        out = []
        for inf in self.infrastructure:
            d = haversine_m(lat, lon, inf["latitude"], inf["longitude"])
            if d <= radius_m:
                out.append({**inf, "distance_m": round(d)})
        out.sort(key=lambda x: x["distance_m"])
        return out

    def _infra_importance(self, lat, lon):
        """Max infrastructure importance within influence radius (0-1)."""
        best = 0.0
        for inf in self.infrastructure:
            d = haversine_m(lat, lon, inf["latitude"], inf["longitude"])
            if d <= 1200:
                factor = max(0.0, 1.0 - d / 1200.0) * inf["importance"]
                best = max(best, factor)
        return best

    def add_observation(self, obs, hazard_type=None):
        """Attach an observation to a nearby incident (or create one) and refuse.

        Returns (incident, is_new, prev_confidence, prev_state).
        """
        hazard = (hazard_type or obs["hazard_type"]).upper()
        self.sim["observations_total"] += 1

        # Find candidate incident within cluster radius.
        target = None
        best_d = CLUSTER_RADIUS_M
        for inc in self.incidents.values():
            if inc.get("response_status") == "RESOLVED":
                continue
            d = haversine_m(obs["latitude"], obs["longitude"],
                            inc["latitude"], inc["longitude"])
            if d <= best_d:
                target = inc
                best_d = d

        is_new = False
        prev_conf, prev_state = 0, None
        if target is None:
            if hazard in ("CLEAR", "ROAD_CLEAR"):
                return None, False, 0, None  # nothing to clear
            target = self._create_incident(obs)
            is_new = True
        else:
            prev_conf = target.get("confidence", 0)
            prev_state = target.get("verification_status")
            target["observations"].append(obs)
            target["observations"] = target["observations"][-40:]

        self.refuse_incident(target)
        return target, is_new, prev_conf, prev_state

    def _create_incident(self, obs):
        eid = self._nearest_edge(obs["latitude"], obs["longitude"])
        inc = {
            "id": self._next_incident_id(),
            "hazard_type": obs["hazard_type"],
            "latitude": obs["latitude"],
            "longitude": obs["longitude"],
            "road_segment_id": eid,
            "road_name": self.graph.edges[eid]["name"] if eid else "Unknown Road",
            "observations": [obs],
            "response_status": "AWAITING",
            "created_at": self.sim_time,
            "updated_at": self.sim_time,
            "resolved_at": None,
            "first_detected": self.sim_time,
            "last_confirmed": self.sim_time,
            "confidence_timeline": [],
            "acknowledged_by": None,
        }
        self.incidents[inc["id"]] = inc
        return inc

    def refuse_incident(self, inc):
        """Recompute an incident's fused assessment from its observations."""
        self.sim["fusions_total"] += 1
        fused = fuse_observations(inc["observations"], now=self.sim_time)

        inc["hazard_type"] = fused["hazard_type"] or inc["hazard_type"]
        inc["severity"] = fused["severity"]
        inc["confidence"] = fused["confidence"]
        inc["confidence_raw"] = fused["confidence_raw"]
        inc["base_confidence"] = fused["base_confidence"]
        inc["verification_status"] = fused["verification_state"]
        inc["evidence_count"] = fused["evidence_count"]
        inc["observation_count"] = fused["observation_count"]
        inc["agreement"] = fused["agreement"]
        inc["conflict_count"] = fused["conflict_count"]
        inc["supporting_vehicles"] = fused["supporting_vehicles"]
        inc["conflicting_vehicles"] = fused["conflicting_vehicles"]
        inc["freshness"] = fused["freshness"]
        inc["avg_sensor_reliability"] = fused["avg_sensor_reliability"]
        inc["breakdown"] = fused["breakdown"]

        # Risk model.
        importance = 0.6
        if inc.get("road_segment_id") in self.graph.edges:
            importance = self.graph.edges[inc["road_segment_id"]].get("importance", 0.6)
        infra = self._infra_importance(inc["latitude"], inc["longitude"])
        comps = risk_components(
            inc["severity"], fused["confidence_raw"], fused["freshness"] / 100.0,
            fused["agreement"] / 100.0, fused["avg_sensor_reliability"] / 100.0)
        inc["risk_components"] = comps
        inc["risk_score"] = comps["total"]
        inc["risk_state"] = risk_state(comps["total"])

        prio = compute_priority(
            risk=comps["total"], severity=inc["severity"],
            traffic_impact=importance, freshness=fused["freshness"] / 100.0,
            infrastructure=infra)
        inc["priority"] = prio["level"]
        inc["priority_score"] = prio["score"]

        inc["nearby_infrastructure"] = self._nearby_infrastructure(
            inc["latitude"], inc["longitude"])
        inc["recommended_action"] = self._recommend(inc)

        # Evidence buckets for the UI.
        sensors = {}
        for o in inc["observations"]:
            sensors.setdefault(o["sensor_type"], 0)
            sensors[o["sensor_type"]] += 1
        inc["sensor_evidence"] = sensors

        # Confidence timeline (record on change).
        tl = inc["confidence_timeline"]
        if not tl or tl[-1]["value"] != inc["confidence"]:
            tl.append({"t": self.sim_time, "value": inc["confidence"]})
            inc["confidence_timeline"] = tl[-24:]

        inc["updated_at"] = self.sim_time
        if inc["confidence"] > 0 and fused["verification_state"] != "STALE":
            inc["last_confirmed"] = self.sim_time

        # Auto-resolve when strongly cleared: dominant hazard collapsed or very
        # low confidence with conflicting clear reports.
        if (inc["response_status"] != "RESOLVED"
                and inc.get("conflict_count", 0) > 0
                and inc["confidence"] < 32
                and inc["agreement"] < 45):
            self._resolve_incident(inc, auto=True)

        self._recompute_edge_risk(inc.get("road_segment_id"))
        return inc

    def _recommend(self, inc):
        state = inc.get("verification_status")
        risk = inc.get("risk_score", 0)
        if inc.get("response_status") == "RESOLVED":
            return "Road reopened — condition cleared by later observations."
        if state == "CONFLICTING":
            return "Under verification — conflicting reports. Advise caution."
        if state == "STALE":
            return "Evidence ageing — awaiting fresh observations."
        if risk >= 80:
            return "Avoid road immediately — dispatch emergency response."
        if risk >= 50:
            return "Exercise caution — monitor for escalation."
        return "Monitor — low current risk."

    def _resolve_incident(self, inc, auto=False):
        inc["response_status"] = "RESOLVED"
        inc["resolved_at"] = self.sim_time
        inc["risk_score"] = min(inc.get("risk_score", 0), 18)
        inc["risk_state"] = "SAFE"
        self._recompute_edge_risk(inc.get("road_segment_id"))
        self._log_event(
            "FUSION",
            f"{inc['id']} on {inc['road_name']} cleared — road status restored "
            f"to SAFE{' (auto)' if auto else ''}.",
            "success", incident_id=inc["id"])

    def _recompute_edge_risk(self, edge_id):
        if not edge_id or edge_id not in self.graph.edges:
            return
        active = [i for i in self.incidents.values()
                  if i.get("road_segment_id") == edge_id
                  and i.get("response_status") != "RESOLVED"]
        if active:
            risk = max(i.get("risk_score", 0) for i in active)
        else:
            risk = 0
        self.graph.set_risk(edge_id, risk)

    # ------------------------------------------------------------------ seeds
    def _seed_incident(self, edge_id, hazard, vehicle_specs, ages, resolved=False):
        """Create a seeded incident with explicit synthetic observations.

        vehicle_specs : list of (vehicle_code, sensor_type, confidence, hazard_override)
        ages          : list of minutes-ago for each observation
        """
        mlat, mlon = self.edge_midpoint(edge_id)
        observations = []
        for (vc, sensor, conf, hz_override), age in zip(vehicle_specs, ages):
            jitter_lat = self.rng.uniform(-0.0006, 0.0006)
            jitter_lon = self.rng.uniform(-0.0006, 0.0006)
            hz = hz_override or hazard
            det = ai_detection.detect(hz, sensor_type=sensor,
                                      device=f"Edge Node {vc}", rng=self.rng,
                                      confidence=conf)
            observations.append({
                "id": _new_id("OBS"),
                "vehicle_id": vc,
                "hazard_type": hz.upper(),
                "latitude": round(mlat + jitter_lat, 6),
                "longitude": round(mlon + jitter_lon, 6),
                "timestamp": self.sim_time - timedelta(minutes=age),
                "confidence": det["confidence"],
                "severity": det["severity"],
                "sensor_type": sensor.upper(),
                "sensor_quality": 1.0,
                "source": "SENSOR",
                "speed": round(self.rng.uniform(8, 30), 1),
                "heading": self.rng.randint(0, 359),
                "metadata": {
                    "bounding_box": det["bounding_box"],
                    "latency_ms": det["latency_ms"],
                    "model": det["model"],
                    "device": det["device"],
                    "label": det["label"],
                },
            })
        inc = self._create_incident(observations[0])
        inc["observations"] = observations
        inc["latitude"] = round(mlat, 6)
        inc["longitude"] = round(mlon, 6)
        oldest = max(ages)
        inc["created_at"] = self.sim_time - timedelta(minutes=oldest)
        inc["first_detected"] = inc["created_at"]
        self.refuse_incident(inc)
        if resolved:
            self._resolve_incident(inc)
        return inc

    def _seed_incidents(self):
        F = lambda vc, s, c: (vc, s, c, None)  # noqa: E731
        # 1. VERIFIED flood (3 camera + IMU) - fresh
        self._seed_incident("RS-18", "FLOOD",
                            [F("RQ-102", "CAMERA", 0.88), F("RQ-117", "CAMERA", 0.91),
                             F("RQ-131", "CAMERA", 0.94), ("RQ-145", "IMU", 0.74, "FLOOD")],
                            [2, 3, 1, 2])
        # 2. VERIFIED landslide - critical
        self._seed_incident("RS-29", "LANDSLIDE",
                            [F("RQ-108", "CAMERA", 0.90), F("RQ-122", "CAMERA", 0.93),
                             F("RQ-140", "CAMERA", 0.87)],
                            [4, 3, 2])
        # 3. CONFLICTING waterlogging (2 report, 1 clear)
        self._seed_incident("RS-25", "WATERLOGGING",
                            [F("RQ-104", "CAMERA", 0.83), F("RQ-119", "CAMERA", 0.80),
                             ("RQ-150", "CAMERA", 0.78, "CLEAR")],
                            [3, 4, 2])
        # 4. CORROBORATED fallen tree
        self._seed_incident("RS-09", "FALLEN_TREE",
                            [F("RQ-110", "CAMERA", 0.85), F("RQ-126", "CAMERA", 0.82)],
                            [5, 3])
        # 5. UNVERIFIED single pothole
        self._seed_incident("RS-02", "POTHOLE",
                            [F("RQ-133", "CAMERA", 0.79)], [4])
        # 6. VERIFIED accident near hospital
        self._seed_incident("RS-13", "ACCIDENT",
                            [F("RQ-106", "CAMERA", 0.89), F("RQ-118", "CAMERA", 0.86),
                             ("RQ-142", "OBD", 0.80, "ACCIDENT")],
                            [3, 2, 1])
        # 7. STALE debris (old observations)
        self._seed_incident("RS-31", "DEBRIS",
                            [F("RQ-113", "CAMERA", 0.84), F("RQ-129", "CAMERA", 0.81)],
                            [55, 62])
        # 8. CORROBORATED road blockage
        self._seed_incident("RS-34", "ROAD_BLOCKAGE",
                            [F("RQ-111", "CAMERA", 0.87), F("RQ-124", "CAMERA", 0.83)],
                            [6, 4])
        # 9. UNVERIFIED construction
        self._seed_incident("RS-05", "CONSTRUCTION",
                            [F("RQ-137", "CAMERA", 0.76)], [7])
        # 10. VERIFIED flood near EOC
        self._seed_incident("RS-16", "FLOOD",
                            [F("RQ-103", "CAMERA", 0.90), F("RQ-121", "CAMERA", 0.88),
                             F("RQ-139", "CAMERA", 0.92), ("RQ-155", "IMU", 0.71, "FLOOD")],
                            [3, 2, 1, 2])
        # 11. CAUTION road damage
        self._seed_incident("RS-22", "ROAD_DAMAGE",
                            [F("RQ-115", "CAMERA", 0.82), F("RQ-148", "CITIZEN", 0.58)],
                            [8, 5])
        # 12. RESOLVED (cleared) waterlogging - shows recovery
        self._seed_incident("RS-26", "WATERLOGGING",
                            [F("RQ-109", "CAMERA", 0.84),
                             ("RQ-127", "CAMERA", 0.80, "CLEAR"),
                             ("RQ-152", "CAMERA", 0.82, "CLEAR")],
                            [30, 6, 3], resolved=True)

    # ------------------------------------------------------------------ events
    def _log_event(self, category, message, level="info", incident_id=None,
                   vehicle_id=None):
        ev = {
            "id": _new_id("EV"),
            "timestamp": self.sim_time,
            "category": category,   # SYSTEM | DETECTION | FUSION | ROUTE | ALERT | RESPONSE | VEHICLE
            "message": message,
            "level": level,         # info | success | warning | critical
            "incident_id": incident_id,
            "vehicle_id": vehicle_id,
        }
        self.events.insert(0, ev)
        self.events = self.events[:200]
        return ev

    # ---------------------------------------------------------------- queries
    def active_incidents(self):
        return [i for i in self.incidents.values()
                if i.get("response_status") != "RESOLVED"]

    def dashboard_summary(self):
        active = self.active_incidents()
        connected = [v for v in self.vehicles.values()
                     if v["network_quality"] != "OFFLINE"]
        verified = [i for i in active if i.get("verification_status") == "VERIFIED"]
        unsafe_roads = [e for e in self.graph.edges.values()
                        if risk_state(e["risk"]) == "UNSAFE"]
        caution_roads = [e for e in self.graph.edges.values()
                         if risk_state(e["risk"]) == "CAUTION"]
        priority_zones = [i for i in active if i.get("priority") in ("P1", "P2")]
        unverified = [i for i in active
                      if i.get("verification_status") in ("UNVERIFIED", "CONFLICTING")]
        conf_vals = [i["confidence"] for i in active] or [0]
        network_conf = round(sum(conf_vals) / len(conf_vals)) if active else 0
        return {
            "active_vehicles": len(connected),
            "total_vehicles": len(self.vehicles),
            "active_hazards": len(active),
            "unsafe_roads": len(unsafe_roads),
            "caution_roads": len(caution_roads),
            "verified_incidents": len(verified),
            "unverified_incidents": len(unverified),
            "network_confidence": network_conf,
            "priority_zones": len(priority_zones),
            "observations_total": self.sim["observations_total"],
            "fusions_total": self.sim["fusions_total"],
        }

    def network_health(self):
        vs = list(self.vehicles.values())
        connected = [v for v in vs if v["network_quality"] != "OFFLINE"]
        gps_rank = {"EXCELLENT": 100, "GOOD": 82, "FAIR": 62, "OFFLINE": 0}
        cam_online = sum(1 for v in vs if v["camera_status"] == "ONLINE")
        avg_gps = round(sum(gps_rank.get(v["gps_status"], 0) for v in connected)
                        / max(1, len(connected)))
        sensor_health = round(100 * cam_online / max(1, len(vs)))
        latency = self.rng.randint(120, 165)
        obs_rate = round(self.sim["observations_total"]
                         / max(1, self.sim["tick"]) * 30, 1) if self.sim["tick"] else 0.0
        return {
            "connected": len(connected),
            "total": len(vs),
            "disconnected": len(vs) - len(connected),
            "avg_sensor_health": sensor_health,
            "avg_gps_accuracy": avg_gps,
            "avg_latency_ms": latency,
            "observation_rate": obs_rate,
            "fusion_success": 93,
        }

    # ------------------------------------------------------- serialization
    def _age_min(self, ts):
        if ts is None:
            return 0.0
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        now = self.sim_time
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        return max(0.0, (now - ts).total_seconds() / 60.0)

    def serialize_vehicle(self, v, detail=False):
        out = {
            "id": v["id"],
            "vehicle_code": v["vehicle_code"],
            "status": v["status"],
            "latitude": v["latitude"],
            "longitude": v["longitude"],
            "speed": v["speed"],
            "heading": v["heading"],
            "camera_status": v["camera_status"],
            "gps_status": v["gps_status"],
            "imu_status": v["imu_status"],
            "network_quality": v["network_quality"],
            "battery": v["battery"],
            "buffered": v["buffered"],
            "road_name": self.graph.edges[v["edge_id"]]["name"],
            "current_observation": v["current_observation"],
            "last_seen_sec": round(self._age_min(
                self.sim_time) * 60) if False else self.rng.randint(1, 20),
        }
        if detail:
            out["observation_history"] = v["observation_history"][-12:]
        return out

    def serialize_incident(self, inc, detail=False):
        out = {
            "id": inc["id"],
            "hazard_type": inc["hazard_type"],
            "hazard_label": ai_detection.label_for(inc["hazard_type"]),
            "latitude": inc["latitude"],
            "longitude": inc["longitude"],
            "road_segment_id": inc.get("road_segment_id"),
            "road_name": inc.get("road_name"),
            "severity": inc.get("severity"),
            "confidence": inc.get("confidence", 0),
            "base_confidence": inc.get("base_confidence", 0),
            "verification_status": inc.get("verification_status", "UNVERIFIED"),
            "risk_score": inc.get("risk_score", 0),
            "risk_state": inc.get("risk_state", "UNKNOWN"),
            "risk_components": inc.get("risk_components", {}),
            "freshness": inc.get("freshness", 0),
            "agreement": inc.get("agreement", 0),
            "evidence_count": inc.get("evidence_count", 0),
            "observation_count": inc.get("observation_count", 0),
            "conflict_count": inc.get("conflict_count", 0),
            "supporting_vehicles": inc.get("supporting_vehicles", []),
            "conflicting_vehicles": inc.get("conflicting_vehicles", []),
            "priority": inc.get("priority", "P4"),
            "priority_score": inc.get("priority_score", 0),
            "response_status": inc.get("response_status", "AWAITING"),
            "recommended_action": inc.get("recommended_action"),
            "breakdown": inc.get("breakdown", {}),
            "sensor_evidence": inc.get("sensor_evidence", {}),
            "nearby_infrastructure": inc.get("nearby_infrastructure", []),
            "age_min": round(self._age_min(inc.get("last_confirmed"))),
            "created_min_ago": round(self._age_min(inc.get("first_detected"))),
        }
        if detail:
            out["observations"] = sorted(
                [self._serialize_obs(o) for o in inc["observations"]],
                key=lambda x: x["timestamp"], reverse=True)
            out["confidence_timeline"] = [
                {"t": (t["t"].isoformat() if hasattr(t["t"], "isoformat") else t["t"]),
                 "age_min": round(self._age_min(t["t"])),
                 "value": t["value"]}
                for t in inc.get("confidence_timeline", [])]
            out["acknowledged_by"] = inc.get("acknowledged_by")
        return out

    def _serialize_obs(self, o):
        return {
            "id": o["id"],
            "vehicle_id": o["vehicle_id"],
            "hazard_type": o["hazard_type"],
            "hazard_label": ai_detection.label_for(o["hazard_type"]),
            "latitude": o["latitude"],
            "longitude": o["longitude"],
            "timestamp": o["timestamp"].isoformat() if hasattr(o["timestamp"], "isoformat") else o["timestamp"],
            "age_min": round(self._age_min(o["timestamp"]), 1),
            "confidence": round(o["confidence"] * 100),
            "severity": o["severity"],
            "sensor_type": o["sensor_type"],
            "source": o.get("source", "SENSOR"),
            "metadata": o.get("metadata", {}),
            "speed": o.get("speed"),
        }

    def serialize_road(self, eid):
        e = self.graph.edges[eid]
        u_node, v_node = self.graph.nodes[e["u"]], self.graph.nodes[e["v"]]
        active = [i["id"] for i in self.active_incidents()
                  if i.get("road_segment_id") == eid]
        return {
            "id": eid,
            "name": e["name"],
            "start_node": e["u"],
            "end_node": e["v"],
            "coordinates": [[u_node["lat"], u_node["lon"]],
                            [v_node["lat"], v_node["lon"]]],
            "base_travel_time": e["base_time"],
            "length_km": round(e.get("length_km", 0), 2),
            "risk_score": round(e["risk"]),
            "risk_state": risk_state(e["risk"]),
            "importance": e.get("importance", 0.6),
            "hazard_ids": active,
        }

    def roads_snapshot(self):
        return [self.serialize_road(eid) for eid in self.graph.edges]

    def snapshot(self, include_detail=False):
        return {
            "sim": {**self.sim, "sim_time": self.sim_time.isoformat()},
            "summary": self.dashboard_summary(),
            "vehicles": [self.serialize_vehicle(v) for v in self.vehicles.values()],
            "incidents": [self.serialize_incident(i)
                          for i in sorted(self.incidents.values(),
                                          key=lambda x: x.get("priority_score", 0),
                                          reverse=True)],
            "roads": self.roads_snapshot(),
            "infrastructure": self.infrastructure,
            "events": [self._serialize_event(e) for e in self.events[:40]],
            "demo_route": self.demo_route,
        }

    def _serialize_event(self, e):
        return {**e, "timestamp": e["timestamp"].isoformat()
                if hasattr(e["timestamp"], "isoformat") else e["timestamp"]}


# Global singleton world.
world = World()
