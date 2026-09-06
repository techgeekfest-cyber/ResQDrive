import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "@/App.css";
import { AppProvider } from "@/context/AppContext";
import { AppShell } from "@/components/AppShell";
import { Toaster } from "@/components/ui/sonner";

import Landing from "@/pages/Landing";
import CommandCenter from "@/pages/CommandCenter";
import LiveMap from "@/pages/LiveMap";
import Vehicles from "@/pages/Vehicles";
import Hazards from "@/pages/Hazards";
import RoutesPage from "@/pages/RoutesPage";
import Response from "@/pages/Response";
import Simulation from "@/pages/Simulation";
import System from "@/pages/System";
import Technology from "@/pages/Technology";
import About from "@/pages/About";
import Citizen from "@/pages/Citizen";

function App() {
  return (
    <div className="App">
      <AppProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route element={<AppShell />}>
              <Route path="/command" element={<CommandCenter />} />
              <Route path="/vehicles" element={<Vehicles />} />
              <Route path="/hazards" element={<Hazards />} />
              <Route path="/routes" element={<RoutesPage />} />
              <Route path="/response" element={<Response />} />
              <Route path="/simulation" element={<Simulation />} />
              <Route path="/system" element={<System />} />
              <Route path="/technology" element={<Technology />} />
              <Route path="/about" element={<About />} />
              <Route path="/citizen" element={<Citizen />} />
            </Route>
            <Route element={<AppShell noFooter />}>
              <Route path="/map" element={<LiveMap />} />
            </Route>
          </Routes>
        </BrowserRouter>
        <Toaster position="top-right" theme="dark" richColors closeButton />
      </AppProvider>
    </div>
  );
}

export default App;
