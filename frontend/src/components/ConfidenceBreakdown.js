import React from "react";
import { DynIcon } from "@/components/DynIcon";

const PARTS = [
  { key: "ai_detection", label: "AI detection", color: "hsl(190 85% 52%)", icon: "ScanEye" },
  { key: "vehicle_corroboration", label: "Vehicle corroboration", color: "hsl(150 70% 50%)", icon: "Car" },
  { key: "sensor_corroboration", label: "Sensor corroboration", color: "hsl(265 60% 62%)", icon: "Radar" },
  { key: "freshness", label: "Freshness", color: "hsl(45 90% 55%)", icon: "Clock" },
  { key: "sensor_reliability", label: "Sensor reliability", color: "hsl(215 30% 62%)", icon: "Gauge" },
];

// "Why is confidence X%?" additive breakdown (values sum to total confidence).
export function ConfidenceBreakdown({ breakdown = {}, total = 0 }) {
  const sum = Object.values(breakdown).reduce((a, b) => a + b, 0) || 1;
  return (
    <div data-testid="confidence-breakdown">
      <div className="mb-3 flex items-center justify-between">
        <span className="rq-label">Why confidence is {total}%</span>
        <span className="mono text-sm font-semibold text-foreground">{total}%</span>
      </div>
      <div className="mb-3 flex h-2.5 w-full overflow-hidden rounded-full bg-secondary">
        {PARTS.map((p) => {
          const v = breakdown[p.key] || 0;
          return <div key={p.key} style={{ width: `${(v / sum) * 100}%`, background: p.color }} title={`${p.label}: ${v}`} />;
        })}
      </div>
      <div className="space-y-1.5">
        {PARTS.map((p) => (
          <div key={p.key} className="flex items-center gap-2 text-[12.5px]">
            <span className="grid h-6 w-6 place-items-center rounded-md" style={{ background: p.color + "22" }}>
              <DynIcon name={p.icon} className="h-3.5 w-3.5" style={{ color: p.color }} />
            </span>
            <span className="flex-1 text-muted-foreground">{p.label}</span>
            <span className="mono font-semibold" style={{ color: p.color }}>+{breakdown[p.key] || 0}</span>
          </div>
        ))}
      </div>
      <p className="mt-3 text-[11px] leading-relaxed text-muted-foreground">
        Prototype explanation. Confidence rises with independent multi-vehicle corroboration and decays with observation age.
      </p>
    </div>
  );
}

export default ConfidenceBreakdown;
