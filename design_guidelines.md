{
  "product": {
    "name": "ResQDrive",
    "subtitle": "Cooperative Vehicle-Based Disaster Intelligence Network",
    "tagline": "Every vehicle becomes a sensor. Every road becomes intelligence.",
    "prototype_disclaimer": "SIMULATED / PROTOTYPE / DEMO DATA — for Smart India Hackathon demonstration only."
  },
  "visual_personality": {
    "keywords": [
      "dark professional",
      "high-contrast",
      "map-first",
      "command-center",
      "confidence-aware intelligence",
      "compact density",
      "restrained motion",
      "credible government-grade"
    ],
    "do_not": [
      "Do not look like a generic admin dashboard.",
      "Do not overuse gradients (max 20% viewport).",
      "Do not make every element glow.",
      "Do not use transparent backgrounds with dark text (define concrete dark surfaces).",
      "Do not rely on color alone for status (always icon + label)."
    ],
    "layout_principles": {
      "primary": "Map is the dominant element on all operator/authority pages.",
      "secondary": "Right-side intelligence rail (feed + incident drawer) with resizable panels.",
      "tertiary": "Top status bar + KPI strip for at-a-glance situational awareness.",
      "density": "Compact information density with strong grouping, separators, and consistent label/value rhythm."
    }
  },
  "design_tokens": {
    "notes": [
      "Implement tokens as CSS custom properties in /frontend/src/index.css under .dark (shadcn tokens).",
      "Use solid dark surfaces; use subtle glass only for overlays/panels on top of the map.",
      "Avoid purple in accents. Use cool-cyan/teal + neutral steel tones."
    ],
    "core": {
      "bg": {
        "app": "hsl(220 18% 6%)",
        "app_2": "hsl(220 16% 8%)",
        "surface": "hsl(220 14% 10%)",
        "surface_2": "hsl(220 12% 12%)",
        "surface_3": "hsl(220 10% 14%)"
      },
      "text": {
        "primary": "hsl(210 20% 96%)",
        "secondary": "hsl(215 14% 78%)",
        "muted": "hsl(215 10% 62%)",
        "disabled": "hsl(215 10% 45%)"
      },
      "border": {
        "subtle": "hsl(220 10% 22%)",
        "default": "hsl(220 10% 28%)",
        "strong": "hsl(220 10% 36%)"
      },
      "accent": {
        "primary": "hsl(190 85% 45%)",
        "primary_2": "hsl(185 70% 38%)",
        "ring": "hsl(190 85% 45%)",
        "link": "hsl(190 85% 55%)"
      },
      "shadow": {
        "elev_1": "0 1px 0 rgba(255,255,255,0.04), 0 10px 30px rgba(0,0,0,0.45)",
        "elev_2": "0 1px 0 rgba(255,255,255,0.05), 0 18px 50px rgba(0,0,0,0.55)"
      },
      "radius": {
        "panel": "14px",
        "control": "10px",
        "chip": "999px"
      }
    },
    "semantic_status": {
      "rules": [
        "These are FIXED semantic meanings: SAFE, CAUTION, UNSAFE, CRITICAL, UNKNOWN.",
        "Always pair color with icon + text label.",
        "Use these tokens for badges, map strokes, KPI accents, and table left-border indicators."
      ],
      "SAFE": {
        "bg": "hsl(152 55% 14%)",
        "fg": "hsl(150 70% 85%)",
        "stroke": "hsl(150 70% 45%)",
        "solid": "hsl(150 70% 45%)",
        "icon": "ShieldCheck"
      },
      "CAUTION": {
        "bg": "hsl(42 70% 14%)",
        "fg": "hsl(45 90% 86%)",
        "stroke": "hsl(45 90% 55%)",
        "solid": "hsl(45 90% 55%)",
        "icon": "AlertTriangle"
      },
      "UNSAFE": {
        "bg": "hsl(8 70% 14%)",
        "fg": "hsl(8 90% 88%)",
        "stroke": "hsl(8 85% 55%)",
        "solid": "hsl(8 85% 55%)",
        "icon": "ShieldAlert"
      },
      "CRITICAL": {
        "bg": "hsl(0 75% 12%)",
        "fg": "hsl(0 90% 90%)",
        "stroke": "hsl(0 85% 50%)",
        "solid": "hsl(0 85% 50%)",
        "icon": "Siren"
      },
      "UNKNOWN": {
        "bg": "hsl(220 10% 16%)",
        "fg": "hsl(215 10% 78%)",
        "stroke": "hsl(215 10% 55%)",
        "solid": "hsl(215 10% 55%)",
        "icon": "HelpCircle"
      }
    },
    "verification_state": {
      "UNVERIFIED": { "label": "Unverified", "tone": "neutral", "icon": "CircleDashed" },
      "CORROBORATED": { "label": "Corroborated", "tone": "info", "icon": "Link2" },
      "VERIFIED": { "label": "Verified", "tone": "success", "icon": "BadgeCheck" },
      "CONFLICTING": { "label": "Conflicting", "tone": "danger", "icon": "GitCompareArrows" },
      "STALE": { "label": "Stale", "tone": "muted", "icon": "Clock" }
    },
    "map_layer_colors": {
      "road_safe": "hsl(150 70% 45%)",
      "road_caution": "hsl(45 90% 55%)",
      "road_unsafe": "hsl(8 85% 55%)",
      "road_critical": "hsl(0 85% 50%)",
      "road_unknown": "hsl(215 10% 55%)",
      "route_fastest": "hsl(190 85% 55%)",
      "route_safe": "hsl(150 70% 55%)",
      "zone_outline": "rgba(255,255,255,0.18)",
      "zone_fill": "rgba(255,255,255,0.06)"
    }
  },
  "typography": {
    "google_fonts": {
      "ui": {
        "name": "IBM Plex Sans",
        "weights": [400, 500, 600]
      },
      "data_mono": {
        "name": "JetBrains Mono",
        "weights": [400, 500, 600]
      }
    },
    "usage": {
      "headings": "IBM Plex Sans 600 (tight tracking, authoritative)",
      "body": "IBM Plex Sans 400/500",
      "telemetry": "JetBrains Mono 500 for coordinates, timestamps, IDs, confidence breakdown numbers"
    },
    "scale_tailwind": {
      "h1": "text-4xl sm:text-5xl lg:text-6xl",
      "h2": "text-base md:text-lg",
      "body": "text-sm md:text-base",
      "small": "text-xs",
      "kpi_value": "text-2xl md:text-3xl font-semibold",
      "kpi_label": "text-xs uppercase tracking-wide"
    },
    "number_formatting": {
      "confidence": "Always show as integer percent (e.g., 78%)",
      "timestamps": "Use 24h time + relative (e.g., 14:32 • 2m ago)",
      "coordinates": "Monospace, 5 decimals max"
    }
  },
  "grid_and_spacing": {
    "container": {
      "desktop_max": "max-w-[1600px]",
      "page_padding": "px-3 sm:px-4 lg:px-6",
      "vertical_rhythm": "space-y-3 md:space-y-4"
    },
    "layout": {
      "command_center": {
        "grid": "grid grid-cols-12 gap-3 lg:gap-4",
        "map_span": "col-span-12 lg:col-span-8 xl:col-span-9",
        "rail_span": "col-span-12 lg:col-span-4 xl:col-span-3"
      },
      "full_map": {
        "map": "h-[calc(100vh-112px)] md:h-[calc(100vh-120px)]",
        "drawer": "right-0 top-[56px] h-[calc(100vh-56px)]"
      }
    },
    "radius_and_elevation": {
      "panel": "rounded-[var(--radius-panel)] shadow-[var(--shadow-elev-1)]",
      "panel_strong": "rounded-[var(--radius-panel)] shadow-[var(--shadow-elev-2)]",
      "control": "rounded-[var(--radius-control)]",
      "chip": "rounded-full"
    }
  },
  "surfaces_and_glass": {
    "panel_base_classes": "bg-[hsl(220_14%_10%)] border border-[hsl(220_10%_22%)]",
    "glass_overlay_classes": "bg-[rgba(15,18,24,0.72)] border border-[rgba(255,255,255,0.10)] backdrop-blur-md",
    "map_overlay_rules": [
      "Use glass overlays only on top of the map (filters, drawers, KPI strip).",
      "Keep overlay opacity >= 0.68 for readability.",
      "Never place long paragraphs on glass; keep it for controls and compact summaries."
    ],
    "noise_texture": {
      "approach": "Add a subtle noise overlay via CSS mask/linear-gradient (no heavy images).",
      "css_snippet": ".noise::before{content:'';position:absolute;inset:0;background-image:url('data:image/svg+xml;utf8,<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"120\" height=\"120\"><filter id=\"n\"><feTurbulence type=\"fractalNoise\" baseFrequency=\"0.9\" numOctaves=\"2\" stitchTiles=\"stitch\"/></filter><rect width=\"120\" height=\"120\" filter=\"url(%23n)\" opacity=\"0.08\"/></svg>');mix-blend-mode:overlay;pointer-events:none;}"
    }
  },
  "navigation_and_status_bar": {
    "top_bar": {
      "height": "h-14",
      "left": "Logo + product name + subtitle (truncate on small screens)",
      "center": "Primary nav (Command Center, Live Map, Vehicles, Hazards, Routes, Response, Simulation, System)",
      "right": "Role switcher + Connection status + Simulation status + Help",
      "classes": "sticky top-0 z-50 bg-[hsl(220_18%_6%)]/95 backdrop-blur border-b border-[hsl(220_10%_22%)]"
    },
    "status_pills": [
      {
        "name": "ConnectionPill",
        "states": ["Connected", "Reconnecting", "Offline"],
        "icons": ["Wifi", "LoaderCircle", "WifiOff"],
        "data_testid": "connection-status-pill"
      },
      {
        "name": "SimulationPill",
        "states": ["SIMULATION RUNNING", "PAUSED", "STOPPED"],
        "icons": ["Play", "Pause", "Square"],
        "data_testid": "simulation-status-pill"
      },
      {
        "name": "DemoDataPill",
        "label": "DEMO DATA",
        "icon": "FlaskConical",
        "data_testid": "demo-data-pill"
      }
    ]
  },
  "component_path": {
    "shadcn_primary": {
      "Button": "/app/frontend/src/components/ui/button.jsx",
      "Card": "/app/frontend/src/components/ui/card.jsx",
      "Badge": "/app/frontend/src/components/ui/badge.jsx",
      "Table": "/app/frontend/src/components/ui/table.jsx",
      "Tabs": "/app/frontend/src/components/ui/tabs.jsx",
      "Dialog": "/app/frontend/src/components/ui/dialog.jsx",
      "Drawer": "/app/frontend/src/components/ui/drawer.jsx",
      "Sheet": "/app/frontend/src/components/ui/sheet.jsx",
      "ScrollArea": "/app/frontend/src/components/ui/scroll-area.jsx",
      "Select": "/app/frontend/src/components/ui/select.jsx",
      "Popover": "/app/frontend/src/components/ui/popover.jsx",
      "Tooltip": "/app/frontend/src/components/ui/tooltip.jsx",
      "Separator": "/app/frontend/src/components/ui/separator.jsx",
      "Progress": "/app/frontend/src/components/ui/progress.jsx",
      "Switch": "/app/frontend/src/components/ui/switch.jsx",
      "Slider": "/app/frontend/src/components/ui/slider.jsx",
      "Input": "/app/frontend/src/components/ui/input.jsx",
      "Textarea": "/app/frontend/src/components/ui/textarea.jsx",
      "Calendar": "/app/frontend/src/components/ui/calendar.jsx",
      "Sonner": "/app/frontend/src/components/ui/sonner.jsx"
    },
    "custom_components_to_create": [
      {
        "name": "ResQDriveLogo",
        "type": "icon+wordmark",
        "icons": ["Car", "MapPin", "Network", "Siren"],
        "data_testid": "app-logo"
      },
      {
        "name": "RiskBadge",
        "purpose": "SAFE/CAUTION/UNSAFE/CRITICAL/UNKNOWN badge with icon + label",
        "data_testid": "risk-badge"
      },
      {
        "name": "VerificationBadge",
        "purpose": "UNVERIFIED/CORROBORATED/VERIFIED/CONFLICTING/STALE badge",
        "data_testid": "verification-badge"
      },
      {
        "name": "ConfidenceRing",
        "purpose": "Compact confidence visualization (0-100) for incident drawer + list rows",
        "data_testid": "confidence-ring"
      },
      {
        "name": "ConfidenceBreakdown",
        "purpose": "Why confidence is X% (additive breakdown + decay + conflict penalties)",
        "data_testid": "confidence-breakdown"
      },
      {
        "name": "LiveEventFeed",
        "purpose": "WebSocket-driven event list with severity + quick actions",
        "data_testid": "live-event-feed"
      },
      {
        "name": "MapOverlayControls",
        "purpose": "Filters, layers, legend, search, time window",
        "data_testid": "map-overlay-controls"
      },
      {
        "name": "IncidentIntelligenceDrawer",
        "purpose": "Slide-in drawer with evidence fusion details",
        "data_testid": "incident-intelligence-drawer"
      },
      {
        "name": "SimulationControlCenter",
        "purpose": "Start/Pause/Reset, speed, scenario, inject hazards",
        "data_testid": "simulation-control-center"
      }
    ]
  },
  "page_blueprints": {
    "landing": {
      "goal": "Credible prototype intro + fast path into demo.",
      "hero_layout": {
        "structure": "Left: headline + tagline + CTAs. Right: stylized network/map concept (SVG/canvas) with restrained motion.",
        "cta_buttons": [
          { "label": "Explore Live Map", "variant": "default", "data_testid": "landing-cta-live-map" },
          { "label": "Launch Demo", "variant": "secondary", "data_testid": "landing-cta-launch-demo" },
          { "label": "View Architecture", "variant": "outline", "data_testid": "landing-cta-architecture" }
        ],
        "background": "Solid dark with a small (<=20% viewport) diagonal mild gradient accent in the top-right only."
      },
      "sections": [
        "THE PROBLEM",
        "THE SOLUTION",
        "THE INNOVATION",
        "How It Works (8-step strip)",
        "Innovation callout: One vehicle can detect. Many vehicles can verify.",
        "Footer with prototype disclaimer"
      ],
      "how_it_works_component": {
        "pattern": "Horizontal stepper strip (scrollable on mobile) with icons + short labels",
        "steps": ["SENSE", "DETECT", "LOCATE", "FUSE", "SCORE", "MAP", "ROUTE", "RESPOND"],
        "data_testid": "how-it-works-strip"
      }
    },
    "command_center_overview": {
      "structure": "Top KPI strip + main grid: Map (dominant) + Right rail (feed + selected incident).",
      "kpis": [
        { "label": "Active Vehicles", "data_testid": "kpi-active-vehicles" },
        { "label": "Active Hazards", "data_testid": "kpi-active-hazards" },
        { "label": "Roads at Risk", "data_testid": "kpi-roads-at-risk" },
        { "label": "Verified Incidents", "data_testid": "kpi-verified-incidents" },
        { "label": "Network Confidence", "data_testid": "kpi-network-confidence" },
        { "label": "Priority Zones", "data_testid": "kpi-priority-zones" }
      ],
      "right_rail": {
        "top": "LiveEventFeed",
        "bottom": "IncidentIntelligenceDrawer (docked mode on desktop, sheet on mobile)"
      }
    },
    "live_map": {
      "structure": "Full-bleed map + overlay controls + slide-in incident drawer.",
      "overlays": [
        "Layer toggles (Road risk, Vehicles, Hazards, Zones, Routes)",
        "Legend (Risk + Verification)",
        "Time window slider (last 5m/15m/1h)",
        "Search (road/area/incident id)",
        "Role-aware quick actions"
      ]
    },
    "vehicles": {
      "structure": "Fleet table (left) + detail drawer (right).",
      "table_columns": ["Vehicle ID", "Role", "Last Seen", "GPS", "Camera", "IMU", "Network", "Current Risk"],
      "detail": ["Telemetry", "Recent observations", "Sensor health", "Route trace"]
    },
    "hazards": {
      "structure": "Incident list + fusion explainability panel.",
      "must_include": [
        "VerificationBadge",
        "ConfidenceRing",
        "Evidence count + agreement % + freshness",
        "Confidence timeline chart",
        "Evidence graph (vehicles contributing)"
      ]
    },
    "routes": {
      "structure": "Inputs (start/destination) + two comparison cards + avoided roads list.",
      "cards": [
        "Fastest Route (risk may be higher)",
        "Recommended Safe Route (risk minimized)"
      ],
      "data_testids": {
        "start": "routes-start-input",
        "destination": "routes-destination-input",
        "compute": "routes-compute-button"
      }
    },
    "response": {
      "structure": "KPIs + priority incident table (P1-P4) + action buttons.",
      "actions": [
        { "label": "Acknowledge", "data_testid": "response-acknowledge-button" },
        { "label": "Dispatch", "data_testid": "response-dispatch-button" },
        { "label": "Monitoring", "data_testid": "response-monitoring-button" },
        { "label": "Resolve", "data_testid": "response-resolve-button" }
      ]
    },
    "simulation": {
      "structure": "Control center + inject panel + event log + map preview.",
      "controls": ["Start", "Pause", "Reset", "Speed 1x/2x/5x/10x", "Scenario selector"],
      "inject": ["Flood", "Landslide", "Road Blockage", "Fallen Tree", "Pothole", "Conflicting Evidence", "Road Clear"],
      "data_testids": {
        "start": "simulation-start-button",
        "pause": "simulation-pause-button",
        "reset": "simulation-reset-button",
        "speed": "simulation-speed-toggle",
        "scenario": "simulation-scenario-select",
        "inject_panel": "simulation-inject-panel",
        "event_log": "simulation-event-log"
      }
    },
    "system": {
      "structure": "Layered architecture diagram + short explanations.",
      "diagram": "Vehicle → Edge AI → Communication → Cloud Intelligence → Application → Users",
      "data_testid": "system-architecture-diagram"
    },
    "technology": {
      "structure": "Two columns of stack cards: Prototype Architecture vs Planned Production Stack.",
      "data_testid": "technology-stack-cards"
    },
    "about": {
      "structure": "Product positioning + prototype disclaimers + team credits.",
      "data_testid": "about-prototype-disclaimer"
    },
    "citizen": {
      "structure": "Simplified map + route + hazard reporting form.",
      "form_fields": ["Location", "Hazard type", "Description", "Optional photo (prototype)", "Consent"],
      "data_testids": {
        "report_form": "citizen-hazard-report-form",
        "submit": "citizen-hazard-report-submit"
      }
    }
  },
  "component_specs": {
    "kpi_card": {
      "base": "Card with compact header, big value, tiny sparkline optional",
      "classes": "relative overflow-hidden rounded-[var(--radius-panel)] bg-[hsl(220_14%_10%)] border border-[hsl(220_10%_22%)] p-3",
      "accent_rule": "Add a 2px top border accent that reflects KPI type (use accent.primary for neutral KPIs; use semantic colors for risk KPIs).",
      "data_testid": "kpi-card"
    },
    "risk_badge": {
      "pattern": "Badge + icon + label (SAFE/CAUTION/UNSAFE/CRITICAL/UNKNOWN)",
      "classes": "inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium border",
      "accessibility": "Include sr-only text like 'Road status: SAFE'.",
      "data_testid": "risk-badge"
    },
    "verification_badge": {
      "pattern": "Badge with icon + label + optional dot",
      "classes": "inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium border",
      "data_testid": "verification-badge"
    },
    "confidence_ring": {
      "pattern": "Small ring (32-40px) with percent in center; stroke color based on verification state + risk",
      "performance": "Use SVG circle with stroke-dasharray; avoid per-frame animation; animate only on value change.",
      "data_testid": "confidence-ring"
    },
    "incident_panel_drawer": {
      "pattern": "Drawer/Sheet with tabs: Summary, Evidence, Explainability, Timeline",
      "tabs": ["Summary", "Evidence", "Why Confidence?", "Timeline"],
      "classes": "bg-[rgba(15,18,24,0.78)] backdrop-blur-md border-l border-[rgba(255,255,255,0.10)]",
      "data_testid": "incident-intelligence-drawer"
    },
    "live_event_feed_row": {
      "pattern": "Dense row: time, icon, title, chips (risk + verification), quick action",
      "classes": "group flex items-start gap-2 rounded-[10px] px-2 py-2 hover:bg-white/5 focus-within:bg-white/5",
      "motion": "Animate entrance with framer-motion y:6→0 opacity:0→1 (duration 0.18) only when new events arrive.",
      "data_testid": "live-event-feed-row"
    },
    "fleet_table": {
      "pattern": "shadcn Table with sticky header + row hover + status mini-icons",
      "classes": "[&_*]:text-sm",
      "data_testid": "fleet-table"
    },
    "route_comparison_cards": {
      "pattern": "Two cards side-by-side on desktop, stacked on mobile; each shows ETA, distance, risk summary, avoided roads",
      "classes": "grid grid-cols-1 lg:grid-cols-2 gap-3",
      "data_testid": "route-comparison"
    },
    "simulation_controls": {
      "pattern": "Control bar with segmented speed toggle + scenario select + primary start/pause",
      "components": ["Button", "ToggleGroup", "Select", "Slider"],
      "data_testid": "simulation-control-center"
    },
    "priority_table": {
      "pattern": "Table with left priority stripe (P1 deep red → P4 muted) + action buttons",
      "data_testid": "priority-incident-table"
    }
  },
  "map_ui_guidelines": {
    "library": {
      "map": "Leaflet + OpenStreetMap via react-leaflet",
      "notes": [
        "Prefer canvas renderer for many polylines/markers.",
        "Cluster markers if needed; throttle updates.",
        "Keep marker DOM minimal; use DivIcon sparingly."
      ]
    },
    "map_style": {
      "basemap": "Use a dark OSM tile provider (ensure license attribution).",
      "overlay": "Road segments colored by risk; add subtle outer glow ONLY for CRITICAL segments (very restrained).",
      "legend": "Always visible on desktop; collapsible on mobile.",
      "labels": "Use monospace for coordinates and incident IDs in popups."
    },
    "marker_specs": {
      "vehicle": {
        "shape": "small arrow/chevron marker indicating heading",
        "color": "accent.primary",
        "state": "If sensor health degraded, add amber outline + tooltip",
        "data_testid": "map-vehicle-marker"
      },
      "hazard": {
        "shape": "pin with hazard icon",
        "color": "based on risk",
        "pulse": "Only for UNSAFE/CRITICAL and only 2 cycles on creation (not infinite)",
        "data_testid": "map-hazard-marker"
      }
    },
    "popups": {
      "content": [
        "Hazard type",
        "RiskBadge",
        "VerificationBadge",
        "Confidence %",
        "Evidence count",
        "Freshness",
        "CTA: Open Intelligence"
      ],
      "data_testid": "map-incident-popup"
    }
  },
  "charts_and_visualization": {
    "library": "recharts",
    "charts": [
      {
        "name": "HazardsByType",
        "type": "bar",
        "data_testid": "chart-hazards-by-type"
      },
      {
        "name": "VerifiedVsUnverified",
        "type": "stacked bar",
        "data_testid": "chart-verified-vs-unverified"
      },
      {
        "name": "RoadRiskDistribution",
        "type": "donut",
        "data_testid": "chart-road-risk-distribution"
      },
      {
        "name": "ConfidenceEvolution",
        "type": "line",
        "data_testid": "chart-confidence-evolution"
      }
    ],
    "styling": {
      "grid": "stroke: rgba(255,255,255,0.08)",
      "axis": "tick fill: rgba(255,255,255,0.65)",
      "tooltip": "Use shadcn Card-like tooltip with glass overlay"
    }
  },
  "motion_microinteractions": {
    "principles": [
      "Restrained, purposeful motion only.",
      "No infinite glowing animations.",
      "Prefer opacity/translate micro-motions over scale for dense UIs.",
      "Throttle map updates; animate only on state changes."
    ],
    "recommended": [
      {
        "interaction": "Button hover",
        "css": "hover:bg-white/8 hover:border-white/20 transition-colors duration-150",
        "note": "Never use transition: all"
      },
      {
        "interaction": "New feed event",
        "framer": "initial={{opacity:0,y:6}} animate={{opacity:1,y:0}} transition={{duration:0.18}}"
      },
      {
        "interaction": "Confidence change",
        "framer": "animate number count-up over 250ms; ring stroke animates once"
      },
      {
        "interaction": "Route draw",
        "note": "Animate polyline dash offset once on compute; keep duration <= 400ms"
      },
      {
        "interaction": "Hazard marker attention",
        "note": "Pulse twice on creation for UNSAFE/CRITICAL only; then stop"
      }
    ],
    "reduced_motion": "Respect prefers-reduced-motion: disable pulses and entrance animations."
  },
  "accessibility": {
    "requirements": [
      "WCAG AA contrast for text on dark surfaces.",
      "Status never relies on color alone: always icon + label.",
      "Visible focus rings using accent.ring.",
      "Keyboard navigable drawers, dialogs, menus (Radix/shadcn).",
      "Provide aria-labels for icon-only buttons.",
      "Use tooltips for dense icon controls."
    ]
  },
  "testing_attributes": {
    "rule": "All interactive and key informational elements MUST include data-testid in kebab-case.",
    "examples": [
      "data-testid=\"nav-command-center-link\"",
      "data-testid=\"map-layer-toggle-road-risk\"",
      "data-testid=\"incident-open-intelligence-button\"",
      "data-testid=\"vehicle-detail-drawer\"",
      "data-testid=\"hazard-filter-select\""
    ]
  },
  "image_urls": {
    "landing_hero_background": [
      {
        "url": "https://images.unsplash.com/photo-1617660872989-e489537acc27?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDJ8MHwxfHNlYXJjaHwxfHxkYXJrJTIwY2l0eSUyMHJvYWQlMjBuZXR3b3JrJTIwYWVyaWFsJTIwbmlnaHR8ZW58MHx8fHRlYWx8MTc4ODcwMzQ5NHww&ixlib=rb-4.1.0&q=85",
        "description": "Optional landing hero backdrop (use as subtle masked image at 10–14% opacity).",
        "category": "landing"
      }
    ],
    "system_about_support": [
      {
        "url": "https://images.unsplash.com/photo-1565164370954-8eac883fb7c8?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1MTN8MHwxfHNlYXJjaHwyfHxlbWVyZ2VuY3klMjBvcGVyYXRpb25zJTIwY2VudGVyJTIwY29udHJvbCUyMHJvb20lMjBkYXJrfGVufDB8fHxibGFja3wxNzg4NzAzNDk0fDA&ixlib=rb-4.1.0&q=85",
        "description": "Optional About/System page supporting image (use in a small side card, not full-bleed).",
        "category": "about/system"
      }
    ],
    "decorative_network_texture": [
      {
        "url": "https://images.pexels.com/photos/12537427/pexels-photo-12537427.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "description": "Decorative network texture for landing section dividers (use as masked overlay <= 8% opacity).",
        "category": "decorative"
      }
    ]
  },
  "libraries_and_integrations": {
    "react_leaflet": {
      "install": "npm i leaflet react-leaflet",
      "notes": [
        "Import leaflet CSS once in index.js or App.js: import 'leaflet/dist/leaflet.css';",
        "Prefer Canvas renderer for performance when drawing many polylines.",
        "Keep marker updates batched; avoid re-creating icons each tick."
      ]
    },
    "framer_motion": {
      "usage": "Use for feed row entrance, drawer transitions, and small count-up animations only. Avoid animating the map container."
    },
    "recharts": {
      "usage": "Use for analytics and confidence timeline; keep charts in panels, not over the map."
    }
  },
  "instructions_to_main_agent": [
    "Switch app to dark mode by default: add 'dark' class on html/body root and replace current light tokens in index.css with the provided dark tokens.",
    "Remove any centered App-header demo styling from App.css; do not center the entire app container.",
    "Implement a persistent TopBar with: ResQDrive logo, nav, role switcher, connection + simulation status pills, and a DEMO DATA pill.",
    "Build Command Center layout first: KPI strip + Map + Right rail (LiveEventFeed + Incident drawer). This is the hero of the demo.",
    "Create RiskBadge + VerificationBadge components (lucide icons + label) and use them everywhere (map popups, tables, feed rows, incident drawer).",
    "Ensure every interactive element and key info element has data-testid (kebab-case).",
    "Keep motion restrained and performant; no infinite pulses except optional subtle map marker attention limited to 2 cycles.",
    "All pages must clearly label SIMULATED/PROTOTYPE/DEMO DATA where relevant (status bar + page headers + simulation panels)."
  ]
}

