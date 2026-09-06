import React from "react";
import { DynIcon } from "@/components/DynIcon";

// KPI card with top accent + big value + optional delta / hint.
export function KpiCard({ label, value, suffix, icon, accent = "hsl(190 85% 45%)", hint, testId }) {
  return (
    <div
      data-testid={testId || "kpi-card"}
      className="rq-accent-top rq-panel relative overflow-hidden p-3.5"
      style={{ "--rq-accent": accent }}
    >
      <div className="flex items-start justify-between">
        <div className="rq-label">{label}</div>
        {icon && (
          <div className="grid h-7 w-7 place-items-center rounded-md" style={{ background: accent + "22" }}>
            <DynIcon name={icon} className="h-4 w-4" style={{ color: accent }} />
          </div>
        )}
      </div>
      <div className="mt-1.5 flex items-baseline gap-1">
        <span className="mono text-2xl font-semibold leading-none text-foreground md:text-[28px]">{value}</span>
        {suffix && <span className="text-sm text-muted-foreground">{suffix}</span>}
      </div>
      {hint && <div className="mt-1 text-[11px] text-muted-foreground">{hint}</div>}
    </div>
  );
}

export default KpiCard;
