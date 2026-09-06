import React from "react";
import { Car, MapPin } from "lucide-react";

// Text + icon brand treatment (vehicle + location pin + network node).
export function ResQDriveLogo({ compact = false, className = "" }) {
  return (
    <div className={`flex items-center gap-2.5 ${className}`} data-testid="app-logo">
      <div className="relative grid h-9 w-9 place-items-center rounded-lg border border-[hsl(190_60%_30%)] bg-[hsl(190_70%_10%)]">
        <Car className="h-4 w-4 text-[hsl(190_85%_55%)]" strokeWidth={2.2} />
        <MapPin className="absolute -right-1 -top-1 h-3.5 w-3.5 text-[hsl(150_70%_50%)]" strokeWidth={2.6} />
        <span className="absolute -bottom-1 -left-1 h-2 w-2 rounded-full bg-[hsl(45_90%_55%)] ring-2 ring-[hsl(220_18%_6%)]" />
      </div>
      {!compact && (
        <div className="leading-tight">
          <div className="text-[15px] font-semibold tracking-tight text-foreground">
            ResQ<span className="text-[hsl(190_85%_55%)]">Drive</span>
          </div>
          <div className="hidden text-[10px] uppercase tracking-wider text-muted-foreground sm:block">
            Disaster Intelligence Network
          </div>
        </div>
      )}
    </div>
  );
}

export default ResQDriveLogo;
