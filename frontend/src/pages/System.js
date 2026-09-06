import React from "react";
import { DynIcon } from "@/components/DynIcon";

const LAYERS = [
  ["Vehicle Layer", "Car", "hsl(190 85% 55%)", ["RGB Camera", "GPS", "Accelerometer / IMU", "OBD-II / IoT"]],
  ["Edge AI Layer", "Cpu", "hsl(265 60% 62%)", ["Object Detection", "Segmentation", "Sensor Fusion", "Local Risk Estimation"]],
  ["Communication Layer", "RadioTower", "hsl(45 90% 58%)", ["MQTT", "WebSocket", "HTTPS", "Offline Edge Buffer"]],
  ["Cloud Intelligence", "Server", "hsl(190 85% 50%)", ["Observation Service", "Evidence Fusion Engine", "Risk Engine", "Geospatial Engine"]],
  ["Application", "LayoutDashboard", "hsl(150 70% 50%)", ["Live Risk Map", "Safe Routing", "Emergency Dashboard", "Analytics"]],
  ["Users", "Users", "hsl(8 85% 58%)", ["Citizens / Drivers", "Emergency Responders", "Authorities"]],
];

const PIPELINE = ["Camera Frame", "Edge AI", "Hazard Detection", "GPS Association", "Local Risk Estimate", "Network Transmission", "Evidence Fusion", "Live Road Intelligence"];

export default function System() {
  return (
    <div className="mx-auto max-w-[1100px] px-3 py-6 lg:px-5">
      <h1 className="text-xl font-semibold tracking-tight">System Architecture</h1>
      <p className="mb-6 text-[13px] text-muted-foreground">Edge-first cooperative sensing pipeline. Labelled as <span className="font-semibold text-[hsl(45_90%_70%)]">Prototype Architecture</span> — no hardware is physically connected.</p>

      {/* Edge-first pipeline */}
      <div className="rq-panel mb-6 p-4">
        <div className="rq-label mb-3">Edge-first inference pipeline</div>
        <div className="flex flex-wrap items-center gap-2">
          {PIPELINE.map((p, i) => (
            <React.Fragment key={p}>
              <span className="rounded-lg border border-border bg-secondary px-3 py-1.5 text-[12.5px] font-medium">{p}</span>
              {i < PIPELINE.length - 1 && <DynIcon name="ArrowRight" className="h-4 w-4 text-muted-foreground" />}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Layered stack */}
      <div className="space-y-2" data-testid="system-architecture-diagram">
        {LAYERS.map(([title, icon, color, items], i) => (
          <React.Fragment key={title}>
            <div className="rq-panel overflow-hidden">
              <div className="flex items-center gap-3 border-b border-border p-3" style={{ background: color + "12" }}>
                <span className="grid h-9 w-9 place-items-center rounded-lg" style={{ background: color + "22" }}><DynIcon name={icon} className="h-5 w-5" style={{ color }} /></span>
                <div className="font-semibold">{title}</div>
              </div>
              <div className="grid grid-cols-2 gap-2 p-3 sm:grid-cols-4">
                {items.map((it) => (
                  <div key={it} className="rounded-lg border border-border bg-secondary px-3 py-2 text-center text-[12.5px]">{it}</div>
                ))}
              </div>
            </div>
            {i < LAYERS.length - 1 && <div className="flex justify-center"><DynIcon name="ArrowDown" className="h-5 w-5 text-muted-foreground" /></div>}
          </React.Fragment>
        ))}
      </div>

      <div className="mt-6 rounded-xl border border-[hsl(190_40%_28%)] bg-[hsl(190_50%_9%)] p-4 text-[13px] text-[hsl(190_60%_82%)]">
        <div className="mb-1 flex items-center gap-2 font-semibold"><DynIcon name="GitMerge" className="h-4 w-4" /> The core innovation</div>
        Multiple independent vehicles observing the same road are fused into a single confidence-aware assessment. Corroboration raises confidence, conflicting reports lower it, and observation freshness decays over time — producing a continuously updated road-risk graph that drives safe routing and emergency response.
      </div>
    </div>
  );
}
