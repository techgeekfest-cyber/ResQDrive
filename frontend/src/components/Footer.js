import React from "react";
import { Link } from "react-router-dom";
import { ResQDriveLogo } from "@/components/ResQDriveLogo";
import { DynIcon } from "@/components/DynIcon";

const LINKS = [
  { to: "/map", label: "Live Map" },
  { to: "/system", label: "Architecture" },
  { to: "/simulation", label: "Simulation" },
  { to: "/technology", label: "Technology" },
  { to: "/about", label: "About" },
];

export function Footer() {
  return (
    <footer className="border-t border-border bg-[hsl(220_16%_7%)]">
      <div className="mx-auto grid max-w-[1720px] gap-6 px-4 py-8 md:grid-cols-3 lg:px-6">
        <div>
          <ResQDriveLogo />
          <p className="mt-3 max-w-sm text-sm text-muted-foreground">
            Cooperative Vehicle-Based Disaster Intelligence Network. Turning moving
            vehicles into a cooperative real-time road intelligence network.
          </p>
        </div>
        <div className="md:justify-self-center">
          <div className="rq-label mb-3">Explore</div>
          <ul className="space-y-2 text-sm">
            {LINKS.map((l) => (
              <li key={l.to}>
                <Link to={l.to} className="text-muted-foreground transition-colors hover:text-[hsl(190_85%_60%)]">{l.label}</Link>
              </li>
            ))}
          </ul>
        </div>
        <div className="md:justify-self-end">
          <div className="rq-label mb-3">Prototype Notice</div>
          <div className="flex items-start gap-2 rounded-lg border border-[hsl(45_60%_28%)] bg-[hsl(42_60%_10%)] p-3 text-xs text-[hsl(45_80%_78%)]">
            <DynIcon name="FlaskConical" className="mt-0.5 h-4 w-4 shrink-0" />
            <span>Prototype for Smart India Hackathon — simulated vehicle and sensor data. No real sensors are connected.</span>
          </div>
        </div>
      </div>
      <div className="border-t border-border py-4 text-center text-xs text-muted-foreground">
        ResQDrive · Cooperative Vehicle-Based Disaster Intelligence Network · SIMULATED / DEMO DATA
      </div>
    </footer>
  );
}

export default Footer;
