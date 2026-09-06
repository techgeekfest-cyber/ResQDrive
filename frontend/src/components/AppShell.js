import React from "react";
import { Outlet } from "react-router-dom";
import { TopBar } from "@/components/TopBar";
import { Footer } from "@/components/Footer";

export function AppShell({ noFooter = false }) {
  return (
    <div className="flex min-h-screen flex-col">
      <TopBar />
      <main className="flex-1">
        <Outlet />
      </main>
      {!noFooter && <Footer />}
    </div>
  );
}

export default AppShell;
