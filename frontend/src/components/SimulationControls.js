import React, { useState } from "react";
import { toast } from "sonner";
import { useApp } from "@/context/AppContext";
import { DynIcon } from "@/components/DynIcon";
import { SCENARIOS, INJECT_TYPES } from "@/lib/constants";
import { Button } from "@/components/ui/button";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";

const SPEEDS = [1, 2, 5, 10];

export function SimulationControls({ compact = false }) {
  const { sim, actions } = useApp();
  const [scenario, setScenario] = useState(sim?.scenario || "CYCLONE_FLOOD");
  const [busy, setBusy] = useState(false);
  const running = sim?.status === "RUNNING";

  const run = async (fn, msg) => {
    setBusy(true);
    try { await fn(); if (msg) toast.success(msg); }
    catch (e) { toast.error("Action failed. Please retry."); }
    finally { setBusy(false); }
  };

  const onStart = () => run(() => actions.start(scenario, sim?.speed || 2), "Simulation started");
  const onPause = () => run(() => actions.pause(), "Simulation paused");
  const onReset = () => run(() => actions.reset(), "World reset to initial state");
  const onSpeed = (s) => run(() => actions.setSpeed(s));
  const onInject = (t) =>
    run(async () => {
      const res = await actions.inject({ inject_type: t });
      if (res && res.ok === false) toast.message(res.message || "No target available");
      else toast.success(`Injected: ${t.replace(/_/g, " ")}`);
    });

  return (
    <div className="space-y-4" data-testid="simulation-control-center">
      <div className="flex flex-wrap items-center gap-2">
        <Select value={scenario} onValueChange={setScenario}>
          <SelectTrigger data-testid="simulation-scenario-select" className="h-9 w-[210px] bg-secondary">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {SCENARIOS.map((s) => <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>)}
          </SelectContent>
        </Select>

        {!running ? (
          <Button onClick={onStart} disabled={busy} data-testid="simulation-start-button" className="gap-1.5 bg-[hsl(150_60%_38%)] text-white hover:bg-[hsl(150_60%_44%)]">
            <DynIcon name="Play" className="h-4 w-4" /> Start
          </Button>
        ) : (
          <Button onClick={onPause} disabled={busy} data-testid="simulation-pause-button" variant="secondary" className="gap-1.5">
            <DynIcon name="Pause" className="h-4 w-4" /> Pause
          </Button>
        )}
        <Button onClick={onReset} disabled={busy} data-testid="simulation-reset-button" variant="outline" className="gap-1.5 border-border">
          <DynIcon name="RotateCcw" className="h-4 w-4" /> Reset
        </Button>

        <div className="ml-auto flex items-center gap-1 rounded-lg border border-border bg-secondary p-0.5" data-testid="simulation-speed-toggle">
          {SPEEDS.map((s) => (
            <button
              key={s}
              onClick={() => onSpeed(s)}
              className={`mono rounded-md px-2.5 py-1 text-xs font-semibold transition-colors ${
                (sim?.speed || 2) === s ? "bg-primary/20 text-[hsl(190_85%_65%)]" : "text-muted-foreground hover:text-foreground"
              }`}
              data-testid={`simulation-speed-${s}x`}
            >{s}x</button>
          ))}
        </div>
      </div>

      {!compact && (
        <div data-testid="simulation-inject-panel">
          <div className="rq-label mb-2 flex items-center gap-1.5"><DynIcon name="Syringe" className="h-3.5 w-3.5" /> Manual demo injection</div>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-4">
            {INJECT_TYPES.map((t) => (
              <button
                key={t.value}
                onClick={() => onInject(t.value)}
                disabled={busy}
                data-testid={`inject-${t.value.toLowerCase()}-button`}
                className="flex items-center gap-2 rounded-lg border border-border bg-secondary px-3 py-2 text-left text-[12.5px] font-medium transition-colors hover:border-[hsl(190_60%_40%)] hover:bg-white/5 disabled:opacity-50"
              >
                <DynIcon name={t.icon} className="h-4 w-4 text-[hsl(190_85%_60%)]" />
                {t.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default SimulationControls;
