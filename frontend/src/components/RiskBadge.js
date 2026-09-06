import React from "react";
import { STATUS_COLORS } from "@/lib/constants";
import { DynIcon } from "@/components/DynIcon";

// SAFE / CAUTION / UNSAFE / CRITICAL / UNKNOWN badge (icon + label, never color-only).
export function RiskBadge({ state = "UNKNOWN", score, size = "sm", className = "" }) {
  const s = STATUS_COLORS[state] || STATUS_COLORS.UNKNOWN;
  const pad = size === "lg" ? "px-2.5 py-1 text-xs" : "px-2 py-0.5 text-[11px]";
  return (
    <span
      data-testid="risk-badge"
      className={`inline-flex items-center gap-1.5 rounded-full border font-semibold ${pad} ${className}`}
      style={{ background: s.bg, color: s.fg, borderColor: s.border }}
    >
      <DynIcon name={s.icon} className="h-3.5 w-3.5" style={{ color: s.solid }} />
      <span className="sr-only">Road status: </span>
      {s.label}
      {score != null && <span className="mono opacity-80">· {score}</span>}
    </span>
  );
}

export default RiskBadge;
