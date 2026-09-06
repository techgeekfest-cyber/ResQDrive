import React, { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { useApp } from "@/context/AppContext";
import { HAZARD_META, STATUS_COLORS, PRIORITY_META } from "@/lib/constants";
import { RiskBadge } from "@/components/RiskBadge";
import { VerificationBadge } from "@/components/VerificationBadge";
import { ConfidenceRing } from "@/components/ConfidenceRing";
import { ConfidenceBreakdown } from "@/components/ConfidenceBreakdown";
import { DynIcon } from "@/components/DynIcon";
import { fmtCoord, relAge, titleCase } from "@/lib/format";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";

function RiskComponentBars({ comps = {} }) {
  const rows = [
    ["severity", "Severity", 35], ["confidence", "Detection Confidence", 25],
    ["freshness", "Freshness", 15], ["agreement", "Evidence Agreement", 20],
    ["sensor_reliability", "Sensor Reliability", 5],
  ];
  return (
    <div className="space-y-2">
      {rows.map(([k, label, max]) => (
        <div key={k} className="flex items-center gap-2 text-[12px]">
          <span className="w-36 text-muted-foreground">{label}</span>
          <div className="h-2 flex-1 overflow-hidden rounded-full bg-secondary">
            <div className="h-full rounded-full bg-[hsl(190_85%_50%)]" style={{ width: `${Math.min(100, ((comps[k] || 0) / max) * 100)}%` }} />
          </div>
          <span className="mono w-8 text-right">{comps[k] || 0}</span>
        </div>
      ))}
    </div>
  );
}

export function IncidentDrawer({ incidentId, open, onOpenChange, onFocus }) {
  const { incidents, role, actions } = useApp();
  const navigate = useNavigate();
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(false);

  const live = useMemo(
    () => incidents.find((i) => i.id === incidentId),
    [incidents, incidentId],
  );

  useEffect(() => {
    if (!open || !incidentId) return;
    let active = true;
    setLoading(true);
    api.incident(incidentId)
      .then((d) => { if (active) setDetail(d); })
      .catch(() => {})
      .finally(() => active && setLoading(false));
    const t = setInterval(() => {
      api.incident(incidentId).then((d) => active && setDetail(d)).catch(() => {});
    }, 3000);
    return () => { active = false; clearInterval(t); };
  }, [open, incidentId]);

  const inc = detail || live;
  const canAct = ["AUTHORITY", "ADMIN", "OPERATOR"].includes(role);

  const doAction = async (action, label) => {
    if (!canAct) { toast.error(`Switch to Authority/Operator role to ${label}.`); return; }
    try {
      await actions.respond(incidentId, action, { operator: role });
      toast.success(`Incident ${label}`);
    } catch { toast.error("Action failed"); }
  };

  if (!inc) {
    return (
      <Sheet open={open} onOpenChange={onOpenChange}>
        <SheetContent side="right" className="w-full border-border sm:max-w-[440px]" data-testid="incident-intelligence-drawer">
          <div className="grid h-full place-items-center text-muted-foreground">
            {loading ? "Loading incident…" : "Select an incident"}
          </div>
        </SheetContent>
      </Sheet>
    );
  }

  const meta = HAZARD_META[inc.hazard_type] || {};
  const c = STATUS_COLORS[inc.risk_state] || STATUS_COLORS.UNKNOWN;
  const observations = detail?.observations || [];
  const timeline = detail?.confidence_timeline || [];

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-full overflow-y-auto border-border bg-[hsl(220_16%_9%)] p-0 sm:max-w-[460px]" data-testid="incident-intelligence-drawer">
        <SheetHeader className="border-b border-border p-4">
          <SheetTitle className="flex items-center gap-2">
            <span className="grid h-8 w-8 place-items-center rounded-lg" style={{ background: c.solid + "22" }}>
              <DynIcon name={meta.icon || "TriangleAlert"} className="h-4 w-4" style={{ color: c.solid }} />
            </span>
            <div>
              <div className="text-[15px]">{meta.label || inc.hazard_type}</div>
              <div className="mono text-[11px] font-normal text-muted-foreground">{inc.id} · {inc.road_name}</div>
            </div>
          </SheetTitle>
        </SheetHeader>

        <div className="flex items-center gap-2 border-b border-border p-4">
          <ConfidenceRing value={inc.confidence} size={56} stroke={5} />
          <div className="flex flex-1 flex-wrap gap-1.5">
            <RiskBadge state={inc.risk_state} score={inc.risk_score} />
            <VerificationBadge state={inc.verification_status} />
            <span className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-semibold" style={{ borderColor: (PRIORITY_META[inc.priority]?.color || "#888") + "66", color: PRIORITY_META[inc.priority]?.color }}>
              <DynIcon name="Flag" className="h-3 w-3" /> {inc.priority}
            </span>
          </div>
        </div>

        <Tabs defaultValue="summary" className="p-4">
          <TabsList className="grid w-full grid-cols-4 bg-secondary">
            <TabsTrigger value="summary" className="text-[11px]" data-testid="tab-summary">Summary</TabsTrigger>
            <TabsTrigger value="evidence" className="text-[11px]" data-testid="tab-evidence">Evidence</TabsTrigger>
            <TabsTrigger value="why" className="text-[11px]" data-testid="tab-why">Why?</TabsTrigger>
            <TabsTrigger value="timeline" className="text-[11px]" data-testid="tab-timeline">Timeline</TabsTrigger>
          </TabsList>

          <TabsContent value="summary" className="mt-4 space-y-4">
            <div className="rq-panel p-3">
              <div className="rq-label mb-2">Road Risk Breakdown · {inc.risk_score}/100</div>
              <RiskComponentBars comps={inc.risk_components} />
            </div>
            <div className="grid grid-cols-2 gap-2 text-[12px]">
              <Info label="Severity" value={titleCase(inc.severity)} />
              <Info label="Evidence" value={`${inc.evidence_count} vehicles`} />
              <Info label="Agreement" value={`${inc.agreement}%`} />
              <Info label="Freshness" value={`${inc.freshness}%`} />
              <Info label="First detected" value={relAge(inc.created_min_ago)} />
              <Info label="Last confirmed" value={relAge(inc.age_min)} />
              <Info label="Location" value={`${fmtCoord(inc.latitude)}, ${fmtCoord(inc.longitude)}`} mono span />
            </div>
            <div className="rounded-lg border p-3 text-[12.5px]" style={{ borderColor: c.border, background: c.bg }}>
              <div className="mb-1 flex items-center gap-1.5 font-semibold" style={{ color: c.fg }}>
                <DynIcon name="Lightbulb" className="h-4 w-4" /> Recommended action
              </div>
              <div style={{ color: c.fg }}>{inc.recommended_action}</div>
            </div>
            {inc.nearby_infrastructure?.length > 0 && (
              <div className="rq-panel p-3">
                <div className="rq-label mb-2">Nearby critical infrastructure</div>
                <ul className="space-y-1.5 text-[12px]">
                  {inc.nearby_infrastructure.slice(0, 4).map((f) => (
                    <li key={f.id} className="flex items-center justify-between">
                      <span className="flex items-center gap-1.5"><DynIcon name="Hospital" className="h-3.5 w-3.5 text-[hsl(8_70%_60%)]" />{f.name}</span>
                      <span className="mono text-muted-foreground">{f.distance_m} m</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <div className="grid grid-cols-2 gap-2">
              <Button variant="outline" className="gap-1.5 border-border" onClick={() => { onOpenChange(false); navigate("/routes"); }} data-testid="drawer-avoid-road-button">
                <DynIcon name="Route" className="h-4 w-4" /> Avoid Road
              </Button>
              <Button className="gap-1.5 bg-[hsl(8_75%_46%)] text-white hover:bg-[hsl(8_75%_52%)]" onClick={() => doAction("dispatch", "dispatched")} data-testid="drawer-dispatch-button">
                <DynIcon name="Siren" className="h-4 w-4" /> Dispatch
              </Button>
              <Button variant="secondary" className="gap-1.5" onClick={() => doAction("acknowledge", "acknowledged")} data-testid="drawer-acknowledge-button">
                <DynIcon name="Check" className="h-4 w-4" /> Acknowledge
              </Button>
              <Button variant="secondary" className="gap-1.5" onClick={() => doAction("resolve", "resolved")} data-testid="drawer-resolve-button">
                <DynIcon name="CircleCheck" className="h-4 w-4" /> Resolve
              </Button>
            </div>
            <div className="text-center text-[11px] text-muted-foreground">Response status: <span className="font-semibold text-foreground">{titleCase(inc.response_status)}</span></div>
          </TabsContent>

          <TabsContent value="evidence" className="mt-4 space-y-4">
            <div className="rq-panel p-3">
              <div className="rq-label mb-2">Evidence graph · {inc.evidence_count} independent vehicles</div>
              <div className="flex flex-wrap items-center justify-center gap-2">
                {(inc.supporting_vehicles || []).map((v) => (
                  <div key={v} className="mono rounded-md border border-[hsl(150_50%_30%)] bg-[hsl(152_45%_11%)] px-2 py-1 text-[11px] text-[hsl(150_70%_70%)]">{v}</div>
                ))}
              </div>
              <div className="my-2 text-center text-muted-foreground"><DynIcon name="ArrowDown" className="inline h-4 w-4" /></div>
              <div className="rounded-lg border border-border bg-secondary p-2 text-center text-[12px]">
                {inc.observation_count} observations → <span className="font-semibold text-[hsl(190_85%_60%)]">{inc.confidence}% confidence</span> → {inc.verification_status}
              </div>
              {inc.conflicting_vehicles?.length > 0 && (
                <div className="mt-2 flex flex-wrap items-center gap-2">
                  <span className="text-[11px] text-[hsl(45_90%_60%)]">Conflict:</span>
                  {inc.conflicting_vehicles.map((v) => (
                    <div key={v} className="mono rounded-md border border-[hsl(45_50%_32%)] bg-[hsl(42_50%_11%)] px-2 py-1 text-[11px] text-[hsl(45_90%_70%)]">{v} · clear</div>
                  ))}
                </div>
              )}
            </div>
            <div className="rq-panel p-3">
              <div className="rq-label mb-2">Sensor evidence</div>
              <div className="flex flex-wrap gap-2">
                {Object.entries(inc.sensor_evidence || {}).map(([k, v]) => (
                  <span key={k} className="mono rounded-md bg-secondary px-2 py-1 text-[11px]">{k} × {v}</span>
                ))}
              </div>
            </div>
            <div>
              <div className="rq-label mb-2">Observations ({observations.length})</div>
              <div className="space-y-1.5">
                {observations.map((o) => (
                  <div key={o.id} className="flex items-center gap-2 rounded-lg border border-border bg-secondary px-2.5 py-2 text-[12px]">
                    <DynIcon name={o.source === "CITIZEN" ? "User" : "Cctv"} className="h-3.5 w-3.5 text-muted-foreground" />
                    <span className="mono">{o.vehicle_id}</span>
                    <span className="rounded bg-white/5 px-1 text-[10px]">{o.sensor_type}</span>
                    <span className="text-muted-foreground">{o.hazard_label}</span>
                    <span className="mono ml-auto">{o.confidence}%</span>
                    <span className="text-[10px] text-muted-foreground">{relAge(o.age_min)}</span>
                  </div>
                ))}
                {observations.length === 0 && <div className="text-[12px] text-muted-foreground">Loading observations…</div>}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="why" className="mt-4 space-y-4">
            <div className="rq-panel p-3"><ConfidenceBreakdown breakdown={inc.breakdown} total={inc.confidence} /></div>
            <div className="rq-panel p-3">
              <div className="rq-label mb-2">Why this status</div>
              <ul className="space-y-1.5 text-[12.5px]">
                <CheckLine ok={inc.evidence_count >= 2}>{inc.evidence_count} independent vehicle(s)</CheckLine>
                <CheckLine ok={inc.confidence >= 70}>{inc.confidence}% fused confidence</CheckLine>
                <CheckLine ok={inc.freshness >= 40}>Recent observations (freshness {inc.freshness}%)</CheckLine>
                <CheckLine ok={inc.agreement >= 75}>Evidence agreement {inc.agreement}%</CheckLine>
                {inc.conflict_count > 0 && <CheckLine ok={false}>{inc.conflict_count} conflicting report(s)</CheckLine>}
              </ul>
            </div>
          </TabsContent>

          <TabsContent value="timeline" className="mt-4 space-y-4">
            <div className="rq-panel p-3">
              <div className="rq-label mb-2">Confidence timeline</div>
              {timeline.length > 1 ? (
                <div className="space-y-1">
                  {timeline.slice(-8).map((t, i) => (
                    <div key={i} className="flex items-center gap-2 text-[12px]">
                      <span className="mono w-16 text-muted-foreground">{relAge(t.age_min)}</span>
                      <div className="h-2 flex-1 overflow-hidden rounded-full bg-secondary">
                        <div className="h-full rounded-full bg-[hsl(190_85%_50%)]" style={{ width: `${t.value}%` }} />
                      </div>
                      <span className="mono w-9 text-right">{t.value}%</span>
                    </div>
                  ))}
                </div>
              ) : <div className="text-[12px] text-muted-foreground">Confidence history accumulates as new evidence arrives.</div>}
            </div>
            <div>
              <div className="rq-label mb-2">Observation timeline</div>
              <ol className="relative space-y-3 border-l border-border pl-4">
                {observations.map((o) => (
                  <li key={o.id} className="relative">
                    <span className="absolute -left-[21px] top-1 h-2.5 w-2.5 rounded-full bg-[hsl(190_85%_55%)] ring-2 ring-[hsl(220_16%_9%)]" />
                    <div className="text-[12px]"><span className="mono">{o.vehicle_id}</span> · {o.sensor_type} · {o.hazard_label}</div>
                    <div className="text-[11px] text-muted-foreground">{o.confidence}% · {relAge(o.age_min)}</div>
                  </li>
                ))}
              </ol>
            </div>
          </TabsContent>
        </Tabs>
      </SheetContent>
    </Sheet>
  );
}

function Info({ label, value, mono, span }) {
  return (
    <div className={`rq-panel px-2.5 py-1.5 ${span ? "col-span-2" : ""}`}>
      <div className="rq-label">{label}</div>
      <div className={`${mono ? "mono" : ""} text-[12.5px] text-foreground`}>{value}</div>
    </div>
  );
}

function CheckLine({ ok, children }) {
  return (
    <li className="flex items-center gap-2">
      <DynIcon name={ok ? "CircleCheck" : "CircleAlert"} className="h-4 w-4" style={{ color: ok ? "hsl(150 70% 52%)" : "hsl(45 90% 58%)" }} />
      <span className={ok ? "text-foreground/90" : "text-[hsl(45_90%_75%)]"}>{children}</span>
    </li>
  );
}

export default IncidentDrawer;
