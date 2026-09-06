import React from "react";
import { VERIFICATION_META } from "@/lib/constants";
import { DynIcon } from "@/components/DynIcon";

// UNVERIFIED / CORROBORATED / VERIFIED / CONFLICTING / STALE badge.
export function VerificationBadge({ state = "UNVERIFIED", className = "" }) {
  const m = VERIFICATION_META[state] || VERIFICATION_META.UNVERIFIED;
  return (
    <span
      data-testid="verification-badge"
      className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[11px] font-semibold ${className}`}
      style={{ background: m.bg, color: m.color, borderColor: m.color + "55" }}
    >
      <DynIcon name={m.icon} className="h-3.5 w-3.5" />
      <span className="sr-only">Verification status: </span>
      {m.label}
    </span>
  );
}

export default VerificationBadge;
