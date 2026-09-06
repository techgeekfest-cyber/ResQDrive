import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { ResQDriveLogo } from "@/components/ResQDriveLogo";
import { Footer } from "@/components/Footer";
import { DynIcon } from "@/components/DynIcon";
import { Button } from "@/components/ui/button";

const STEPS = [
  ["Sense", "Radio"], ["Detect", "ScanEye"], ["Locate", "MapPin"], ["Fuse", "GitMerge"],
  ["Score", "Gauge"], ["Map", "Map"], ["Route", "Route"], ["Respond", "Siren"],
];

function HeroVisual() {
  return (
    <svg viewBox="0 0 520 420" className="h-full w-full" role="img" aria-label="Stylised cooperative road-sensing network">
      <defs>
        <radialGradient id="g1" cx="50%" cy="40%" r="70%">
          <stop offset="0%" stopColor="hsl(190 85% 20%)" stopOpacity="0.5" />
          <stop offset="100%" stopColor="hsl(220 30% 8%)" stopOpacity="0" />
        </radialGradient>
      </defs>
      <rect x="0" y="0" width="520" height="420" fill="url(#g1)" />
      {/* roads */}
      <g stroke="hsl(220 12% 30%)" strokeWidth="3" fill="none">
        <path d="M40 340 L200 250 L330 300 L480 210" />
        <path d="M60 120 L190 170 L300 120 L470 150" />
        <path d="M200 250 L190 170" />
        <path d="M330 300 L300 120" />
        <path d="M40 340 L60 120" />
      </g>
      {/* unsafe segment */}
      <path d="M200 250 L330 300" stroke="hsl(8 85% 56%)" strokeWidth="4" fill="none" />
      <path d="M300 120 L470 150" stroke="hsl(45 90% 55%)" strokeWidth="4" fill="none" />
      {/* hazard node */}
      <g>
        <circle cx="265" cy="275" r="22" fill="hsl(8 85% 56%)" opacity="0.16">
          <animate attributeName="r" values="18;30;18" dur="2.4s" repeatCount="indefinite" />
        </circle>
        <circle cx="265" cy="275" r="8" fill="hsl(8 85% 56%)" stroke="#fff" strokeWidth="2" />
      </g>
      {/* vehicles converging (evidence) */}
      {[[120, 300], [210, 210], [360, 250], [300, 180]].map(([x, y], i) => (
        <g key={i}>
          <line x1={x} y1={y} x2="265" y2="275" stroke="hsl(190 85% 55%)" strokeWidth="1" strokeDasharray="3 4" opacity="0.5" />
          <circle cx={x} cy={y} r="5" fill="hsl(190 85% 55%)" />
        </g>
      ))}
      {/* safe route */}
      <path d="M40 340 L60 120 L300 120 L470 150" stroke="hsl(150 70% 52%)" strokeWidth="3" fill="none" strokeDasharray="7 6">
        <animate attributeName="stroke-dashoffset" values="40;0" dur="1.6s" repeatCount="indefinite" />
      </path>
    </svg>
  );
}

