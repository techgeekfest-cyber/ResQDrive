import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { DynIcon } from "@/components/DynIcon";
import { fmtTimeShort } from "@/lib/format";

const LEVEL = {
  info: { color: "hsl(190 85% 55%)", icon: "Info" },
  success: { color: "hsl(150 70% 52%)", icon: "CircleCheck" },
  warning: { color: "hsl(45 90% 58%)", icon: "TriangleAlert" },
  critical: { color: "hsl(8 85% 58%)", icon: "Siren" },
};
const CAT_ICON = {
  SYSTEM: "Cpu",
  DETECTION: "ScanEye",
  FUSION: "GitMerge",
  ROUTE: "Route",
  ALERT: "Siren",
  RESPONSE: "ShieldCheck",
  VEHICLE: "Car",
};

export function LiveEventFeed({ events = [], onSelectIncident, max = 60, dense = false }) {
  const list = events.slice(0, max);
  return (
    <div data-testid="live-event-feed" className="flex h-full flex-col">
      <div className="space-y-1 overflow-y-auto rq-scroll-fade pr-1" style={{ maxHeight: "100%" }}>
        {list.length === 0 && (
          <div className="flex flex-col items-center justify-center gap-2 py-10 text-center text-muted-foreground">
            <DynIcon name="Radio" className="h-6 w-6 opacity-50" />
            <div className="text-xs">No live events yet. Start the simulation to see the network respond.</div>
          </div>
        )}
        <AnimatePresence initial={false}>
          {list.map((e) => {
            const lv = LEVEL[e.level] || LEVEL.info;
            return (
              <motion.button
                key={e.id}
                type="button"
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.18 }}
                onClick={() => e.incident_id && onSelectIncident && onSelectIncident(e.incident_id)}
                data-testid="live-event-feed-row"
                className={`group flex w-full items-start gap-2 rounded-lg px-2 py-2 text-left transition-colors hover:bg-white/5 ${
                  e.incident_id ? "cursor-pointer" : "cursor-default"
                }`}
              >
                <div className="mt-0.5 grid h-6 w-6 shrink-0 place-items-center rounded-md" style={{ background: lv.color + "1f" }}>
                  <DynIcon name={CAT_ICON[e.category] || lv.icon} className="h-3.5 w-3.5" style={{ color: lv.color }} />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="mono text-[10px] text-muted-foreground">{fmtTimeShort(e.timestamp)}</span>
                    <span className="rounded bg-white/5 px-1 text-[9px] font-semibold uppercase tracking-wide text-muted-foreground">{e.category}</span>
                  </div>
                  <div className={`${dense ? "text-[12px]" : "text-[12.5px]"} leading-snug text-foreground/90`}>{e.message}</div>
                </div>
              </motion.button>
            );
          })}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default LiveEventFeed;
