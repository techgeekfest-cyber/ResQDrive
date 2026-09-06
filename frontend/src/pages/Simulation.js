import React from "react";
import { toast } from "sonner";
import { useApp } from "@/context/AppContext";
import { SimulationControls } from "@/components/SimulationControls";
import { LiveEventFeed } from "@/components/LiveEventFeed";
import { MapView } from "@/components/MapView";
import { DynIcon } from "@/components/DynIcon";
import { fmtClock } from "@/lib/format";
import { Button } from "@/components/ui/button";

const STAGES = [
  ["Normal traffic", "Vehicles move across the city; roads reported clear.", "Car"],
  ["First detection", "A vehicle camera detects flood water — incident UNVERIFIED.", "ScanEye"],
  ["Corroboration", "A second independent vehicle detects the same hazard.", "Link2"],
  ["Confirmation", "A third vehicle confirms — fused confidence rises.", "BadgeCheck"],
  ["Sensor fusion", "IMU reports abnormal motion + speed drop (42→11 km/h).", "Radar"],
  ["Road UNSAFE", "Verified flood — road risk crosses the unsafe threshold.", "ShieldAlert"],
  ["Safe route", "Router avoids the flooded corridor and recommends an alternative.", "Route"],
  ["P1 alert", "Authority dashboard receives a prioritised response alert.", "Siren"],
  ["Recovery", "A later vehicle reports the road clear — confidence decays, road returns to SAFE.", "CircleCheck"],
];

function Stat({ label, value, color }) {
  return (
    <div className="rq-panel px-3 py-2">
      <div className="rq-label">{label}</div>
      <div className="mono text-lg font-semibold" style={{ color: color || "inherit" }}>{value}</div>
    </div>
  );
}

export default function Simulation() {
  const { sim, summary, events, incidents, roads, vehicles, infrastructure, demo_route, actions } = useApp();

  const launchDemo = async () => {
    try {
      await actions.reset();
      await new Promise((r) => setTimeout(r, 400));
      await actions.start("CYCLONE_FLOOD", 5);
      toast.success("Cyclone + Urban Flood scenario launched");
    } catch { toast.error("Could not launch scenario"); }
  };

  return (
    <div className="mx-auto max-w-[1720px] px-3 py-4 lg:px-5">
      <h1 className="text-xl font-semibold tracking-tight">Simulation Control Center</h1>
      <p className="mb-4 text-[13px] text-muted-foreground">Drive the live cooperative-sensing demo. Deterministic “Cyclone + Urban Flood” scenario is repeatable.</p>

      <div className="grid gap-3 lg:grid-cols-12">
        <div className="lg:col-span-8">
          <div className="rq-panel p-4">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <span className="rounded-lg bg-[hsl(42_60%_10%)] px-2 py-1 text-[11px] font-semibold uppercase text-[hsl(45_90%_70%)]">Demo Mode</span>
                <Button onClick={launchDemo} className="gap-2 bg-[hsl(8_75%_46%)] text-white hover:bg-[hsl(8_75%_52%)]" data-testid="launch-disaster-simulation-button">
                  <DynIcon name="Zap" className="h-4 w-4" /> Launch Disaster Simulation
                </Button>
              </div>
            </div>
            <SimulationControls />
          </div>

          <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
            <Stat label="Simulation" value={sim?.status || "STOPPED"} color={sim?.status === "RUNNING" ? "hsl(150 70% 55%)" : "hsl(215 12% 62%)"} />
            <Stat label="Scenario" value={(sim?.scenario || "—").replace(/_/g, " ")} />
            <Stat label="Sim Time" value={fmtClock(sim?.sim_time)} />
            <Stat label="Tick" value={sim?.tick ?? 0} />
            <Stat label="Vehicles" value={summary.active_vehicles ?? "—"} color="hsl(190 85% 60%)" />
            <Stat label="Observations" value={summary.observations_total ?? 0} />
            <Stat label="Active Incidents" value={summary.active_hazards ?? "—"} color="hsl(45 90% 60%)" />
            <Stat label="Unsafe Roads" value={summary.unsafe_roads ?? "—"} color="hsl(8 85% 60%)" />
          </div>

          <div className="mt-3">
            <MapView incidents={incidents} roads={roads} vehicles={vehicles} infrastructure={infrastructure}
              routes={sim?.status === "RUNNING" ? demo_route : null}
              layers={{ roads: true, hazards: true, vehicles: true, infrastructure: false, routes: true }}
              height="360px" />
          </div>
        </div>

        <div className="lg:col-span-4">
          <div className="rq-panel mb-3 p-3">
            <div className="rq-label mb-2">Cyclone + Urban Flood — demo script</div>
            <ol className="space-y-2">
              {STAGES.map(([t, d, icon], i) => (
                <li key={t} className="flex gap-2.5">
                  <span className="grid h-6 w-6 shrink-0 place-items-center rounded-md bg-primary/15 text-[hsl(190_85%_60%)]"><DynIcon name={icon} className="h-3.5 w-3.5" /></span>
                  <div><div className="text-[12.5px] font-semibold">{i + 1}. {t}</div><div className="text-[11.5px] leading-snug text-muted-foreground">{d}</div></div>
                </li>
              ))}
            </ol>
          </div>
          <div className="rq-panel flex flex-col p-3" style={{ height: 380 }} data-testid="simulation-event-log">
            <div className="rq-label mb-2 flex items-center gap-1.5"><DynIcon name="ScrollText" className="h-3.5 w-3.5" /> Event Log</div>
            <div className="min-h-0 flex-1"><LiveEventFeed events={events} dense /></div>
          </div>
        </div>
      </div>
    </div>
  );
}