export default function Landing() {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 border-b border-border bg-[hsl(220_18%_6%)]/95 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-[1200px] items-center px-4">
          <ResQDriveLogo />
          <nav className="ml-auto flex items-center gap-1">
            <Link to="/system" className="hidden rounded-md px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground sm:block">Architecture</Link>
            <Link to="/technology" className="hidden rounded-md px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground sm:block">Technology</Link>
            <Button size="sm" onClick={() => navigate("/command")} className="ml-2 gap-1.5" data-testid="landing-enter-command">
              Enter Command Center <DynIcon name="ArrowRight" className="h-4 w-4" />
            </Button>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden border-b border-border">
        <div className="rq-grid-bg pointer-events-none absolute inset-0 opacity-[0.15]" />
        <div className="mx-auto grid max-w-[1200px] items-center gap-8 px-4 py-16 lg:grid-cols-2 lg:py-24">
          <div>
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-[hsl(45_60%_30%)] bg-[hsl(42_60%_10%)] px-3 py-1 text-[11px] font-semibold uppercase tracking-wide text-[hsl(45_90%_70%)]">
              <DynIcon name="FlaskConical" className="h-3.5 w-3.5" /> Prototype · Smart India Hackathon
            </div>
            <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl lg:text-6xl">
              ResQ<span className="text-[hsl(190_85%_55%)]">Drive</span>
            </h1>
            <p className="mt-3 text-lg font-medium text-foreground/90 sm:text-xl">
              Every vehicle becomes a sensor. Every road becomes intelligence.
            </p>
            <p className="mt-4 max-w-xl text-[15px] leading-relaxed text-muted-foreground">
              An AI-powered cooperative vehicle sensing network that transforms distributed
              road observations into continuously updated, confidence-aware disaster intelligence.
            </p>
            <div className="mt-7 flex flex-wrap gap-3">
              <Button onClick={() => navigate("/map")} className="gap-2" data-testid="landing-cta-live-map">
                <DynIcon name="Map" className="h-4 w-4" /> Explore Live Map
              </Button>
              <Button variant="secondary" onClick={() => navigate("/simulation")} className="gap-2" data-testid="landing-cta-launch-demo">
                <DynIcon name="Play" className="h-4 w-4" /> Launch Demo
              </Button>
              <Button variant="outline" onClick={() => navigate("/system")} className="gap-2 border-border" data-testid="landing-cta-architecture">
                <DynIcon name="Network" className="h-4 w-4" /> View Architecture
              </Button>
            </div>
          </div>
          <div className="rq-panel relative aspect-[13/10] overflow-hidden p-2">
            <HeroVisual />
            <div className="absolute bottom-3 left-3 rounded-md rq-glass px-2.5 py-1 text-[11px] text-muted-foreground">
              Live cooperative evidence fusion — SIMULATED
            </div>
          </div>
        </div>
      </section>

      {/* Problem / Solution / Innovation */}
      <section className="mx-auto max-w-[1200px] px-4 py-14">
        <div className="grid gap-4 md:grid-cols-3">
          {[
            ["The Problem", "CloudRain", "During disasters, road conditions can change within minutes. Static maps and manual reports cannot keep up, and drivers and responders act on stale information."],
            ["The Solution", "Car", "Turn moving vehicles into mobile sensing nodes. Cameras, GPS and motion sensors observe roads continuously and stream observations to the network."],
            ["The Innovation", "GitMerge", "Fuse independent observations from many vehicles into confidence-aware road intelligence — corroboration raises confidence, conflict lowers it, and freshness decays over time."],
          ].map(([t, icon, d]) => (
            <div key={t} className="rq-panel p-5">
              <div className="mb-3 grid h-10 w-10 place-items-center rounded-lg bg-primary/15">
                <DynIcon name={icon} className="h-5 w-5 text-[hsl(190_85%_60%)]" />
              </div>
              <h3 className="text-lg font-semibold">{t}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{d}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="border-y border-border bg-[hsl(220_16%_7%)]">
        <div className="mx-auto max-w-[1200px] px-4 py-14">
          <h2 className="text-center text-2xl font-semibold">How It Works</h2>
          <p className="mx-auto mt-2 max-w-lg text-center text-sm text-muted-foreground">The complete intelligence pipeline, from a single camera frame to prioritised emergency response.</p>
          <div className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-8" data-testid="how-it-works-strip">
            {STEPS.map(([label, icon], i) => (
              <div key={label} className="rq-panel flex flex-col items-center gap-2 p-4 text-center">
                <span className="mono text-[11px] text-muted-foreground">0{i + 1}</span>
                <DynIcon name={icon} className="h-6 w-6 text-[hsl(190_85%_60%)]" />
                <span className="text-[13px] font-semibold">{label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Innovation callout */}
      <section className="mx-auto max-w-[1200px] px-4 py-16 text-center">
        <h2 className="text-2xl font-semibold sm:text-3xl">One vehicle can detect.<br /><span className="text-[hsl(190_85%_60%)]">Many vehicles can verify.</span></h2>
        <div className="mx-auto mt-8 grid max-w-3xl gap-3 sm:grid-cols-3">
          {[
            ["Single observation", "→ Candidate incident", "CircleDashed"],
            ["Independent observations", "→ Corroborated & verified", "BadgeCheck"],
            ["Continuous new evidence", "→ Dynamic confidence & routing", "Activity"],
          ].map(([a, b, icon]) => (
            <div key={a} className="rq-panel p-5 text-left">
              <DynIcon name={icon} className="h-5 w-5 text-[hsl(150_70%_55%)]" />
              <div className="mt-2 text-sm font-semibold">{a}</div>
              <div className="text-sm text-muted-foreground">{b}</div>
            </div>
          ))}
        </div>
        <div className="mt-10">
          <Button size="lg" onClick={() => navigate("/command")} className="gap-2">
            Open the Command Center <DynIcon name="ArrowRight" className="h-4 w-4" />
          </Button>
        </div>
      </section>

      <Footer />
    </div>
  );
}
