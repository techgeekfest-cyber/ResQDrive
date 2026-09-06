import React from "react";
import * as LucideIcons from "lucide-react";

// Renders a lucide-react icon by its string name (from constants metadata).
export function DynIcon({ name, ...props }) {
  const Cmp = LucideIcons[name] || LucideIcons.Circle;
  return <Cmp {...props} />;
}

export default DynIcon;