<General UI UX Design Guidelines>  
    - You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms
    - You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text
   - NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json

 **GRADIENT RESTRICTION RULE**
NEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc
NEVER use dark gradients for logo, testimonial, footer etc
NEVER let gradients cover more than 20% of the viewport.
NEVER apply gradients to text-heavy content or reading areas.
NEVER use gradients on small UI elements (<100px width).
NEVER stack multiple gradient layers in the same viewport.

**ENFORCEMENT RULE:**
    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors

**How and where to use:**
   • Section backgrounds (not content backgrounds)
   • Hero section header content. Eg: dark to light to dark color
   • Decorative overlays and accent elements only
   • Hero section with 2-3 mild color
   • Gradients creation can be done for any angle say horizontal, vertical or diagonal

- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc**

</Font Guidelines>

- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. 
   
- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.

- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.
   
- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly
    Eg: - if it implies playful/energetic, choose a colorful scheme
           - if it implies monochrome/minimal, choose a black–white/neutral scheme

**Component Reuse:**
	- Prioritize using pre-existing components from src/components/ui when applicable
	- Create new components that match the style and conventions of existing components when needed
	- Examine existing components to understand the project's component patterns before creating new ones

**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component

**Best Practices:**
	- Use Shadcn/UI as the primary component library for consistency and accessibility
	- Import path: ./components/[component-name]

**Export Conventions:**
	- Components MUST use named exports (export const ComponentName = ...)
	- Pages MUST use default exports (export default function PageName() {...})

**Toasts:**
  - Use `sonner` for toasts"
  - Sonner component are located in `/app/src/components/ui/sonner.tsx`

Use 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals.
</General UI UX Design Guidelines>
