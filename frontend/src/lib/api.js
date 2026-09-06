import axios from "axios";

const BASE = `${process.env.REACT_APP_BACKEND_URL}/api`;

const client = axios.create({ baseURL: BASE, timeout: 20000 });

export const WS_URL = `${process.env.REACT_APP_BACKEND_URL.replace(/^http/, "ws")}/api/ws`;

export const api = {
  snapshot: () => client.get("/snapshot").then((r) => r.data),
  dashboard: () => client.get("/dashboard/summary").then((r) => r.data),
  networkHealth: () => client.get("/network/health").then((r) => r.data),
  infrastructure: () => client.get("/infrastructure").then((r) => r.data),

  vehicles: () => client.get("/vehicles").then((r) => r.data),
  vehicle: (id) => client.get(`/vehicles/${id}`).then((r) => r.data),

  incidents: (params) => client.get("/incidents", { params }).then((r) => r.data),
  incident: (id) => client.get(`/incidents/${id}`).then((r) => r.data),
  hazards: () => client.get("/hazards").then((r) => r.data),
  roads: () => client.get("/roads/risk").then((r) => r.data),
  analytics: () => client.get("/analytics/summary").then((r) => r.data),

  fuse: (observations) => client.post("/evidence/fuse", observations).then((r) => r.data),

  routesMeta: () => client.get("/routes").then((r) => r.data),
  planRoute: (start, destination) =>
    client.post("/routes/plan", { start, destination }).then((r) => r.data),

  simStatus: () => client.get("/simulation/status").then((r) => r.data),
  simStart: (scenario, speed) =>
    client.post("/simulation/start", { scenario, speed }).then((r) => r.data),
  simPause: () => client.post("/simulation/pause").then((r) => r.data),
  simReset: () => client.post("/simulation/reset").then((r) => r.data),
  simSpeed: (speed) => client.post("/simulation/speed", { speed }).then((r) => r.data),
  inject: (payload) => client.post("/simulation/inject", payload).then((r) => r.data),

  respond: (incidentId, action, body = {}) =>
    client.post(`/response/${incidentId}/${action}`, body).then((r) => r.data),

  citizenReport: (body) => client.post("/citizen/report", body).then((r) => r.data),
};
