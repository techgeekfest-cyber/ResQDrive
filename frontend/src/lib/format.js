export function confidenceBand(pct) {
  if (pct >= 90) return "Very High";
  if (pct >= 70) return "High";
  if (pct >= 40) return "Moderate";
  return "Low";
}

export function relAge(min) {
  if (min == null) return "—";
  if (min < 1) return "just now";
  if (min < 60) return `${Math.round(min)}m ago`;
  const h = Math.floor(min / 60);
  const m = Math.round(min % 60);
  return `${h}h ${m}m ago`;
}

export function fmtClock(iso) {
  if (!iso) return "--:--:--";
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString("en-GB", { hour12: false });
  } catch {
    return "--:--:--";
  }
}

export function fmtTimeShort(iso) {
  if (!iso) return "--:--";
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString("en-GB", { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });
  } catch {
    return "--:--";
  }
}

export function fmtCoord(v) {
  if (v == null) return "—";
  return Number(v).toFixed(5);
}

export function titleCase(s) {
  if (!s) return "";
  return String(s).replace(/_/g, " ").replace(/\w\S*/g, (t) => t.charAt(0).toUpperCase() + t.slice(1).toLowerCase());
}
