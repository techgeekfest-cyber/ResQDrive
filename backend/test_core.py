"""ResQDrive CORE POC test.

Validates the make-or-break backend algorithms IN ISOLATION before building the
full application:

  1. Single-vehicle detection confidence.
  2. Multi-vehicle corroboration RAISES confidence (independence-aware).
  3. Conflicting evidence LOWERS confidence and yields a CONFLICTING state.
  4. Temporal freshness decays and recovers; stale incidents detected.
  5. Risk scoring produces sensible SAFE / CAUTION / UNSAFE bands.
  6. Risk-aware routing AVOIDS an unsafe (flooded) segment.

Run:  cd /app/backend && python test_core.py
"""
from datetime import datetime, timedelta, timezone

from engines.fusion import fuse_observations, cluster_observations
from engines.freshness import freshness_weight, freshness_bucket
from engines.risk import compute_risk, risk_state, compute_priority
from engines.routing import RoadGraph

NOW = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)

# Hyderabad-ish coordinates around one flooded junction.
BASE_LAT, BASE_LON = 17.3850, 78.4867


def obs(vid, hazard, conf, sensor, minutes_ago, dlat=0.0, dlon=0.0,
        sev="HIGH", quality=1.0):
    return {
        "vehicle_id": vid,
        "hazard_type": hazard,
        "latitude": BASE_LAT + dlat,
        "longitude": BASE_LON + dlon,
        "confidence": conf,
        "sensor_type": sensor,
        "severity": sev,
        "sensor_quality": quality,
        "timestamp": NOW - timedelta(minutes=minutes_ago),
    }


def approx(a, b, tol):
    return abs(a - b) <= tol


PASS = 0
FAIL = 0


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")


# ---------------------------------------------------------------------------
def test_single_vehicle():
    print("\n[1] Single-vehicle detection")
    r = fuse_observations([obs("RQ-101", "FLOOD", 0.82, "CAMERA", 1)], now=NOW)
    check("confidence ~82%", approx(r["confidence"], 82, 4),
          f"-> {r['confidence']}%")
    check("state UNVERIFIED", r["verification_state"] == "UNVERIFIED",
          f"-> {r['verification_state']}")
    check("evidence_count == 1", r["evidence_count"] == 1)
    check("hazard is FLOOD", r["hazard_type"] == "FLOOD")


def test_corroboration():
    print("\n[2] Multi-vehicle corroboration raises confidence")
    o1 = obs("RQ-101", "FLOOD", 0.82, "CAMERA", 1)
    o2 = obs("RQ-104", "FLOOD", 0.80, "CAMERA", 1, dlat=0.0003)
    o3 = obs("RQ-109", "FLOOD", 0.84, "CAMERA", 1, dlon=0.0003)
    o4 = obs("RQ-112", "FLOOD", 0.83, "IMU", 1, dlat=0.0002, dlon=0.0002)

    c1 = fuse_observations([o1], now=NOW)["confidence"]
    c2 = fuse_observations([o1, o2], now=NOW)["confidence"]
    r3 = fuse_observations([o1, o2, o3], now=NOW)
    c3 = r3["confidence"]
    r4 = fuse_observations([o1, o2, o3, o4], now=NOW)
    c4 = r4["confidence"]

    print(f"      1 veh={c1}%  2 veh={c2}%  3 veh={c3}%  4 veh={c4}%")
    check("monotonically increasing", c1 < c2 < c3 < c4)
    check("2 vehicles ~89%", approx(c2, 89, 5), f"-> {c2}%")
    check("3 vehicles ~93%", approx(c3, 93, 5), f"-> {c3}%")
    check("4 vehicles 95-99%", 95 <= c4 <= 99, f"-> {c4}%")
    check("3 vehicles CORROBORATED/VERIFIED",
          r3["verification_state"] in ("CORROBORATED", "VERIFIED"),
          f"-> {r3['verification_state']}")
    check("4 vehicles VERIFIED", r4["verification_state"] == "VERIFIED",
          f"-> {r4['verification_state']}")
    check("NOT a simple average (fused > mean)",
          c2 > 81, f"mean~81 vs fused {c2}")


def test_conflict():
    print("\n[3] Conflicting evidence lowers confidence")
    o1 = obs("RQ-101", "FLOOD", 0.85, "CAMERA", 1)
    o2 = obs("RQ-104", "FLOOD", 0.85, "CAMERA", 1, dlat=0.0003)
    clear = obs("RQ-120", "CLEAR", 0.80, "CAMERA", 1, dlon=0.0003)

    no_conflict = fuse_observations([o1, o2], now=NOW)
    with_conflict = fuse_observations([o1, o2, clear], now=NOW)

    print(f"      no-conflict={no_conflict['confidence']}% "
          f"conflict={with_conflict['confidence']}% "
          f"agreement={with_conflict['agreement']}%")
    check("conflict reduces confidence",
          with_conflict["confidence"] < no_conflict["confidence"])
    check("state CONFLICTING",
          with_conflict["verification_state"] == "CONFLICTING",
          f"-> {with_conflict['verification_state']}")
    check("agreement ~67%", approx(with_conflict["agreement"], 67, 6),
          f"-> {with_conflict['agreement']}%")
    check("conflict_count == 1", with_conflict["conflict_count"] == 1)


