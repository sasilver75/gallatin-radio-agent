export type DependencyStatus = {
  name: string;
  status: "ready" | "unavailable";
  details: string;
};

export type ReadinessResponse = {
  service: string;
  status: "ready" | "unavailable";
  dependencies: DependencyStatus[];
};

export type Coordinate = {
  latitude: number;
  longitude: number;
};

export type Bounds = {
  west: number;
  south: number;
  east: number;
  north: number;
};

export type AreaOfOperations = {
  id: string;
  name: string;
  corridor: string;
  bounds: Bounds;
  polygon: Coordinate[];
};

export type FriendlyCallsign = {
  callsign: string;
  role: string;
  entity_id: string | null;
};

export type NamedLocation = {
  id: string;
  name: string;
  role: string;
  coordinate: Coordinate;
  description: string;
};

export type SupplyStatus = "green" | "amber" | "red" | "black";

export type InventoryItem = {
  tracked_supply: string;
  class_of_supply: string;
  quantity: number;
  unit: string;
  status: SupplyStatus;
  days_of_supply: number | null;
  projected_black_time: string | null;
};

export type SupportedUnit = {
  id: string;
  callsign: string;
  radio_callsign: string;
  display_name: string;
  echelon: string;
  location_id: string;
  mission: string;
  inventory: InventoryItem[];
};

export type SupplyLoadItem = {
  tracked_supply: string;
  class_of_supply: string;
  quantity: number;
  unit: string;
  destination_unit_id: string;
};

export type SupplyConvoy = {
  id: string;
  callsign: string;
  display_name: string;
  location_id: string;
  movement_status: string;
  route_summary: string;
  route_location_ids: string[];
  supply_load: SupplyLoadItem[];
};

export type EventEvidence = {
  kind: string;
  reference: string;
};

export type AcceptedDomainEvent = {
  event_id: string;
  event_type: "position_update";
  subject_id: string;
  source_callsign: string;
  occurred_at: string;
  accepted_at: string;
  summary: string;
  evidence: EventEvidence[];
  position: Coordinate;
};

export type ProjectionMetadata = {
  source: string;
  accepted_event_count: number;
};

export type LogisticsPictureScenario = {
  scenario_id: string;
  name: string;
  updated_at: string;
  radio_channel: string;
  agent_callsign: string;
  logistics_watch_officer: string;
  area_of_operations: AreaOfOperations;
  friendly_callsigns: FriendlyCallsign[];
  locations: NamedLocation[];
  supported_units: SupportedUnit[];
  supply_convoy: SupplyConvoy;
  projection: ProjectionMetadata;
  event_ledger: AcceptedDomainEvent[];
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function fetchReadiness(): Promise<ReadinessResponse> {
  const response = await fetch(`${API_BASE_URL}/readyz`);
  const body = (await response.json()) as ReadinessResponse;

  if (!response.ok && body.status !== "unavailable") {
    throw new Error(`Readiness check failed with HTTP ${response.status}`);
  }

  return body;
}

export async function fetchLogisticsPicture(): Promise<LogisticsPictureScenario> {
  const response = await fetch(`${API_BASE_URL}/scenarios/kaohsiung-tainan/logistics-picture`);
  const body = (await response.json()) as LogisticsPictureScenario;

  if (!response.ok) {
    throw new Error(`Logistics Picture fetch failed with HTTP ${response.status}`);
  }

  return body;
}
