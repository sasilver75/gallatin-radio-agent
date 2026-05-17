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

export type InventoryProjection = {
  source: string;
  source_event_id: string | null;
  baseline_days_of_supply: number | null;
  projected_days_of_supply: number | null;
  baseline_daily_burn_rate: number | null;
  projected_daily_burn_rate: number | null;
  burn_rate_change: string;
  status_before: SupplyStatus;
  status_after: SupplyStatus;
  projected_black_time: string | null;
};

export type InventoryItem = {
  tracked_supply: string;
  class_of_supply: string;
  quantity: number;
  unit: string;
  status: SupplyStatus;
  days_of_supply: number | null;
  projected_black_time: string | null;
  projection: InventoryProjection | null;
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
  selected_route_variant_id: string | null;
  selected_route_name: string | null;
  route_location_ids: string[];
  supply_load: SupplyLoadItem[];
};

export type DeniedArea = {
  denied_area_id: string;
  name: string;
  hazard_type: string;
  route_name: string;
  center: Coordinate;
  radius_meters: number;
  buffer_rule: string;
  polygon: Coordinate[];
};

export type RouteEvaluation = {
  status: "avoids_denied_areas" | "conflicts_with_denied_area";
  conflicting_denied_area_ids: string[];
};

export type GeneratedRouteVariant = {
  route_id: string;
  name: string;
  summary: string;
  source: string;
  requested_avoid_polygon_count: number;
  distance_km: number;
  estimated_minutes: number;
  geometry: Coordinate[];
  evaluation: RouteEvaluation;
};

export type CoaLogpacItem = {
  tracked_supply: string;
  class_of_supply: string;
  quantity: number;
  unit: string;
  destination_unit_id: string;
  destination_callsign: string;
  reason: string;
};

export type CoaMovement = {
  movement_id: string;
  movement_status: string;
  route_variant_id: string | null;
  route_name: string;
  depart_at: string;
  arrive_at: string;
  logpac: CoaLogpacItem[];
  assumptions: string[];
  risks: string[];
  projected_effect: string;
};

export type ExecutableCourseOfAction = {
  coa_id: string;
  name: string;
  source_event_ids: string[];
  rationale: string;
  movements: CoaMovement[];
  decision_status: "proposed" | "approved" | "rejected";
  decision_event_id: string | null;
};

export type EventEvidence = {
  kind: string;
  reference: string;
};

export type SupplySignal = {
  unit_id: string;
  tracked_supply: string;
  current_quantity: number;
  daily_burn_rate_multiplier: number;
  reason: string;
};

export type CoaDecision = {
  coa_id: string;
  decision: "approved" | "rejected";
  decided_by: string;
  movement_id?: string;
  selected_route_variant_id?: string;
  selected_route_name?: string;
};

export type AcceptedDomainEvent = {
  event_id: string;
  event_type: "position_update" | "denied_area_created" | "supply_signal" | "coa_decision";
  subject_id: string;
  source_callsign: string;
  occurred_at: string;
  accepted_at: string;
  summary: string;
  evidence: EventEvidence[];
  position?: Coordinate;
  denied_area?: DeniedArea;
  supply_signal?: SupplySignal;
  coa_decision?: CoaDecision;
};

export type ProjectionMetadata = {
  source: string;
  accepted_event_count: number;
};

export type AudioMetadata = {
  filename: string;
  content_type: string;
  duration_seconds: number;
  fixture_uri: string;
};

export type PrerecordedRadioClip = {
  clip_id: string;
  title: string;
  radio_channel: string;
  source_callsign: string;
  recorded_at: string;
  audio: AudioMetadata;
};

export type TranscriptionMetadata = {
  pipeline: string;
  fixture_id: string;
};

export type AutoAcceptedRadioInterpretation = {
  interpretation_id: string;
  kind: "auto_accepted";
  domain_event_id: string;
  summary: string;
  extracted_callsigns: string[];
};

export type ProposedHazardMeaning = {
  hazard_type: string;
  route_name: string;
  location_name: string;
  center: Coordinate;
  buffer_radius_meters: number;
  buffer_rule: string;
};

export type ReviewRequiredRadioInterpretation = {
  interpretation_id: string;
  kind: "review_required";
  domain_event_id: string | null;
  status: "pending" | "accepted" | "rejected";
  summary: string;
  extracted_callsigns: string[];
  proposed_hazard: ProposedHazardMeaning;
};

export type RadioInterpretation =
  | AutoAcceptedRadioInterpretation
  | ReviewRequiredRadioInterpretation;

export type RadioTransmission = {
  transmission_id: string;
  clip_id: string;
  radio_channel: string;
  source_callsign: string;
  recorded_at: string;
  audio: AudioMetadata;
  transcript: string;
  transcription: TranscriptionMetadata;
  interpretations: RadioInterpretation[];
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
  denied_areas: DeniedArea[];
  generated_routes: GeneratedRouteVariant[];
  executable_coas: ExecutableCourseOfAction[];
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

export async function fetchPrerecordedRadioClips(): Promise<PrerecordedRadioClip[]> {
  const response = await fetch(`${API_BASE_URL}/radio/prerecorded-clips`);
  const body = (await response.json()) as PrerecordedRadioClip[];

  if (!response.ok) {
    throw new Error(`Prerecorded Radio Clip fetch failed with HTTP ${response.status}`);
  }

  return body;
}

export async function transmitPrerecordedRadioClip(clipId: string): Promise<RadioTransmission> {
  const response = await fetch(`${API_BASE_URL}/radio/transmissions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ clip_id: clipId })
  });
  const body = (await response.json()) as RadioTransmission;

  if (!response.ok) {
    throw new Error(`Tactical Radio Audio transcription failed with HTTP ${response.status}`);
  }

  return body;
}

export async function acceptProposedInterpretation(
  interpretationId: string
): Promise<AcceptedDomainEvent> {
  const response = await fetch(`${API_BASE_URL}/interpretations/proposed/${interpretationId}/accept`, {
    method: "POST"
  });
  const body = (await response.json()) as AcceptedDomainEvent;

  if (!response.ok) {
    throw new Error(`Proposed Interpretation accept failed with HTTP ${response.status}`);
  }

  return body;
}

export async function rejectProposedInterpretation(
  interpretationId: string
): Promise<ReviewRequiredRadioInterpretation> {
  const response = await fetch(`${API_BASE_URL}/interpretations/proposed/${interpretationId}/reject`, {
    method: "POST"
  });
  const body = (await response.json()) as ReviewRequiredRadioInterpretation;

  if (!response.ok) {
    throw new Error(`Proposed Interpretation reject failed with HTTP ${response.status}`);
  }

  return body;
}

export async function approveExecutableCoa(coaId: string): Promise<AcceptedDomainEvent> {
  const response = await fetch(`${API_BASE_URL}/coas/${coaId}/approve`, {
    method: "POST"
  });
  const body = (await response.json()) as AcceptedDomainEvent;

  if (!response.ok) {
    throw new Error(`Executable COA approval failed with HTTP ${response.status}`);
  }

  return body;
}

export async function rejectExecutableCoa(coaId: string): Promise<AcceptedDomainEvent> {
  const response = await fetch(`${API_BASE_URL}/coas/${coaId}/reject`, {
    method: "POST"
  });
  const body = (await response.json()) as AcceptedDomainEvent;

  if (!response.ok) {
    throw new Error(`Executable COA rejection failed with HTTP ${response.status}`);
  }

  return body;
}
