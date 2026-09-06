import React, { useState } from "react";
import { useApp } from "@/context/AppContext";
import { MapView } from "@/components/MapView";
import { LiveEventFeed } from "@/components/LiveEventFeed";
import { KpiCard } from "@/components/KpiCard";
import { SimulationControls } from "@/components/SimulationControls";
import { IncidentDrawer } from "@/components/IncidentDrawer";
import { DynIcon } from "@/components/DynIcon";

export default function CommandCenter() {
  const { summary, incidents, roads, vehicles, infrastructure, events, demo_route, sim } = useApp();
  const [selected, setSelected] = useState(null);
  const [focus, setFocus] = useState(null);

  const openIncident = (id) => {
    setSelected(id);
    const inc = incidents.find((i) => i.id === id);
    if (inc) setFocus([inc.latitude, inc.longitude]);
  };

  const kpis = [
    { label: "Active Vehicles", value: summary.active_vehicles ?? "—", suffix: `/ ${summary.total_vehicles ?? ""}`, icon: "Car", accent: "hsl(190 85% 45%)", testId: "kpi-active-vehicles" },
    { label: "Active Hazards", value: summary.active_hazards ?? "—", icon: "TriangleAlert", accent: "hsl(45 90% 55%)", testId: "kpi-active-hazards" },
    { label: "Roads at Risk", value: (summary.unsafe_roads ?? 0) + (summary.caution_roads ?? 0), hint: `${summary.unsafe_roads ?? 0} unsafe · ${summary.caution_roads ?? 0} caution`, icon: "ShieldAlert", accent: "hsl(8 85% 56%)", testId: "kpi-roads-at-risk" },
    { label: "Verified Incidents", value: summary.verified_incidents ?? "—", icon: "BadgeCheck", accent: "hsl(150 70% 48%)", testId: "kpi-verified-incidents" },
    { label: "Network Confidence", value: summary.network_confidence ?? "—", suffix: "%", icon: "Gauge", accent: "hsl(190 85% 45%)", testId: "kpi-network-confidence" },
    { label: "Priority Zones", value: summary.priority_zones ?? "—", icon: "Siren", accent: "hsl(0 85% 52%)", testId: "kpi-priority-zones" },
  ];

  return (
    <div className="mx-auto max-w-[1720px] px-3 py-4 lg:px-5">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">ResQDrive Command Center</h1>
          <p className="text-[13px] text-muted-foreground">Live cooperative road-risk intelligence · Hyderabad · SIMULATED</p>
        </div>
        <div className="rq-panel flex items-center gap-3 px-3 py-2">
          <SimulationControls compact />
        </div>
      </div>

      <div className="mb-3 grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6">
        {kpis.map((k) => <KpiCard key={k.label} {...k} />)}
      </div>

      <div className="grid grid-cols-12 gap-3 lg:gap-4">
        <div className="col-span-12 lg:col-span-8 xl:col-span-9">
          <MapView
            incidents={incidents} roads={roads} vehicles={vehicles} infrastructure={infrastructure}
            routes={sim?.status === "RUNNING" ? demo_route : null}
            onSelectIncident={openIncident} focus={focus} selectedId={selected}
            height="clamp(460px, 62vh, 660px)"
          />
        </div>
        <div className="col-span-12 lg:col-span-4 xl:col-span-3">
          <div className="rq-panel flex flex-col p-3" style={{ height: "clamp(460px, 62vh, 660px)" }}>
            <div className="mb-2 flex items-center justify-between">
              <div className="rq-label flex items-center gap-1.5"><DynIcon name="Radio" className="h-3.5 w-3.5" /> Live Intelligence Feed</div>
              <span className="mono text-[10px] text-muted-foreground">{events.length} events</span>
            </div>
            <div className="min-h-0 flex-1">
              <LiveEventFeed events={events} onSelectIncident={openIncident} />
            </div>
          </div>
        </div>
      </div>

      <IncidentDrawer incidentId={selected} open={!!selected} onOpenChange={(o) => !o && setSelected(null)} />
    </div>
  );
}