def test_freshness():
    print("\n[4] Temporal freshness decay + recovery")
    w0 = freshness_weight(0)
    w20 = freshness_weight(20)
    w60 = freshness_weight(60)
    print(f"      weight(0)={w0:.3f} weight(20)={w20:.3f} weight(60)={w60:.3f}")
    check("weight decreases with age", w0 > w20 > w60)
    check("weight(0) == 1.0", approx(w0, 1.0, 0.001))
    check("buckets correct",
          freshness_bucket(2) == "VERY_FRESH"
          and freshness_bucket(10) == "FRESH"
          and freshness_bucket(20) == "AGING"
          and freshness_bucket(45) == "STALE"
          and freshness_bucket(90) == "EXPIRED")

    # All-old cluster -> STALE
    old = [obs("RQ-1", "FLOOD", 0.9, "CAMERA", 75),
           obs("RQ-2", "FLOOD", 0.9, "CAMERA", 80, dlat=0.0003)]
    r_old = fuse_observations(old, now=NOW)
    check("all-stale cluster => STALE state",
          r_old["verification_state"] == "STALE",
          f"-> {r_old['verification_state']} (freshness {r_old['freshness']})")

    # A fresh observation restores confidence/freshness.
    recovered = old + [obs("RQ-3", "FLOOD", 0.9, "CAMERA", 1, dlon=0.0003)]
    r_new = fuse_observations(recovered, now=NOW)
    check("fresh observation recovers freshness",
          r_new["freshness"] > r_old["freshness"],
          f"{r_old['freshness']} -> {r_new['freshness']}")
    check("fresh observation recovers confidence/state",
          r_new["verification_state"] != "STALE",
          f"-> {r_new['verification_state']}")


def test_risk():
    print("\n[5] Risk scoring bands")
    high = compute_risk("CRITICAL", 0.94, 0.98, 1.0, 0.90)
    mod = compute_risk("MODERATE", 0.55, 0.55, 0.70, 0.75)
    low = compute_risk("LOW", 0.40, 0.30, 0.60, 0.70)
    print(f"      high={high} moderate={mod} low={low}")
    check("high risk UNSAFE", risk_state(high) == "UNSAFE", f"-> {high}")
    check("moderate risk CAUTION", risk_state(mod) == "CAUTION", f"-> {mod}")
    check("low risk SAFE", risk_state(low) == "SAFE", f"-> {low}")
    check("higher confidence => higher risk",
          compute_risk("HIGH", 0.95, 0.9, 1.0, 0.9)
          > compute_risk("HIGH", 0.50, 0.9, 1.0, 0.9))

    # Priority engine: hospital-proximate critical flood => P1
    p = compute_priority(risk=93, severity="CRITICAL", traffic_impact=0.8,
                         freshness=0.95, infrastructure=0.9)
    check("critical incident near infra => P1", p["level"] == "P1",
          f"-> {p['level']} ({p['score']})")


def test_routing():
    print("\n[6] Risk-aware routing avoids unsafe segment")
    g = RoadGraph()
    g.add_node("A", 17.40, 78.48, "Start")
    g.add_node("B", 17.41, 78.49, "North Junction")
    g.add_node("C", 17.39, 78.49, "South Junction")
    g.add_node("D", 17.40, 78.50, "Destination")
    # Safe northern corridor (longer): A-B-D
    g.add_edge("e1", "A", "B", base_time=7, risk=10, name="North Rd 1")
    g.add_edge("e2", "B", "D", base_time=7, risk=15, name="North Rd 2")
    # Fast southern corridor (shorter) but C-D is flooded/unsafe.
    g.add_edge("e3", "A", "C", base_time=5, risk=12, name="South Rd 1")
    g.add_edge("e4", "C", "D", base_time=5, risk=91, name="South Rd 2 (FLOODED)")

    cmp = g.plan_comparison("A", "D")
    fastest, safe, avoided = cmp["fastest"], cmp["safe"], cmp["avoided"]
    print(f"      fastest edges={fastest['edges']} time={fastest['total_time']} "
          f"maxrisk={fastest['max_risk']}")
    print(f"      safe    edges={safe['edges']} time={safe['total_time']} "
          f"maxrisk={safe['max_risk']}")
    print(f"      avoided={avoided}")
    check("fastest uses flooded edge e4", "e4" in fastest["edges"])
    check("safe route avoids flooded edge e4", "e4" not in safe["edges"])
    check("safe route uses northern corridor",
          set(safe["edges"]) == {"e1", "e2"})
    check("safe route is slower than fastest",
          safe["total_time"] > fastest["total_time"])
    check("safe route has lower max risk",
          safe["max_risk"] < fastest["max_risk"])
    check("avoided list reports flooded segment",
          any(a["id"] == "e4" for a in avoided))


def test_clustering():
    print("\n[7] Spatial clustering separates distant incidents")
    near = [obs("RQ-1", "FLOOD", 0.8, "CAMERA", 1),
            obs("RQ-2", "FLOOD", 0.8, "CAMERA", 1, dlat=0.0005)]
    far = [obs("RQ-9", "LANDSLIDE", 0.8, "CAMERA", 1, dlat=0.05, dlon=0.05)]
    clusters = cluster_observations(near + far)
    check("two separate clusters formed", len(clusters) == 2,
          f"-> {len(clusters)} clusters")


def main():
    print("=" * 62)
    print(" ResQDrive CORE POC  -  Evidence Fusion / Risk / Routing")
    print("=" * 62)
    test_single_vehicle()
    test_corroboration()
    test_conflict()
    test_freshness()
    test_risk()
    test_routing()
    test_clustering()
    print("\n" + "=" * 62)
    print(f" RESULT: {PASS} passed, {FAIL} failed")
    print("=" * 62)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
