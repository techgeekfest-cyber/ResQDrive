import React, {
  createContext,
  useContext,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import { api, WS_URL } from "@/lib/api";

const AppContext = createContext(null);

const EMPTY = {
  sim: { status: "STOPPED", scenario: "CYCLONE_FLOOD", speed: 2, tick: 0, sim_time: null },
  summary: {},
  vehicles: [],
  incidents: [],
  roads: [],
  infrastructure: [],
  events: [],
  demo_route: null,
};

export function AppProvider({ children }) {
  const [snapshot, setSnapshot] = useState(EMPTY);
  const [connection, setConnection] = useState("connecting");
  const [role, setRoleState] = useState(
    () => localStorage.getItem("resq_role") || "OPERATOR",
  );
  const wsRef = useRef(null);
  const retryRef = useRef(null);
  const pingRef = useRef(null);

  const setRole = useCallback((r) => {
    setRoleState(r);
    localStorage.setItem("resq_role", r);
  }, []);

  const applyState = useCallback((data) => {
    setSnapshot((prev) => ({ ...prev, ...data }));
  }, []);

  // Initial REST load (fallback in case WS is slow).
  useEffect(() => {
    api.snapshot().then(applyState).catch(() => {});
  }, [applyState]);

  // WebSocket live connection with auto-reconnect.
  useEffect(() => {
    let closed = false;

    const connect = () => {
      try {
        const ws = new WebSocket(WS_URL);
        wsRef.current = ws;
        setConnection((c) => (c === "connected" ? c : "connecting"));

        ws.onopen = () => {
          setConnection("connected");
          clearInterval(pingRef.current);
          pingRef.current = setInterval(() => {
            try { ws.send("ping"); } catch { /* noop */ }
          }, 25000);
        };
        ws.onmessage = (ev) => {
          try {
            const msg = JSON.parse(ev.data);
            if (msg && msg.type === "state") applyState(msg);
          } catch { /* noop */ }
        };
        ws.onclose = () => {
          clearInterval(pingRef.current);
          if (closed) return;
          setConnection("reconnecting");
          retryRef.current = setTimeout(connect, 2500);
        };
        ws.onerror = () => { try { ws.close(); } catch { /* noop */ } };
      } catch {
        setConnection("reconnecting");
        retryRef.current = setTimeout(connect, 2500);
      }
    };

    connect();
    return () => {
      closed = true;
      clearTimeout(retryRef.current);
      clearInterval(pingRef.current);
      try { wsRef.current && wsRef.current.close(); } catch { /* noop */ }
    };
  }, [applyState]);

  // Simulation + action helpers (backend broadcasts updates over WS).
  const actions = {
    start: (scenario, speed) => api.simStart(scenario, speed),
    pause: () => api.simPause(),
    reset: () => api.simReset(),
    setSpeed: (s) => api.simSpeed(s),
    inject: (payload) => api.inject(payload),
    respond: (id, action, body) => api.respond(id, action, body),
  };

  const value = {
    ...snapshot,
    connection,
    role,
    setRole,
    actions,
    refresh: () => api.snapshot().then(applyState).catch(() => {}),
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used within AppProvider");
  return ctx;
}
