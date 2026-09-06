import React from "react";

// Compact confidence ring (SVG stroke-dasharray). Color reflects confidence band.
export function ConfidenceRing({ value = 0, size = 44, stroke = 4, showLabel = true }) {
  const v = Math.max(0, Math.min(100, value));
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const dash = (v / 100) * c;
  const color =
    v >= 90 ? "hsl(150 70% 50%)" : v >= 70 ? "hsl(190 85% 52%)" : v >= 40 ? "hsl(45 90% 55%)" : "hsl(8 85% 56%)";
  return (
    <div
      data-testid="confidence-ring"
      className="relative inline-grid place-items-center"
      style={{ width: size, height: size }}
    >
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="hsl(220 10% 20%)" strokeWidth={stroke} />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeDasharray={`${dash} ${c}`}
          strokeLinecap="round"
          style={{ transition: "stroke-dasharray 0.4s ease" }}
        />
      </svg>
      {showLabel && (
        <div className="absolute inset-0 grid place-items-center">
          <span className="mono text-[11px] font-semibold" style={{ color }}>{v}%</span>
        </div>
      )}
    </div>
  );
}

export default ConfidenceRing;
