import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { useApp } from "@/context/AppContext";
import { RiskBadge } from "@/components/RiskBadge";
import { DynIcon } from "@/components/DynIcon";
import { HAZARD_META } from "@/lib/constants";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const HAZARD_OPTIONS = Object.keys(HAZARD_META).filter((h) => h !== "CLEAR");
const SEVERITIES = ["LOW", "MODERATE", "HIGH", "CRITICAL"];

export default function Citizen() {
  const { incidents } = useApp();
  const navigate = useNavigate();
  const [nodes, setNodes] = useState([]);
  const [start, setStart] = useState("GACHI");
  const [dest, setDest] = useState("KOTI");
  const [route, setRoute] = useState(null);
  const [form, setForm] = useState({ hazard_type: "FLOOD", location: "KOTI", severity: "MODERATE", description: "", reporter_name: "" });
  const [busy, setBusy] = useState(false);

  useEffect(() => { api.routesMeta().then((d) => setNodes(d.nodes || [])).catch(() => {}); }, []);

  const nodeMap = useMemo(() => Object.fromEntries(nodes.map((n) => [n.id, n])), [nodes]);

  const findRoute = async () => {
    if (start === dest) { toast.error("Choose different points"); return; }
    try { setRoute(await api.planRoute(start, dest)); } catch { toast.error("No route available"); }
  };
  useEffect(() => { if (nodes.length) findRoute(); /* eslint-disable-next-line */ }, [nodes.length]);

  const submitReport = async () => {
    const loc = nodeMap[form.location];
    if (!loc) return;
    setBusy(true);
    try {
      await api.citizenReport({
        hazard_type: form.hazard_type,
        latitude: 17.41, longitude: 78.47,
        severity: form.severity, description: form.description,
        reporter_name: form.reporter_name || "Anonymous Citizen",
      });
      toast.success("Report submitted — entered the fusion pipeline at citizen reliability.");
      setForm((f) => ({ ...f, description: "" }));
    } catch { toast.error("Could not submit report"); }
    finally { setBusy(false); }
  };

  const nearby = incidents.filter((i) => i.response_status !== "RESOLVED").slice(0, 5);

  return (
    <div className="mx-auto max-w-[1100px] px-3 py-6 lg:px-5">
      <div className="mb-1 flex items-center gap-2">
        <DynIcon name="Users" className="h-5 w-5 text-[hsl(190_85%_60%)]" />
        <h1 className="text-xl font-semibold tracking-tight">Citizen View</h1>
      </div>
      <p className="mb-5 text-[13px] text-muted-foreground">A simplified driver-facing view — safer routes and road conditions, without the internal technical detail.</p>

      <div className="grid gap-4 lg:grid-cols-2">
        {/* Route */}
        <div className="rq-panel p-4">
          <div className="rq-label mb-3">Plan your trip</div>
          <div className="grid grid-cols-2 gap-2">
            <Select value={start} onValueChange={setStart}><SelectTrigger className="bg-secondary"><SelectValue placeholder="From" /></SelectTrigger><SelectContent className="max-h-72">{nodes.map((n) => <SelectItem key={n.id} value={n.id}>{n.name}</SelectItem>)}</SelectContent></Select>
            <Select value={dest} onValueChange={setDest}><SelectTrigger className="bg-secondary"><SelectValue placeholder="To" /></SelectTrigger><SelectContent className="max-h-72">{nodes.map((n) => <SelectItem key={n.id} value={n.id}>{n.name}</SelectItem>)}</SelectContent></Select>
          </div>
          <Button onClick={findRoute} className="mt-3 w-full gap-2"><DynIcon name="Navigation" className="h-4 w-4" /> Find Safe Route</Button>

          {route && (
            <div className="mt-4 space-y-2">
              <div className="flex items-center justify-between rounded-lg border border-border bg-secondary p-3">
                <div><div className="rq-label">Fastest route</div><div className="mono text-xl font-semibold">{route.fastest.total_time} min</div></div>
                <RiskBadge state={route.fastest.max_risk >= 80 ? "UNSAFE" : route.fastest.max_risk >= 50 ? "CAUTION" : "SAFE"} score={route.fastest.max_risk} />
              </div>
              <div className="flex items-center justify-between rounded-lg border border-[hsl(150_50%_30%)] bg-[hsl(152_45%_10%)] p-3">
                <div><div className="rq-label">Recommended safe route</div><div className="mono text-xl font-semibold text-[hsl(150_70%_60%)]">{route.safe.total_time} min</div></div>
                <RiskBadge state={route.safe.max_risk >= 80 ? "UNSAFE" : route.safe.max_risk >= 50 ? "CAUTION" : "SAFE"} score={route.safe.max_risk} />
              </div>
              <p className="text-[12.5px] text-muted-foreground"><DynIcon name="Info" className="mr-1 inline h-4 w-4" />{route.explanation?.safe}</p>
              <div className="flex gap-2">
                <Button variant="secondary" className="flex-1 gap-1.5" onClick={() => toast.success("Safe route selected")}><DynIcon name="ShieldCheck" className="h-4 w-4" /> Use Safe Route</Button>
                <Button variant="outline" className="flex-1 gap-1.5 border-border" onClick={() => navigate("/hazards")}><DynIcon name="TriangleAlert" className="h-4 w-4" /> View Hazards</Button>
              </div>
            </div>
          )}
        </div>

        {/* Report */}
        <div className="rq-panel p-4" data-testid="citizen-hazard-report-form">
          <div className="rq-label mb-3 flex items-center gap-1.5"><DynIcon name="MessageSquarePlus" className="h-4 w-4" /> Report a road condition</div>
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-2">
              <div><div className="rq-label mb-1">Hazard</div><Select value={form.hazard_type} onValueChange={(v) => setForm({ ...form, hazard_type: v })}><SelectTrigger className="bg-secondary"><SelectValue /></SelectTrigger><SelectContent>{HAZARD_OPTIONS.map((h) => <SelectItem key={h} value={h}>{HAZARD_META[h].label}</SelectItem>)}</SelectContent></Select></div>
              <div><div className="rq-label mb-1">Severity</div><Select value={form.severity} onValueChange={(v) => setForm({ ...form, severity: v })}><SelectTrigger className="bg-secondary"><SelectValue /></SelectTrigger><SelectContent>{SEVERITIES.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}</SelectContent></Select></div>
            </div>
            <div><div className="rq-label mb-1">Location</div><Select value={form.location} onValueChange={(v) => setForm({ ...form, location: v })}><SelectTrigger className="bg-secondary"><SelectValue /></SelectTrigger><SelectContent className="max-h-72">{nodes.map((n) => <SelectItem key={n.id} value={n.id}>{n.name}</SelectItem>)}</SelectContent></Select></div>
            <div><div className="rq-label mb-1">Your name (optional)</div><Input value={form.reporter_name} onChange={(e) => setForm({ ...form, reporter_name: e.target.value })} placeholder="Anonymous Citizen" className="bg-secondary" /></div>
            <div><div className="rq-label mb-1">Description (optional)</div><Textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="What did you observe?" className="bg-secondary" rows={2} /></div>
            <Button onClick={submitReport} disabled={busy} className="w-full gap-2" data-testid="citizen-hazard-report-submit"><DynIcon name="Send" className="h-4 w-4" /> {busy ? "Submitting…" : "Submit Report"}</Button>
            <p className="text-[11px] text-muted-foreground">Citizen reports enter the same evidence pipeline at lower reliability (0.55) than verified sensor observations.</p>
          </div>
        </div>
      </div>

      <div className="mt-4 rq-panel p-4">
        <div className="rq-label mb-2">Hazards near you</div>
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {nearby.map((i) => (
            <div key={i.id} className="flex items-center justify-between rounded-lg border border-border bg-secondary px-3 py-2 text-[12.5px]">
              <span className="flex items-center gap-1.5"><DynIcon name={HAZARD_META[i.hazard_type]?.icon || "TriangleAlert"} className="h-4 w-4 text-[hsl(190_85%_60%)]" />{HAZARD_META[i.hazard_type]?.label || i.hazard_type}</span>
              <RiskBadge state={i.risk_state} />
            </div>
          ))}
          {nearby.length === 0 && <div className="text-[12.5px] text-muted-foreground">No active hazards reported.</div>}
        </div>
      </div>
    </div>
  );
}
