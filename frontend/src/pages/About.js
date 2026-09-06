import React from "react";
import { DynIcon } from "@/components/DynIcon";

const POINTS = [
  ["Distributed sensing", "Every participating vehicle is a mobile sensing node."],
  ["Independent observations", "Many vehicles observe the same road from different vantage points."],
  ["Evidence fusion", "Observations are fused with confidence, agreement and freshness — not simple averaging."],
  ["Risk-aware road graph", "Road segments carry a live risk score that drives safe routing."],
  ["Emergency response", "Authorities receive prioritised, verified intelligence with explainability."],
];

export default function About() {
  return (
    <div className="mx-auto max-w-[900px] px-3 py-6 lg:px-5">
      <h1 className="text-2xl font-semibold tracking-tight">About ResQDrive</h1>
      <p className="mt-2 text-[15px] leading-relaxed text-muted-foreground">
        ResQDrive is a <span className="text-foreground">cooperative mobile sensing network for continuously updated road-risk intelligence</span> —
        not merely “AI detects floods”. It turns moving vehicles into a cooperative real-time road intelligence network.
      </p>

      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        {POINTS.map(([t, d]) => (
          <div key={t} className="rq-panel p-4">
            <div className="mb-1 flex items-center gap-2 font-semibold"><DynIcon name="CircleCheckBig" className="h-4 w-4 text-[hsl(150_70%_55%)]" />{t}</div>
            <p className="text-[13px] leading-relaxed text-muted-foreground">{d}</p>
          </div>
        ))}
      </div>

      <div className="mt-6 rounded-xl border border-[hsl(45_60%_28%)] bg-[hsl(42_60%_10%)] p-4" data-testid="about-prototype-disclaimer">
        <div className="mb-1 flex items-center gap-2 font-semibold text-[hsl(45_90%_72%)]"><DynIcon name="FlaskConical" className="h-4 w-4" /> Prototype disclaimer</div>
        <p className="text-[13px] leading-relaxed text-[hsl(45_85%_80%)]">
          This is a prototype built for the Smart India Hackathon. All vehicle, sensor and hazard data is <span className="font-semibold">SIMULATED</span>.
          No real cameras, GPS units, OBD-II hardware or edge devices are connected. Confidence values are illustrative prototype parameters, not scientifically validated accuracy claims. The system is not deployed in production.
        </p>
      </div>

      <div className="mt-6 rounded-xl border border-border bg-[hsl(220_16%_8%)] p-4 text-center text-sm text-muted-foreground">
        “Every vehicle becomes a sensor. Every road becomes intelligence.”
      </div>
    </div>
  );
}
