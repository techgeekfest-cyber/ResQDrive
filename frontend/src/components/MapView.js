import React, { useEffect, useMemo } from "react";
import {
  MapContainer, TileLayer, Polyline, CircleMarker, Popup, Tooltip, useMap,
} from "react-leaflet";
import { STATUS_COLORS, HAZARD_META, MAP_CENTER, MAP_ZOOM } from "@/lib/constants";
import { RiskBadge } from "@/components/RiskBadge";
import { VerificationBadge } from "@/components/VerificationBadge";
import { DynIcon } from "@/components/DynIcon";

const VEHICLE_COLORS = {
  EMERGENCY: "hsl(8 85% 58%)",
  OBSERVING: "hsl(45 90% 58%)",
  DISCONNECTED: "hsl(215 10% 45%)",
  TRANSMITTING: "hsl(190 85% 55%)",
  ACTIVE: "hsl(190 70% 50%)",
};

const INFRA_ICON = {
  HOSPITAL: "Cross", FIRE: "Flame", POLICE: "Shield", SHELTER: "Home", EMERGENCY: "Siren",
};

function Recenter({ focus }) {
  const map = useMap();
  useEffect(() => {
    if (focus && focus.length === 2) {
      map.flyTo(focus, Math.max(map.getZoom(), 14), { duration: 0.8 });
    }
  }, [focus, map]);
  return null;
}

function roadStyle(state) {
  const c = STATUS_COLORS[state] || STATUS_COLORS.UNKNOWN;
  const weight = state === "UNSAFE" ? 6 : state === "CAUTION" ? 4.5 : 3;
  return { color: c.solid, weight, opacity: state === "SAFE" ? 0.55 : 0.9 };
}

export function MapView({
  incidents = [], roads = [], vehicles = [], infrastructure = [],
  routes = null, layers = {}, onSelectIncident, focus = null,
  selectedId = null, height = "100%",
}) {
  const L = {
    roads: true, vehicles: true, hazards: true, infrastructure: true, routes: true, ...layers,
  };

  const activeIncidents = useMemo(
    () => incidents.filter((i) => i.response_status !== "RESOLVED"),
    [incidents],
  );

  return (
    <div style={{ height }} className="h-full w-full overflow-hidden rounded-xl border border-border">
      <MapContainer
        center={MAP_CENTER}
        zoom={MAP_ZOOM}
        preferCanvas
        scrollWheelZoom
        style={{ height: "100%", width: "100%" }}
        zoomControl
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
          subdomains="abc"
          className="rq-dark-tiles"
          maxZoom={19}
        />
        <Recenter focus={focus} />

        {L.roads && roads.map((r) => (
          <Polyline key={r.id} positions={r.coordinates} pathOptions={roadStyle(r.risk_state)}>
            <Tooltip sticky>
              <span className="mono text-[11px]">{r.name} · risk {r.risk_score} · {r.risk_state}</span>
            </Tooltip>
          </Polyline>
        ))}

        {L.routes && routes?.safe?.coordinates && (
          <Polyline positions={routes.safe.coordinates} pathOptions={{ color: "hsl(150 70% 55%)", weight: 6, opacity: 0.95 }} />
        )}
        {L.routes && routes?.fastest?.coordinates && (
          <Polyline positions={routes.fastest.coordinates} pathOptions={{ color: "hsl(190 85% 60%)", weight: 4, opacity: 0.85, dashArray: "6 8" }} />
        )}

        {L.infrastructure && infrastructure.map((inf) => (
          <CircleMarker
            key={inf.id}
            center={[inf.latitude, inf.longitude]}
            radius={5}
            pathOptions={{ color: "hsl(190 40% 75%)", weight: 1.5, fillColor: "hsl(220 20% 30%)", fillOpacity: 0.9 }}
          >
            <Tooltip>
              <span className="flex items-center gap-1.5 text-[11px]">
                <DynIcon name={INFRA_ICON[inf.type] || "MapPin"} className="h-3 w-3" />{inf.name}
              </span>
            </Tooltip>
          </CircleMarker>
        ))}

        {L.vehicles && vehicles.map((v) => (
          <CircleMarker
            key={v.id}
            center={[v.latitude, v.longitude]}
            radius={v.status === "OBSERVING" || v.status === "EMERGENCY" ? 4.5 : 3}
            pathOptions={{
              color: "rgba(255,255,255,0.5)", weight: v.status === "OBSERVING" ? 1.5 : 0,
              fillColor: VEHICLE_COLORS[v.status] || VEHICLE_COLORS.ACTIVE, fillOpacity: 0.95,
            }}
          >
            <Tooltip>
              <span className="mono text-[11px]">{v.id} · {v.status} · {v.speed} km/h</span>
            </Tooltip>
          </CircleMarker>
        ))}

        {L.hazards && activeIncidents.map((inc) => {
          const c = STATUS_COLORS[inc.risk_state] || STATUS_COLORS.UNKNOWN;
          const isSel = inc.id === selectedId;
          const radius = 6 + Math.round((inc.risk_score || 0) / 22);
          const meta = HAZARD_META[inc.hazard_type] || {};
          return (
            <React.Fragment key={inc.id}>
              {(inc.risk_state === "UNSAFE" || inc.risk_state === "CRITICAL") && (
                <CircleMarker center={[inc.latitude, inc.longitude]} radius={radius + 9}
                  pathOptions={{ color: c.solid, weight: 0, fillColor: c.solid, fillOpacity: 0.14 }} />
              )}
              <CircleMarker
                center={[inc.latitude, inc.longitude]}
                radius={radius}
                pathOptions={{
                  color: isSel ? "#fff" : "rgba(255,255,255,0.85)",
                  weight: isSel ? 3 : 2,
                  fillColor: c.solid, fillOpacity: 0.9,
                }}
                eventHandlers={{ click: () => onSelectIncident && onSelectIncident(inc.id) }}
              >
                <Popup>
                  <div className="w-56" data-testid="map-incident-popup">
                    <div className="mb-1 flex items-center gap-1.5 font-semibold">
                      <DynIcon name={meta.icon || "TriangleAlert"} className="h-4 w-4" style={{ color: c.solid }} />
                      {meta.label || inc.hazard_type}
                    </div>
                    <div className="mb-2 text-[11px] text-muted-foreground">{inc.road_name}</div>
                    <div className="mb-2 flex flex-wrap gap-1.5">
                      <RiskBadge state={inc.risk_state} score={inc.risk_score} />
                      <VerificationBadge state={inc.verification_status} />
                    </div>
                    <div className="mono grid grid-cols-2 gap-x-2 gap-y-0.5 text-[11px]">
                      <span className="text-muted-foreground">Confidence</span><span className="text-right">{inc.confidence}%</span>
                      <span className="text-muted-foreground">Evidence</span><span className="text-right">{inc.evidence_count} veh</span>
                      <span className="text-muted-foreground">Freshness</span><span className="text-right">{inc.freshness}%</span>
                      <span className="text-muted-foreground">Priority</span><span className="text-right">{inc.priority}</span>
                    </div>
                    <button
                      onClick={() => onSelectIncident && onSelectIncident(inc.id)}
                      className="mt-2 w-full rounded-md bg-primary/20 px-2 py-1 text-[12px] font-semibold text-[hsl(190_85%_65%)] transition-colors hover:bg-primary/30"
                      data-testid="incident-open-intelligence-button"
                    >
                      Open Intelligence →
                    </button>
                  </div>
                </Popup>
              </CircleMarker>
            </React.Fragment>
          );
        })}
      </MapContainer>
    </div>
  );
}

export default MapView;
