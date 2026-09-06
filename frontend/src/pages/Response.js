import React, { useMemo, useState } from "react";
import { toast } from "sonner";
import { useApp } from "@/context/AppContext";
import { KpiCard } from "@/components/KpiCard";
import { RiskBadge } from "@/components/RiskBadge";
import { IncidentDrawer } from "@/components/IncidentDrawer";
import { DynIcon } from "@/components/DynIcon";
import { PRIORITY_META, HAZARD_META } from "@/lib/constants";
import { relAge, titleCase } from "@/lib/format";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";

const ACTIONS = [
  ["acknowledge", "Acknowledge", "Check", "response-acknowledge-button"],
  ["dispatch", "Dispatch", "Siren", "response-dispatch-button"],
  ["monitor", "Monitor", "Eye", "response-monitoring-button"],
  ["resolve", "Resolve", "CircleCheck", "response-resolve-button"],
];

export default function Response() {
  const { incidents, summary, role, actions } = useApp();
  const [selected, setSelected] = useState(null);
  const canAct = ["AUTHORITY", "ADMIN", "OPERATOR"].includes(role);

  const rows = useMemo(
    () => incidents.filter((i) => i.response_status !== "RESOLVED")
      .sort((a, b) => (b.priority_score || 0) - (a.priority_score || 0)),
    [incidents],
  );
  const p1 = rows.filter((i) => i.priority === "P1").length;

  const act = async (id, action, label) => {
    if (!canAct) { toast.error(`Switch to Authority/Operator role to ${label}.`); return; }
    try { await actions.respond(id, action, { operator: role }); toast.success(`Incident ${label}`); }
    catch { toast.error("Action failed"); }
  };

  return (
    <div className="mx-auto max-w-[1720px] px-3 py-4 lg:px-5">
      <div className="mb-1 flex items-center gap-2">
        <DynIcon name="Siren" className="h-5 w-5 text-[hsl(8_85%_58%)]" />
        <h1 className="text-xl font-semibold tracking-tight">Emergency Response Command</h1>
      </div>
      <p className="mb-4 text-[13px] text-muted-foreground">Prioritised, verified road intelligence for responders · acting as <span className="font-semibold text-foreground">{role}</span>.</p>

      <div className="mb-4 grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
        <KpiCard label="Active Incidents" value={summary.active_hazards ?? "—"} icon="TriangleAlert" accent="hsl(45 90% 55%)" />
        <KpiCard label="P1 Critical" value={p1} icon="Siren" accent="hsl(0 85% 52%)" />
        <KpiCard label="Priority Zones" value={summary.priority_zones ?? "—"} icon="MapPinned" accent="hsl(8 85% 56%)" />
        <KpiCard label="Verified Hazards" value={summary.verified_incidents ?? "—"} icon="BadgeCheck" accent="hsl(150 70% 48%)" />
        <KpiCard label="Unverified Reports" value={summary.unverified_incidents ?? "—"} icon="CircleDashed" accent="hsl(215 12% 60%)" />
        <KpiCard label="Available Vehicles" value={summary.active_vehicles ?? "—"} icon="Car" accent="hsl(190 85% 45%)" />
      </div>

      <div className="rq-panel overflow-hidden">
        <div className="border-b border-border p-3"><div className="rq-label">Priority Incident Queue · {rows.length}</div></div>
        <div className="max-h-[60vh] overflow-auto">
          <Table data-testid="priority-incident-table">
            <TableHeader className="sticky top-0 bg-[hsl(220_14%_12%)]">
              <TableRow className="border-border hover:bg-transparent">
                <TableHead>Incident</TableHead><TableHead>Location</TableHead><TableHead>Hazard</TableHead>
                <TableHead>Risk</TableHead><TableHead>Conf</TableHead><TableHead>Evidence</TableHead>
                <TableHead>Age</TableHead><TableHead>Priority</TableHead><TableHead>Status</TableHead><TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.map((inc) => {
                const meta = HAZARD_META[inc.hazard_type] || {};
                return (
                  <TableRow key={inc.id} className="border-border" style={{ boxShadow: `inset 3px 0 0 ${PRIORITY_META[inc.priority]?.color}` }}>
                    <TableCell className="mono cursor-pointer font-semibold text-[hsl(190_85%_62%)]" onClick={() => setSelected(inc.id)} data-testid={`response-incident-${inc.id}`}>{inc.id}</TableCell>
                    <TableCell className="max-w-[150px] truncate text-[12px] text-muted-foreground">{inc.road_name}</TableCell>
                    <TableCell className="text-[12px]"><span className="flex items-center gap-1.5"><DynIcon name={meta.icon || "TriangleAlert"} className="h-3.5 w-3.5" />{meta.label || inc.hazard_type}</span></TableCell>
                    <TableCell><RiskBadge state={inc.risk_state} score={inc.risk_score} /></TableCell>
                    <TableCell className="mono text-[12px]">{inc.confidence}%</TableCell>
                    <TableCell className="mono text-[12px]">{inc.evidence_count} veh</TableCell>
                    <TableCell className="text-[12px] text-muted-foreground">{relAge(inc.age_min)}</TableCell>
                    <TableCell><span className="text-[12px] font-semibold" style={{ color: PRIORITY_META[inc.priority]?.color }}>{inc.priority}</span></TableCell>
                    <TableCell className="text-[12px]">{titleCase(inc.response_status)}</TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        {ACTIONS.map(([a, label, icon, testid]) => (
                          <button key={a} title={label} onClick={() => act(inc.id, a, label.toLowerCase())} data-testid={testid}
                            className="grid h-7 w-7 place-items-center rounded-md border border-border bg-secondary text-muted-foreground transition-colors hover:border-[hsl(190_50%_40%)] hover:text-foreground">
                            <DynIcon name={icon} className="h-3.5 w-3.5" />
                          </button>
                        ))}
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })}
              {rows.length === 0 && <TableRow><TableCell colSpan={10} className="py-10 text-center text-muted-foreground">No active incidents. Network is clear.</TableCell></TableRow>}
            </TableBody>
          </Table>
        </div>
      </div>

      <IncidentDrawer incidentId={selected} open={!!selected} onOpenChange={(o) => !o && setSelected(null)} />
    </div>
  );
}
