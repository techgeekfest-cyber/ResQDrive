"""ResQDrive backend API (FastAPI + MongoDB + WebSockets).

Serves the cooperative vehicle-based disaster-intelligence prototype. All
dashboard metrics are derived from live backend World state (never hardcoded),
and the simulation genuinely mutates that state and broadcasts changes over
WebSockets. MongoDB is used for durable persistence of the world snapshot,
events, response actions and citizen reports.

All data is SIMULATED / DEMO data.
"""
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import (
    APIRouter,
    Body,
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.middleware.cors import CORSMiddleware

from engines.fusion import fuse_observations
from engines.risk import risk_state
from models import (
    CitizenReport,
    InjectRequest,
    ObservationCreate,
    ResponseActionRequest,
    RoutePlanRequest,
    SimulationSpeedRequest,
    SimulationStartRequest,
)
from simulation import SimulationEngine
from world import world
from ws_manager import manager

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("resqdrive")

app = FastAPI(title="ResQDrive API")
api = APIRouter(prefix="/api")


# --------------------------------------------------------------- persistence
async def persist_snapshot(snapshot):
    """Durably store the latest world snapshot (single doc, fast)."""
    try:
        snapshot = {**snapshot, "_id": "latest",
                    "persisted_at": datetime.now(timezone.utc).isoformat()}
        await db.world_state.replace_one({"_id": "latest"}, snapshot, upsert=True)
    except Exception:
        logger.exception("persist_snapshot failed")


sim = SimulationEngine(world, manager, persist_cb=persist_snapshot)


async def push():
    """Broadcast current world state to all WebSocket clients + persist."""
    await manager.broadcast({"type": "state", **world.snapshot()})
    await persist_snapshot(world.snapshot())


# ------------------------------------------------------------------- helpers
def _enrich_route(route):
    if not route:
        return None
    edges = []
    for eid in route["edges"]:
        e = world.graph.edges[eid]
        edges.append({
            "id": eid, "name": e["name"], "risk_score": round(e["risk"]),
            "risk_state": risk_state(e["risk"]),
            "base_time": e["base_time"],
        })
    nodes = [{"id": n, "name": world.graph.nodes[n]["name"]}
             for n in route["nodes"]]
    return {**route, "segments": edges, "node_details": nodes}


# ------------------------------------------------------------------- routes
@api.get("/")
async def root():
    return {"service": "ResQDrive", "status": "online",
            "disclaimer": "SIMULATED / PROTOTYPE / DEMO DATA"}


@api.get("/snapshot")
async def get_snapshot():
    return world.snapshot()


@api.get("/dashboard/summary")
async def dashboard_summary():
    return world.dashboard_summary()


@api.get("/network/health")
async def network_health():
    return world.network_health()


@api.get("/infrastructure")
async def get_infrastructure():
    return world.infrastructure


# -- vehicles ----------------------------------------------------------------
@api.get("/vehicles")
async def get_vehicles():
    return [world.serialize_vehicle(v) for v in world.vehicles.values()]


@api.get("/vehicles/{vehicle_id}")
async def get_vehicle(vehicle_id: str):
    v = world.vehicles.get(vehicle_id)
    if not v:
        raise HTTPException(404, "Vehicle not found")
    return world.serialize_vehicle(v, detail=True)


# -- incidents / hazards -----------------------------------------------------
@api.get("/incidents")
async def get_incidents(verification: str = None, active: bool = True):
    incs = world.incidents.values()
    if active:
        incs = [i for i in incs if i.get("response_status") != "RESOLVED"]
    else:
        incs = list(incs)
    if verification:
        incs = [i for i in incs
                if i.get("verification_status") == verification.upper()]
    incs = sorted(incs, key=lambda x: x.get("priority_score", 0), reverse=True)
    return [world.serialize_incident(i) for i in incs]


@api.get("/incidents/{incident_id}")
async def get_incident(incident_id: str):
    inc = world.incidents.get(incident_id)
    if not inc:
        raise HTTPException(404, "Incident not found")
    return world.serialize_incident(inc, detail=True)


@api.get("/hazards")
async def get_hazards():
    incs = sorted(world.active_incidents(),
                  key=lambda x: x.get("priority_score", 0), reverse=True)
    return [world.serialize_incident(i) for i in incs]


# -- roads -------------------------------------------------------------------
@api.get("/roads/risk")
async def roads_risk():
    return world.roads_snapshot()


# -- observations / fusion ---------------------------------------------------
@api.post("/observations")
async def post_observation(payload: ObservationCreate):
    quality = payload.sensor_quality
    if payload.source == "CITIZEN":
        quality = 1.0  # reliability handled by CITIZEN sensor weight
    conf = payload.confidence
    obs = world._make_observation(
        payload.vehicle_id or "CITIZEN",
        payload.hazard_type,
        payload.latitude, payload.longitude,
        "CITIZEN" if payload.source == "CITIZEN" else payload.sensor_type,
        conf, severity=payload.severity, quality=quality, source=payload.source)
    inc, is_new, prev_c, prev_s = world.add_observation(obs)
    if inc is None:
        return {"ok": True, "incident": None}
    world._log_event(
        "DETECTION",
        f"Observation added on {inc['road_name']} — {inc['hazard_label'] if 'hazard_label' in inc else inc['hazard_type']} "
        f"now {inc['confidence']}% ({inc['verification_status']}).",
        "info", incident_id=inc["id"])
    await push()
    return {"ok": True, "incident": world.serialize_incident(inc, detail=True),
            "is_new": is_new}


@api.post("/evidence/fuse")
async def evidence_fuse(observations: List[Dict[str, Any]] = Body(...)):
    """Stateless demonstration of the Evidence Fusion Engine.

    Accepts a list of observation dicts (vehicle_id, hazard_type, latitude,
    longitude, confidence, sensor_type, sensor_quality, age_minutes) and returns
    the fused assessment. ``age_minutes`` (if given) is converted to a timestamp.
    """
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    prepared = []
    for o in observations:
        age = float(o.get("age_minutes", 0))
        prepared.append({
            "vehicle_id": o.get("vehicle_id"),
            "hazard_type": o.get("hazard_type", "FLOOD"),
            "latitude": o.get("latitude", 0.0),
            "longitude": o.get("longitude", 0.0),
            "confidence": float(o.get("confidence", 0.8)),
            "severity": o.get("severity", "HIGH"),
            "sensor_type": o.get("sensor_type", "CAMERA"),
            "sensor_quality": float(o.get("sensor_quality", 1.0)),
            "timestamp": now - timedelta(minutes=age),
        })
    return fuse_observations(prepared, now=now)


# -- routing -----------------------------------------------------------------
@api.get("/routes")
async def get_routes():
    nodes = [{"id": nid, "name": world.graph.nodes[nid]["name"]}
             for nid in world.graph.nodes]
    demo = None
    if world.demo_route:
        demo = {
            "fastest": _enrich_route(world.demo_route.get("fastest")),
            "safe": _enrich_route(world.demo_route.get("safe")),
            "avoided": world.demo_route.get("avoided", []),
        }
    return {"nodes": sorted(nodes, key=lambda x: x["name"]), "demo": demo}


@api.post("/routes/plan")
async def plan_route(payload: RoutePlanRequest):
    if payload.start == payload.destination:
        raise HTTPException(400, "Start and destination must differ")
    cmp = world.graph.plan_comparison(payload.start, payload.destination)
    fastest = _enrich_route(cmp["fastest"])
    safe = _enrich_route(cmp["safe"])
    if not fastest or not safe:
        raise HTTPException(400, "No route available between these points")
    extra = round(safe["total_time"] - fastest["total_time"])
    same = set(fastest["edges"]) == set(safe["edges"])
    explanation = {
        "fastest": (f"Fastest route: {fastest['total_time']} min, max road risk "
                    f"{fastest['max_risk']}/100"
                    + (" — crosses a high-confidence hazard zone."
                       if fastest["max_risk"] >= 50 else " — currently clear.")),
        "safe": (f"Recommended safe route: {safe['total_time']} min, max road "
                 f"risk {safe['max_risk']}/100."
                 + (f" Adds {extra} min but avoids all verified hazards."
                    if extra > 0 and not same else " Already the fastest clear path.")),
        "recommended": "safe",
        "same_route": same,
    }
    return {"fastest": fastest, "safe": safe, "avoided": cmp["avoided"],
            "explanation": explanation}


# -- simulation --------------------------------------------------------------
@api.get("/simulation/status")
async def sim_status():
    return {**world.sim, "sim_time": world.sim_time.isoformat(),
            "connections": manager.count,
            "summary": world.dashboard_summary()}


@api.post("/simulation/start")
async def sim_start(payload: SimulationStartRequest):
    await sim.start(scenario=payload.scenario, speed=payload.speed)
    return {"ok": True, "sim": {**world.sim,
                                "sim_time": world.sim_time.isoformat()}}


@api.post("/simulation/pause")
async def sim_pause():
    await sim.pause()
    return {"ok": True, "status": world.sim["status"]}


@api.post("/simulation/reset")
async def sim_reset():
    await sim.reset()
    return {"ok": True, "status": world.sim["status"]}


@api.post("/simulation/speed")
async def sim_speed(payload: SimulationSpeedRequest):
    await sim.set_speed(payload.speed)
    return {"ok": True, "speed": world.sim["speed"]}


@api.post("/simulation/inject")
async def sim_inject(payload: InjectRequest):
    inc = sim.inject(payload.inject_type,
                     road_segment_id=payload.road_segment_id,
                     incident_id=payload.incident_id)
    await push()
    if inc is None:
        return {"ok": False, "message": "No target incident available."}
    return {"ok": True, "incident": world.serialize_incident(inc, detail=True)}


# -- response actions --------------------------------------------------------
async def _response_action(incident_id, status, verb, level, payload):
    inc = world.incidents.get(incident_id)
    if not inc:
        raise HTTPException(404, "Incident not found")
    inc["response_status"] = status
    if status == "RESOLVED":
        world._resolve_incident(inc)
    inc["acknowledged_by"] = payload.operator
    action = {
        "id": f"ACT-{len(world.response_actions) + 1}",
        "incident_id": incident_id,
        "status": status,
        "operator": payload.operator,
        "note": payload.note,
        "timestamp": world.sim_time.isoformat(),
    }
    world.response_actions.append(action)
    world._log_event("RESPONSE",
                     f"{payload.operator} marked {incident_id} on "
                     f"{inc['road_name']} as {verb}.",
                     level, incident_id=incident_id)
    try:
        await db.response_actions.insert_one({**action})
    except Exception:
        logger.exception("response action persist failed")
    await push()
    return {"ok": True, "incident": world.serialize_incident(inc, detail=True)}


@api.post("/response/{incident_id}/acknowledge")
async def resp_ack(incident_id: str, payload: ResponseActionRequest):
    return await _response_action(incident_id, "ACKNOWLEDGED", "ACKNOWLEDGED",
                                  "info", payload)


@api.post("/response/{incident_id}/dispatch")
async def resp_dispatch(incident_id: str, payload: ResponseActionRequest):
    return await _response_action(incident_id, "DISPATCHED",
                                  "RESPONSE DISPATCHED", "warning", payload)


@api.post("/response/{incident_id}/monitor")
async def resp_monitor(incident_id: str, payload: ResponseActionRequest):
    return await _response_action(incident_id, "MONITORING", "MONITORING",
                                  "info", payload)


@api.post("/response/{incident_id}/resolve")
async def resp_resolve(incident_id: str, payload: ResponseActionRequest):
    return await _response_action(incident_id, "RESOLVED", "RESOLVED",
                                  "success", payload)


# -- citizen reporting -------------------------------------------------------
@api.post("/citizen/report")
async def citizen_report(payload: CitizenReport):
    obs = world._make_observation(
        "CITIZEN", payload.hazard_type, payload.latitude, payload.longitude,
        "CITIZEN", None, severity=payload.severity, source="CITIZEN")
    inc, is_new, prev_c, prev_s = world.add_observation(obs)
    if inc is None:
        return {"ok": False, "message": "No matching hazard to update."}
    world._log_event(
        "DETECTION",
        f"Citizen report ({payload.reporter_name}) — "
        f"{inc.get('hazard_type')} on {inc['road_name']} entered the fusion "
        f"pipeline at lower reliability ({inc['confidence']}% fused).",
        "info", incident_id=inc["id"])
    try:
        await db.citizen_reports.insert_one({
            "hazard_type": payload.hazard_type,
            "latitude": payload.latitude, "longitude": payload.longitude,
            "severity": payload.severity, "description": payload.description,
            "reporter_name": payload.reporter_name,
            "incident_id": inc["id"],
            "timestamp": world.sim_time.isoformat(),
        })
    except Exception:
        logger.exception("citizen report persist failed")
    await push()
    return {"ok": True, "incident": world.serialize_incident(inc, detail=True),
            "is_new": is_new}


# -- analytics ---------------------------------------------------------------
@api.get("/analytics/summary")
async def analytics_summary():
    active = world.active_incidents()
    by_type = {}
    for i in active:
        by_type[i["hazard_type"]] = by_type.get(i["hazard_type"], 0) + 1
    ver = {"UNVERIFIED": 0, "CORROBORATED": 0, "VERIFIED": 0,
           "CONFLICTING": 0, "STALE": 0}
    for i in active:
        ver[i.get("verification_status", "UNVERIFIED")] = \
            ver.get(i.get("verification_status", "UNVERIFIED"), 0) + 1
    risk_dist = {"SAFE": 0, "CAUTION": 0, "UNSAFE": 0}
    for e in world.graph.edges.values():
        risk_dist[risk_state(e["risk"])] += 1
    prio = {"P1": 0, "P2": 0, "P3": 0, "P4": 0}
    for i in active:
        prio[i.get("priority", "P4")] = prio.get(i.get("priority", "P4"), 0) + 1

    # Confidence evolution = timeline of the highest-priority active incident.
    top = sorted(active, key=lambda x: x.get("priority_score", 0), reverse=True)
    timeline = []
    if top:
        det = world.serialize_incident(top[0], detail=True)
        timeline = det.get("confidence_timeline", [])
    return {
        "hazards_by_type": [{"type": k, "label": k.replace("_", " ").title(),
                             "count": v} for k, v in sorted(by_type.items())],
        "verification": [{"state": k, "count": v} for k, v in ver.items()],
        "risk_distribution": [{"state": k, "count": v}
                              for k, v in risk_dist.items()],
        "priority_distribution": [{"level": k, "count": v}
                                  for k, v in prio.items()],
        "confidence_evolution": timeline,
        "incident_for_evolution": top[0]["id"] if top else None,
    }


# -- websocket ---------------------------------------------------------------
@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_json({"type": "state", **world.snapshot()})
        while True:
            await websocket.receive_text()  # keepalive / detect disconnect
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception:
        await manager.disconnect(websocket)


# ------------------------------------------------------------------ lifecycle
@app.on_event("startup")
async def on_startup():
    """Seed MongoDB with the freshly built deterministic world."""
    try:
        await db.world_state.replace_one(
            {"_id": "latest"},
            {**world.snapshot(), "_id": "latest",
             "persisted_at": datetime.now(timezone.utc).isoformat()},
            upsert=True)
        logger.info("ResQDrive world seeded to MongoDB (db=%s).",
                    os.environ["DB_NAME"])
    except Exception:
        logger.exception("startup seed failed")


@app.on_event("shutdown")
async def on_shutdown():
    client.close()


app.include_router(api)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)
