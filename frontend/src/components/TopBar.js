import React, { useEffect, useState } from "react";
import { NavLink, Link, useLocation } from "react-router-dom";
import { useApp } from "@/context/AppContext";
import { ResQDriveLogo } from "@/components/ResQDriveLogo";
import { DynIcon } from "@/components/DynIcon";
import { NAV_ITEMS, ROLES } from "@/lib/constants";
import { fmtClock } from "@/lib/format";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Menu } from "lucide-react";

function ConnectionPill({ connection }) {
  const map = {
    connected: { c: "hsl(150 70% 50%)", i: "Wifi", t: "Connected" },
    connecting: { c: "hsl(45 90% 58%)", i: "LoaderCircle", t: "Connecting" },
    reconnecting: { c: "hsl(45 90% 58%)", i: "LoaderCircle", t: "Reconnecting" },
    offline: { c: "hsl(8 85% 58%)", i: "WifiOff", t: "Offline" },
  };
  const s = map[connection] || map.connecting;
  return (
    <span data-testid="connection-status-pill" className="inline-flex items-center gap-1.5 rounded-full border border-border bg-secondary px-2 py-1 text-[11px] font-medium">
      <DynIcon name={s.i} className={`h-3.5 w-3.5 ${connection !== "connected" ? "animate-spin" : ""}`} style={{ color: s.c }} />
      <span className="hidden sm:inline">{s.t}</span>
    </span>
  );
}

function SimulationPill({ sim }) {
  const map = {
    RUNNING: { c: "hsl(150 70% 50%)", i: "Play", t: "Sim Running" },
    PAUSED: { c: "hsl(45 90% 58%)", i: "Pause", t: "Sim Paused" },
    STOPPED: { c: "hsl(215 12% 60%)", i: "Square", t: "Sim Stopped" },
  };
  const s = map[sim?.status] || map.STOPPED;
  return (
    <span data-testid="simulation-status-pill" className="inline-flex items-center gap-1.5 rounded-full border border-border bg-secondary px-2 py-1 text-[11px] font-medium">
      <DynIcon name={s.i} className="h-3.5 w-3.5" style={{ color: s.c }} />
      <span className="hidden md:inline">{s.t}</span>
      {sim?.status === "RUNNING" && <span className="mono hidden text-[10px] text-muted-foreground lg:inline">{sim.speed}x</span>}
    </span>
  );
}

export function TopBar() {
  const { connection, sim, role, setRole } = useApp();
  const [clock, setClock] = useState(new Date().toLocaleTimeString("en-GB", { hour12: false }));
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const t = setInterval(() => setClock(new Date().toLocaleTimeString("en-GB", { hour12: false })), 1000);
    return () => clearInterval(t);
  }, []);
  useEffect(() => { setMenuOpen(false); }, [location.pathname]);

  const navLinkClass = ({ isActive }) =>
    `inline-flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-[13px] font-medium transition-colors ${
      isActive ? "bg-primary/15 text-[hsl(190_85%_60%)]" : "text-muted-foreground hover:bg-white/5 hover:text-foreground"
    }`;

  return (
    <header className="sticky top-0 z-[900] border-b border-border bg-[hsl(220_18%_6%)]/95 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-[1720px] items-center gap-3 px-3 lg:px-5">
        <Link to="/" className="shrink-0"><ResQDriveLogo /></Link>

        <nav className="ml-2 hidden items-center gap-0.5 xl:flex">
          {NAV_ITEMS.map((n) => (
            <NavLink key={n.to} to={n.to} className={navLinkClass} data-testid={`nav-${n.label.toLowerCase().replace(/\s+/g, "-")}-link`}>
              <DynIcon name={n.icon} className="h-4 w-4" />
              {n.label}
            </NavLink>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-2">
          <span className="mono hidden items-center gap-1.5 rounded-full border border-border bg-secondary px-2 py-1 text-[11px] text-muted-foreground md:inline-flex">
            <DynIcon name="Clock" className="h-3.5 w-3.5" />{clock}
          </span>
          <span data-testid="demo-data-pill" className="hidden items-center gap-1 rounded-full border border-[hsl(45_70%_34%)] bg-[hsl(42_70%_12%)] px-2 py-1 text-[10px] font-semibold uppercase tracking-wide text-[hsl(45_90%_70%)] sm:inline-flex">
            <DynIcon name="FlaskConical" className="h-3 w-3" /> Demo Data
          </span>
          <ConnectionPill connection={connection} />
          <SimulationPill sim={sim} />

          <Select value={role} onValueChange={setRole}>
            <SelectTrigger data-testid="role-switcher" className="h-8 w-[118px] border-border bg-secondary text-xs">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {ROLES.map((r) => (
                <SelectItem key={r} value={r} className="text-xs" data-testid={`role-option-${r.toLowerCase()}`}>
                  <span className="flex items-center gap-2"><DynIcon name="UserCog" className="h-3.5 w-3.5" />{r}</span>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Sheet open={menuOpen} onOpenChange={setMenuOpen}>
            <SheetTrigger asChild>
              <button className="grid h-8 w-8 place-items-center rounded-md border border-border bg-secondary xl:hidden" data-testid="mobile-menu-button" aria-label="Open menu">
                <Menu className="h-4 w-4" />
              </button>
            </SheetTrigger>
            <SheetContent side="left" className="w-[260px] border-border bg-[hsl(220_16%_8%)] p-0">
              <SheetHeader className="border-b border-border p-4"><SheetTitle className="text-left"><ResQDriveLogo /></SheetTitle></SheetHeader>
              <nav className="flex flex-col gap-1 p-3">
                {[...NAV_ITEMS, { to: "/citizen", label: "Citizen", icon: "Users" }, { to: "/technology", label: "Technology", icon: "Cpu" }, { to: "/about", label: "About", icon: "Info" }].map((n) => (
                  <NavLink key={n.to} to={n.to} className={navLinkClass}>
                    <DynIcon name={n.icon} className="h-4 w-4" />{n.label}
                  </NavLink>
                ))}
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}

export default TopBar;
