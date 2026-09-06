import React, { useEffect, useState } from "react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { MapView } from "@/components/MapView";
import { useApp } from "@/context/AppContext";
import { DynIcon } from "@/components/DynIcon";
import { RiskBadge } from "@/components/RiskBadge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

function RouteCard({ title, route, recommended, tone }) {
  if (!route) return null;
  const color = tone === "safe" ? "hsl(150 70% 52%)" : "hsl(190 85% 60%)";
  return (
    <div className={`rq-panel p-4 ${recommended ? "ring-1 ring-[hsl(150_60%_40%)]" : ""}`} data-testid={`route-card-${tone}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 font-semibold">
          <DynIcon name={tone === "safe" ? "ShieldCheck" : "Zap"} className="h-4 w-4" style={{ color }} />{title}
        </div>
        {recommended && <span className="rounded-full bg-[hsl(152_45%_12%)] px-2 py-0.5 text-[11px] font-semibold text-[hsl(150_70%_65%)]">Recommended</span>}
      </div>
      <div className="mt-3 flex items-end gap-4">
        <div><div className="mono text-3xl font-semibold" style={{ color }}>{route.total_time}</div><div className="rq-label">minutes</div></div>
        <div className="mb-1"><RiskBadge state={route.max_risk >= 80 ? "UNSAFE" : route.max_risk >= 50 ? "CAUTION" : "SAFE"} score={route.max_risk} /></div>
      </div>
      <div className="mt-3 border-t border-border pt-2">
        <div className="rq-label mb-1">Via</div>
        <div className="flex flex-wrap items-center gap-1 text-[12px] text-muted-foreground">
          {route.node_details?.map((n, i) => (
            <span key={n.id} className="flex items-center gap-1">{n.name}{i < route.node_details.length - 1 && <DynIcon name="ChevronRight" className="h-3 w-3" />}</span>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function RoutesPage() {
  const { incidents, roads, vehicles, infrastructure } = useApp();
  const [nodes, setNodes] = useState([]);
  const [start, setStart] = useState("GACHI");
  const [dest, setDest] = useState("KOTI");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => { api.routesMeta().then((d) => setNodes(d.nodes || [])).catch(() => {}); }, []);

  const compute = async () => {
    if (start === dest) { toast.error("Choose different start and destination"); return; }
    setBusy(true);
    try { setResult(await api.planRoute(start, dest)); }
    catch (e) { toast.error(e?.response?.data?.detail || "No route available"); }
    finally { setBusy(false); }
  };

  useEffect(() => { compute(); /* eslint-disable-next-line */ }, []);

  return (
    <div className="mx-auto max-w-[1720px] px-3 py-4 lg:px-5">
      <h1 className="text-xl font-semibold tracking-tight">Risk-Aware Safe Routing</h1>
      <p className="mb-4 text-[13px] text-muted-foreground">Route cost = travel time + risk penalty. Unsafe road segments are heavily penalised or avoided.</p>

      <div className="grid gap-3 lg:grid-cols-12">
        <div className="lg:col-span-5 xl:col-span-4">
          <div className="rq-panel p-4">
            <div className="grid gap-3">
              <div>
                <div className="rq-label mb-1">Start</div>
                <Select value={start} onValueChange={setStart}>
                  <SelectTrigger className="bg-secondary" data-testid="routes-start-input"><SelectValue /></SelectTrigger>
                  <SelectContent className="max-h-72">{nodes.map((n) => <SelectItem key={n.id} value={n.id}>{n.name}</SelectItem>)}</SelectContent>
                </Select>
              </div>
              <div>
                <div className="rq-label mb-1">Destination</div>
                <Select value={dest} onValueChange={setDest}>
                  <SelectTrigger className="bg-secondary" data-testid="routes-destination-input"><SelectValue /></SelectTrigger>
                  <SelectContent className="max-h-72">{nodes.map((n) => <SelectItem key={n.id} value={n.id}>{n.name}</SelectItem>)}</SelectContent>
                </Select>
              </div>
              <Button onClick={compute} disabled={busy} className="gap-2" data-testid="routes-compute-button">
                <DynIcon name="Navigation" className="h-4 w-4" /> {busy ? "Computing…" : "Compute Routes"}
              </Button>
            </div>

            {result?.explanation && (
              <div className="mt-4 space-y-2">
                <div className="rounded-lg border border-[hsl(190_40%_28%)] bg-[hsl(190_50%_9%)] p-3 text-[12.5px] text-[hsl(190_60%_80%)]">
                  <DynIcon name="Info" className="mr-1 inline h-4 w-4" />{result.explanation.safe}
                </div>
                {result.avoided?.length > 0 && (
                  <div className="rounded-lg border border-[hsl(8_50%_30%)] bg-[hsl(8_50%_10%)] p-3 text-[12.5px] text-[hsl(8_80%_82%)]">
                    <div className="mb-1 flex items-center gap-1.5 font-semibold"><DynIcon name="Ban" className="h-4 w-4" /> Avoided roads</div>
                    {result.avoided.map((a) => <div key={a.id} className="mono text-[12px]">· {a.name} (risk {a.risk})</div>)}
                  </div>
                )}
              </div>
            )}
          </div>

          {result && (
            <div className="mt-3 grid gap-3">
              <RouteCard title="Fastest Route" route={result.fastest} tone="fastest" recommended={result.explanation?.same_route} />
              <RouteCard title="Safe Route" route={result.safe} tone="safe" recommended={!result.explanation?.same_route} />
            </div>
          )}
        </div>

        <div className="lg:col-span-7 xl:col-span-8">
          <MapView
            incidents={incidents} roads={roads} vehicles={vehicles} infrastructure={infrastructure}
            routes={result ? { safe: result.safe, fastest: result.fastest } : null}
            layers={{ roads: true, hazards: true, vehicles: false, infrastructure: true, routes: true }}
            height="clamp(460px, 66vh, 720px)"
          />
        </div>
      </div>
    </div>
  );
}
