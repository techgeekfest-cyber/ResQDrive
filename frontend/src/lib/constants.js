// Fixed semantic colors + hazard/verification metadata for ResQDrive.

export const STATUS_COLORS = {
  SAFE: { solid: "hsl(150 70% 45%)", bg: "hsl(152 55% 14%)", fg: "hsl(150 70% 82%)", border: "hsl(150 60% 30%)", icon: "ShieldCheck", label: "Safe" },
  CAUTION: { solid: "hsl(45 90% 55%)", bg: "hsl(42 70% 14%)", fg: "hsl(45 90% 82%)", border: "hsl(42 70% 34%)", icon: "AlertTriangle", label: "Caution" },
  UNSAFE: { solid: "hsl(8 85% 56%)", bg: "hsl(8 65% 15%)", fg: "hsl(8 90% 85%)", border: "hsl(8 65% 36%)", icon: "ShieldAlert", label: "Unsafe" },
  CRITICAL: { solid: "hsl(0 85% 52%)", bg: "hsl(0 70% 13%)", fg: "hsl(0 90% 88%)", border: "hsl(0 70% 34%)", icon: "Siren", label: "Critical" },
  UNKNOWN: { solid: "hsl(215 10% 55%)", bg: "hsl(220 10% 16%)", fg: "hsl(215 12% 78%)", border: "hsl(220 10% 30%)", icon: "HelpCircle", label: "Unknown" },
};

export const VERIFICATION_META = {
  UNVERIFIED: { color: "hsl(215 12% 62%)", bg: "hsl(220 10% 16%)", icon: "CircleDashed", label: "Unverified" },
  CORROBORATED: { color: "hsl(190 85% 52%)", bg: "hsl(190 60% 12%)", icon: "Link2", label: "Corroborated" },
  VERIFIED: { color: "hsl(150 70% 50%)", bg: "hsl(152 55% 12%)", icon: "BadgeCheck", label: "Verified" },
  CONFLICTING: { color: "hsl(38 92% 58%)", bg: "hsl(38 70% 12%)", icon: "GitCompareArrows", label: "Conflicting" },
  STALE: { color: "hsl(215 10% 56%)", bg: "hsl(220 10% 15%)", icon: "Clock", label: "Stale" },
};

export const HAZARD_META = {
  FLOOD: { label: "Flood Water", icon: "Waves" },
  WATERLOGGING: { label: "Waterlogging", icon: "Droplets" },
  LANDSLIDE: { label: "Landslide", icon: "Mountain" },
  DEBRIS: { label: "Road Debris", icon: "Boxes" },
  FALLEN_TREE: { label: "Fallen Tree", icon: "Trees" },
  POTHOLE: { label: "Pothole Cluster", icon: "CircleDot" },
  ROAD_DAMAGE: { label: "Damaged Road", icon: "Hammer" },
  ACCIDENT: { label: "Vehicle Accident", icon: "CarFront" },
  ROAD_BLOCKAGE: { label: "Road Blockage", icon: "Ban" },
  CONSTRUCTION: { label: "Construction", icon: "TrafficCone" },
  CLEAR: { label: "Road Clear", icon: "CircleCheck" },
};

export const PRIORITY_META = {
  P1: { label: "P1 · Critical", color: "hsl(0 85% 52%)" },
  P2: { label: "P2 · High", color: "hsl(8 85% 56%)" },
  P3: { label: "P3 · Moderate", color: "hsl(45 90% 55%)" },
  P4: { label: "P4 · Low", color: "hsl(215 12% 60%)" },
};

export const SCENARIOS = [
  { value: "CYCLONE_FLOOD", label: "Cyclone + Urban Flood" },
  { value: "FLOOD", label: "Flood" },
  { value: "CYCLONE", label: "Cyclone" },
  { value: "LANDSLIDE", label: "Landslide" },
  { value: "URBAN_WATERLOGGING", label: "Urban Waterlogging" },
  { value: "ROAD_BLOCKAGE", label: "Road Blockage" },
  { value: "MIXED", label: "Mixed Disaster" },
];

export const INJECT_TYPES = [
  { value: "FLOOD", label: "Flood", icon: "Waves" },
  { value: "LANDSLIDE", label: "Landslide", icon: "Mountain" },
  { value: "ROAD_BLOCKAGE", label: "Road Blockage", icon: "Ban" },
  { value: "FALLEN_TREE", label: "Fallen Tree", icon: "Trees" },
  { value: "POTHOLE", label: "Pothole", icon: "CircleDot" },
  { value: "CONFLICTING", label: "Conflicting Evidence", icon: "GitCompareArrows" },
  { value: "ROAD_CLEAR", label: "Road Clear", icon: "CircleCheck" },
];

export const ROLES = ["CITIZEN", "OPERATOR", "AUTHORITY", "ADMIN"];

export const NAV_ITEMS = [
  { to: "/command", label: "Overview", icon: "LayoutDashboard" },
  { to: "/map", label: "Live Map", icon: "Map" },
  { to: "/vehicles", label: "Vehicles", icon: "Car" },
  { to: "/hazards", label: "Hazards", icon: "TriangleAlert" },
  { to: "/routes", label: "Routes", icon: "Route" },
  { to: "/response", label: "Response", icon: "Siren" },
  { to: "/simulation", label: "Simulation", icon: "FlaskConical" },
  { to: "/system", label: "System", icon: "Network" },
];

export const MAP_CENTER = [17.412, 78.472];
export const MAP_ZOOM = 12;
