import React, { useState } from "react";
import { useApp } from "@/context/AppContext";
import { MapView } from "@/components/MapView";
import { IncidentDrawer } from "@/components/IncidentDrawer";
import { DynIcon } from "@/components/DynIcon";
import { STATUS_COLORS, VERIFICATION_META } from "@/lib/constants";
import { Switch } from "@/components/ui/switch";

const LAYER_DEFS = [
  ["roads", "Road Risk", "Spline"],
  ["hazards", "Hazards", "TriangleAlert"],
  ["vehicles", "Vehicles", "Car"],
  ["infrastructure", "Infrastructure", "Hospital"],
  ["routes", "Routes", "Route"],
];

export default function LiveMap() {
  const { incidents, roads, vehicles, infrastructure, demo_route, summary } = useApp();
  const [selected, setSelected] = useState(null);
  const [focus, setFocus] = useState(null);
  const [layers, setLayers] = useState({ roads: true, hazards: true, vehicles: true, infrastructure: true, routes: true });

  const toggle = (k) => setLayers((l) => ({ ...l, [k]: !l[k] }));
  const openIncident = (id) => {
    setSelected(id);
    const inc = incidents.find((i) => i.id === id);
    if (inc) setFocus([inc.latitude, inc.longitude]);
  };

  return (
    <div className="relative" style={{ height: "calc(100vh - 56px)" }}>
      <MapView
        incidents={incidents} roads={roads} vehicles={vehicles} infrastructure={infrastructure}
        routes={demo_route} layers={layers} onSelectIncident={openIncident} focus={focus} selectedId={selected}
        height="100%"
      />

      {/* Layer controls */}
      <div className="absolute left-3 top-3 z-[500] w-52 rounded-xl rq-glass p-3" data-testid="map-overlay-controls">
        <div className="rq-label mb-2 flex items-center gap-1.5"><DynIcon name="Layers" className="h-3.5 w-3.5" /> Layers</div>
        <div className="space-y-2">
          {LAYER_DEFS.map(([k, label, icon]) => (
            <label key={k} className="flex items-center justify-between gap-2 text-[12.5px]" data-testid={`map-layer-toggle-${k}`}>
              <span className="flex items-center gap-2"><DynIcon name={icon} className="h-4 w-4 text-muted-foreground" />{label}</span>
              <Switch checked={layers[k]} onCheckedChange={() => toggle(k)} />
            </label>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="absolute bottom-6 left-3 z-[500] w-52 rounded-xl rq-glass p-3">
        <div className="rq-label mb-2">Road Risk</div>
        <div className="space-y-1">
          {["SAFE", "CAUTION", "UNSAFE", "CRITICAL"].map((s) => (
            <div key={s} className="flex items-center gap-2 text-[12px]">
              <span className="h-1.5 w-6 rounded-full" style={{ background: STATUS_COLORS[s].solid }} />{STATUS_COLORS[s].label}
            </div>
          ))}
        </div>
        <div className="rq-label mb-1 mt-3">Verification</div>
        <div className="grid grid-cols-1 gap-1">
          {Object.entries(VERIFICATION_META).map(([k, m]) => (
            <div key={k} className="flex items-center gap-2 text-[11.5px]"><span className="h-2 w-2 rounded-full" style={{ background: m.color }} />{m.label}</div>
          ))}
        </div>
      </div>

      {/* Top-right mini stats */}
      <div className="absolute right-3 top-3 z-[500] flex gap-2">
        {[["Hazards", summary.active_hazards, "hsl(45 90% 55%)"], ["Unsafe", summary.unsafe_roads, "hsl(8 85% 56%)"], ["Verified", summary.verified_incidents, "hsl(150 70% 50%)"]].map(([l, v, c]) => (
          <div key={l} className="rounded-lg rq-glass px-3 py-1.5 text-center">
            <div className="mono text-lg font-semibold" style={{ color: c }}>{v ?? "—"}</div>
            <div className="rq-label">{l}</div>
          </div>
        ))}
      </div>

      <IncidentDrawer incidentId={selected} open={!!selected} onOpenChange={(o) => !o && setSelected(null)} />
    </div>
  );
}
