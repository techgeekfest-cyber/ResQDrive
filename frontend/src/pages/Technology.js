import React from "react";
import { DynIcon } from "@/components/DynIcon";

const PROTOTYPE = [
  ["Frontend", "MonitorSmartphone", ["React + CRA", "Tailwind CSS + shadcn/ui", "Leaflet + OpenStreetMap", "Recharts", "WebSocket client"]],
  ["Backend", "Server", ["FastAPI", "MongoDB", "WebSockets", "Evidence Fusion Engine", "Risk + Routing Engine"]],
  ["Intelligence", "BrainCircuit", ["Confidence-aware fusion", "Exponential freshness decay", "Dijkstra risk-aware routing", "Response prioritisation"]],
];

const PRODUCTION = [
  ["Frontend", "MonitorSmartphone", ["React / Next.js + TypeScript", "MapLibre / Leaflet", "Realtime dashboards"]],
  ["Backend", "Server", ["FastAPI / Node.js", "PostgreSQL + PostGIS", "Redis", "MQTT + WebSockets"]],
  ["AI / Edge", "Cpu", ["Python + PyTorch", "YOLO-family models + OpenCV", "Raspberry Pi / Jetson", "Android smartphone nodes"]],
  ["Maps / Routing", "Map", ["OpenStreetMap", "OSRM / GraphHopper", "Live traffic + weather feeds"]],
];

function Column({ title, badge, badgeColor, groups }) {
  return (
    <div className="rq-panel p-4" data-testid="technology-stack-cards">
      <div className="mb-3 flex items-center gap-2">
        <h2 className="text-base font-semibold">{title}</h2>
        <span className="rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide" style={{ background: badgeColor + "22", color: badgeColor }}>{badge}</span>
      </div>
      <div className="space-y-3">
        {groups.map(([g, icon, items]) => (
          <div key={g} className="rounded-lg border border-border bg-secondary p-3">
            <div className="mb-2 flex items-center gap-2 text-[13px] font-semibold"><DynIcon name={icon} className="h-4 w-4 text-[hsl(190_85%_60%)]" />{g}</div>
            <div className="flex flex-wrap gap-1.5">
              {items.map((it) => <span key={it} className="rounded-md bg-[hsl(220_12%_16%)] px-2 py-1 text-[11.5px] text-muted-foreground">{it}</span>)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Technology() {
  return (
    <div className="mx-auto max-w-[1100px] px-3 py-6 lg:px-5">
      <h1 className="text-xl font-semibold tracking-tight">Technology</h1>
      <p className="mb-6 text-[13px] text-muted-foreground">The stack powering this prototype today, and the planned production stack for real deployment.</p>
      <div className="grid gap-4 lg:grid-cols-2">
        <Column title="Prototype Architecture" badge="Running now" badgeColor="hsl(150 70% 50%)" groups={PROTOTYPE} />
        <Column title="Planned Production Stack" badge="Planned" badgeColor="hsl(45 90% 58%)" groups={PRODUCTION} />
      </div>
      <div className="mt-4 rounded-xl border border-[hsl(45_60%_28%)] bg-[hsl(42_60%_10%)] p-4 text-[13px] text-[hsl(45_85%_78%)]">
        <DynIcon name="TriangleAlert" className="mr-1 inline h-4 w-4" /> These components are not physically deployed. Edge devices, YOLO inference, MQTT, OBD-II and PostGIS are planned integrations with clean extension points in the current architecture.
      </div>
    </div>
  );
}
