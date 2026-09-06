import React, { useEffect, useMemo, useState } from "react";
import { useApp } from "@/context/AppContext";
import { api } from "@/lib/api";
import { RiskBadge } from "@/components/RiskBadge";
import { VerificationBadge } from "@/components/VerificationBadge";
import { ConfidenceRing } from "@/components/ConfidenceRing";
import { IncidentDrawer } from "@/components/IncidentDrawer";
import { DynIcon } from "@/components/DynIcon";
import { HAZARD_META } from "@/lib/constants";
import { relAge } from "@/lib/format";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip as RTooltip, ResponsiveContainer, PieChart, Pie, Cell,
} from "recharts";

const STATES = ["ALL", "VERIFIED", "CORROBORATED", "CONFLICTING", "UNVERIFIED", "STALE"];
const RISK_COLORS = { SAFE: "hsl(150 70% 45%)", CAUTION: "hsl(45 90% 55%)", UNSAFE: "hsl(8 85% 56%)" };

export default function Hazards() {
  const { incidents } = useApp();
  const [filter, setFilter] = useState("ALL");
  const [selected, setSelected] = useState(null);
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    const load = () => api.analytics().then(setAnalytics).catch(() => {});
    load();
    const t = setInterval(load, 5000);
    return () => clearInterval(t);
  }, []);

  const list = useMemo(() => {
    const active = incidents.filter((i) => i.response_status !== "RESOLVED");
    return filter === "ALL" ? active : active.filter((i) => i.verification_status === filter);
  }, [incidents, filter]);

  return (
    <div className="mx-auto max-w-[1720px] px-3 py-4 lg:px-5">
      <h1 className="text-xl font-semibold tracking-tight">Hazard Intelligence</h1>
      <p className="mb-4 text-[13px] text-muted-foreground">Multi-vehicle evidence fusion · confidence, verification & freshness per incident.</p>

      {/* Analytics */}
      <div className="mb-4 grid gap-3 lg:grid-cols-3">
        <div className="rq-panel p-3">
          <div className="rq-label mb-2">Hazards by Type</div>
          <ResponsiveContainer width="100%" height={160} data-testid="chart-hazards-by-type">
            <BarChart data={analytics?.hazards_by_type || []} margin={{ left: -18, top: 4 }}>
              <XAxis dataKey="label" tick={{ fill: "rgba(255,255,255,0.55)", fontSize: 9 }} interval={0} angle={-30} textAnchor="end" height={44} />
              <YAxis tick={{ fill: "rgba(255,255,255,0.55)", fontSize: 10 }} allowDecimals={false} />
              <RTooltip contentStyle={{ background: "hsl(220 14% 12%)", border: "1px solid hsl(220 10% 26%)", borderRadius: 8, fontSize: 12 }} />
              <Bar dataKey="count" fill="hsl(190 85% 50%)" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="rq-panel p-3">
          <div className="rq-label mb-2">Verified vs Unverified</div>
          <ResponsiveContainer width="100%" height={160} data-testid="chart-verified-vs-unverified">
            <BarChart data={analytics?.verification || []} margin={{ left: -18, top: 4 }}>
              <XAxis dataKey="state" tick={{ fill: "rgba(255,255,255,0.55)", fontSize: 9 }} interval={0} angle={-30} textAnchor="end" height={44} />
              <YAxis tick={{ fill: "rgba(255,255,255,0.55)", fontSize: 10 }} allowDecimals={false} />
              <RTooltip contentStyle={{ background: "hsl(220 14% 12%)", border: "1px solid hsl(220 10% 26%)", borderRadius: 8, fontSize: 12 }} />
              <Bar dataKey="count" fill="hsl(150 70% 48%)" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="rq-panel p-3">
          <div className="rq-label mb-2">Road Risk Distribution</div>
          <ResponsiveContainer width="100%" height={160} data-testid="chart-road-risk-distribution">
            <PieChart>
              <Pie data={analytics?.risk_distribution || []} dataKey="count" nameKey="state" innerRadius={40} outerRadius={64} paddingAngle={2}>
                {(analytics?.risk_distribution || []).map((e) => <Cell key={e.state} fill={RISK_COLORS[e.state]} />)}
              </Pie>
              <RTooltip contentStyle={{ background: "hsl(220 14% 12%)", border: "1px solid hsl(220 10% 26%)", borderRadius: 8, fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex justify-center gap-3 text-[11px]">
            {(analytics?.risk_distribution || []).map((e) => (
              <span key={e.state} className="flex items-center gap-1"><span className="h-2 w-2 rounded-full" style={{ background: RISK_COLORS[e.state] }} />{e.state} {e.count}</span>
            ))}
          </div>
        </div>
      </div>

      <div className="mb-3 flex items-center gap-2">
        <span className="rq-label">Filter</span>
        <Select value={filter} onValueChange={setFilter}>
          <SelectTrigger className="h-9 w-[190px] bg-secondary" data-testid="hazard-filter-select"><SelectValue /></SelectTrigger>
          <SelectContent>{STATES.map((s) => <SelectItem key={s} value={s}>{s === "ALL" ? "All incidents" : s}</SelectItem>)}</SelectContent>
        </Select>
        <span className="text-[13px] text-muted-foreground">{list.length} incidents</span>
      </div>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {list.map((inc) => {
          const meta = HAZARD_META[inc.hazard_type] || {};
          return (
            <button key={inc.id} onClick={() => setSelected(inc.id)} className="rq-panel group p-3.5 text-left transition-colors hover:border-[hsl(190_50%_38%)]" data-testid={`hazard-card-${inc.id}`}>
              <div className="flex items-start gap-3">
                <ConfidenceRing value={inc.confidence} size={48} stroke={4} />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-1.5 font-semibold">
                    <DynIcon name={meta.icon || "TriangleAlert"} className="h-4 w-4 text-[hsl(190_85%_60%)]" />
                    {meta.label || inc.hazard_type}
                  </div>
                  <div className="mono truncate text-[11px] text-muted-foreground">{inc.id} · {inc.road_name}</div>
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    <RiskBadge state={inc.risk_state} score={inc.risk_score} />
                    <VerificationBadge state={inc.verification_status} />
                  </div>
                </div>
              </div>
              <div className="mono mt-3 grid grid-cols-3 gap-2 border-t border-border pt-2 text-[11px] text-muted-foreground">
                <span><DynIcon name="Car" className="mr-1 inline h-3 w-3" />{inc.evidence_count} veh</span>
                <span><DynIcon name="GitCompareArrows" className="mr-1 inline h-3 w-3" />{inc.agreement}%</span>
                <span><DynIcon name="Clock" className="mr-1 inline h-3 w-3" />{relAge(inc.age_min)}</span>
              </div>
            </button>
          );
        })}
        {list.length === 0 && <div className="col-span-full rq-panel p-8 text-center text-muted-foreground">No incidents match this filter.</div>}
      </div>

      <IncidentDrawer incidentId={selected} open={!!selected} onOpenChange={(o) => !o && setSelected(null)} />
    </div>
  );
}
