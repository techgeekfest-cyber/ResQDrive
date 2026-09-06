import React, { useEffect, useState } from "react";
import { useApp } from "@/context/AppContext";
import { api } from "@/lib/api";
import { KpiCard } from "@/components/KpiCard";
import { DynIcon } from "@/components/DynIcon";
import { titleCase } from "@/lib/format";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";

const STATUS_COLOR = {
  ACTIVE: "hsl(190 70% 50%)", OBSERVING: "hsl(45 90% 58%)", TRANSMITTING: "hsl(190 85% 55%)",
  EMERGENCY: "hsl(8 85% 58%)", DISCONNECTED: "hsl(215 12% 50%)",
};
const sensorDot = (v) => (v === "ONLINE" || v === "EXCELLENT" || v === "GOOD" ? "hsl(150 70% 50%)" : v === "FAIR" || v === "DEGRADED" ? "hsl(45 90% 58%)" : "hsl(8 85% 58%)");

export default function Vehicles() {
  const { vehicles } = useApp();
  const [health, setHealth] = useState(null);
  const [q, setQ] = useState("");
  const [detailId, setDetailId] = useState(null);
  const [detail, setDetail] = useState(null);

  useEffect(() => {
    const load = () => api.networkHealth().then(setHealth).catch(() => {});
    load();
    const t = setInterval(load, 5000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    if (!detailId) return;
    let active = true;
    const load = () => api.vehicle(detailId).then((d) => active && setDetail(d)).catch(() => {});
    load();
    const t = setInterval(load, 3000);
    return () => { active = false; clearInterval(t); };
  }, [detailId]);

  const filtered = vehicles.filter((v) =>
    !q || v.id.toLowerCase().includes(q.toLowerCase()) || v.status.toLowerCase().includes(q.toLowerCase()),
  );

  return (
    <div className="mx-auto max-w-[1720px] px-3 py-4 lg:px-5">
      <h1 className="text-xl font-semibold tracking-tight">Vehicle Sensing Network</h1>
      <p className="mb-4 text-[13px] text-muted-foreground">Simulated cooperative fleet · each vehicle is a mobile edge sensing node.</p>

      <div className="mb-4 grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
        <KpiCard label="Connected" value={health ? `${health.connected}` : "—"} suffix={health ? `/ ${health.total}` : ""} icon="Wifi" accent="hsl(150 70% 48%)" />
        <KpiCard label="Disconnected" value={health?.disconnected ?? "—"} icon="WifiOff" accent="hsl(8 85% 56%)" />
        <KpiCard label="Avg Sensor Health" value={health?.avg_sensor_health ?? "—"} suffix="%" icon="Activity" accent="hsl(190 85% 45%)" />
        <KpiCard label="Avg GPS Accuracy" value={health?.avg_gps_accuracy ?? "—"} suffix="%" icon="Satellite" accent="hsl(190 85% 45%)" />
        <KpiCard label="Avg Latency" value={health?.avg_latency_ms ?? "—"} suffix="ms" icon="Timer" accent="hsl(45 90% 55%)" />
        <KpiCard label="Fusion Success" value={health?.fusion_success ?? "—"} suffix="%" icon="GitMerge" accent="hsl(150 70% 48%)" />
      </div>

      <div className="rq-panel overflow-hidden">
        <div className="flex items-center justify-between gap-2 border-b border-border p-3">
          <div className="rq-label">Fleet · {filtered.length} vehicles</div>
          <div className="relative w-56">
            <DynIcon name="Search" className="pointer-events-none absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search vehicle / status" className="h-9 bg-secondary pl-8" data-testid="vehicle-search-input" />
          </div>
        </div>
        <div className="max-h-[62vh] overflow-auto">
          <Table data-testid="fleet-table">
            <TableHeader className="sticky top-0 bg-[hsl(220_14%_12%)]">
              <TableRow className="border-border hover:bg-transparent">
                <TableHead>Vehicle</TableHead><TableHead>Status</TableHead><TableHead>Road</TableHead>
                <TableHead>Speed</TableHead><TableHead>Cam</TableHead><TableHead>GPS</TableHead>
                <TableHead>IMU</TableHead><TableHead>Network</TableHead><TableHead>Observation</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((v) => (
                <TableRow key={v.id} className="cursor-pointer border-border" onClick={() => setDetailId(v.id)} data-testid={`vehicle-row-${v.id}`}>
                  <TableCell className="mono font-semibold">{v.id}</TableCell>
                  <TableCell><span className="inline-flex items-center gap-1.5 text-[12px]"><span className="h-2 w-2 rounded-full" style={{ background: STATUS_COLOR[v.status] }} />{titleCase(v.status)}</span></TableCell>
                  <TableCell className="max-w-[160px] truncate text-[12px] text-muted-foreground">{v.road_name}</TableCell>
                  <TableCell className="mono text-[12px]">{v.speed} km/h</TableCell>
                  <TableCell><span className="h-2 w-2 rounded-full" style={{ background: sensorDot(v.camera_status), display: "inline-block" }} title={v.camera_status} /></TableCell>
                  <TableCell><span className="h-2 w-2 rounded-full" style={{ background: sensorDot(v.gps_status), display: "inline-block" }} title={v.gps_status} /></TableCell>
                  <TableCell><span className="h-2 w-2 rounded-full" style={{ background: sensorDot(v.imu_status), display: "inline-block" }} title={v.imu_status} /></TableCell>
                  <TableCell className="text-[12px] text-muted-foreground">{titleCase(v.network_quality)}{v.buffered > 0 && <span className="ml-1 text-[hsl(45_90%_60%)]">· {v.buffered} buffered</span>}</TableCell>
                  <TableCell className="max-w-[130px] truncate text-[12px]">{v.current_observation || <span className="text-muted-foreground">—</span>}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>

      <Sheet open={!!detailId} onOpenChange={(o) => { if (!o) { setDetailId(null); setDetail(null); } }}>
        <SheetContent side="right" className="w-full overflow-y-auto border-border bg-[hsl(220_16%_9%)] sm:max-w-[420px]" data-testid="vehicle-detail-drawer">
          <SheetHeader><SheetTitle className="mono">{detailId}</SheetTitle></SheetHeader>
          {detail ? (
            <div className="mt-4 space-y-4">
              <div className="grid grid-cols-2 gap-2 text-[12px]">
                {[["Status", titleCase(detail.status)], ["Speed", `${detail.speed} km/h`], ["Heading", `${detail.heading}°`], ["Battery", `${detail.battery}%`], ["Road", detail.road_name], ["Network", titleCase(detail.network_quality)], ["Camera", detail.camera_status], ["GPS", detail.gps_status], ["IMU", detail.imu_status]].map(([l, val]) => (
                  <div key={l} className="rq-panel px-2.5 py-1.5"><div className="rq-label">{l}</div><div className="text-[12.5px]">{val}</div></div>
                ))}
                <div className="rq-panel col-span-2 px-2.5 py-1.5"><div className="rq-label">Coordinates</div><div className="mono text-[12.5px]">{detail.latitude}, {detail.longitude}</div></div>
              </div>
              <div>
                <div className="rq-label mb-2">Observation history</div>
                <div className="space-y-1.5">
                  {(detail.observation_history || []).length === 0 && <div className="text-[12px] text-muted-foreground">No recent observations from this vehicle.</div>}
                  {(detail.observation_history || []).slice().reverse().map((o) => (
                    <div key={o.id} className="flex items-center gap-2 rounded-lg border border-border bg-secondary px-2.5 py-2 text-[12px]">
                      <span className="rounded bg-white/5 px-1 text-[10px]">{o.sensor_type}</span>
                      <span>{o.hazard_label}</span>
                      <span className="mono ml-auto">{o.confidence}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : <div className="mt-6 text-muted-foreground">Loading…</div>}
        </SheetContent>
      </Sheet>
    </div>
  );
}
