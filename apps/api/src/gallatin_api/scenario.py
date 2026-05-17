import json
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from gallatin_api.event_ledger import AcceptedDomainEvent, DeniedArea, SupplySignal


SupplyStatus = Literal["green", "amber", "red", "black"]


class Coordinate(BaseModel):
    latitude: float
    longitude: float


class Bounds(BaseModel):
    west: float
    south: float
    east: float
    north: float


class AreaOfOperations(BaseModel):
    id: str
    name: str
    corridor: str
    bounds: Bounds
    polygon: list[Coordinate]


class FriendlyCallsign(BaseModel):
    callsign: str
    role: str
    entity_id: str | None


class NamedLocation(BaseModel):
    id: str
    name: str
    role: str
    coordinate: Coordinate
    description: str


class InventoryProjection(BaseModel):
    source: str
    source_event_id: str | None
    baseline_days_of_supply: float | None
    projected_days_of_supply: float | None
    baseline_daily_burn_rate: float | None
    projected_daily_burn_rate: float | None
    burn_rate_change: str
    status_before: SupplyStatus
    status_after: SupplyStatus
    projected_black_time: str | None


class InventoryItem(BaseModel):
    tracked_supply: str
    class_of_supply: str
    quantity: float
    unit: str
    status: SupplyStatus
    days_of_supply: float | None
    projected_black_time: str | None
    projection: InventoryProjection | None = None


class SupportedUnit(BaseModel):
    id: str
    callsign: str
    radio_callsign: str
    display_name: str
    echelon: str
    location_id: str
    mission: str
    inventory: list[InventoryItem]


class SupplyLoadItem(BaseModel):
    tracked_supply: str
    class_of_supply: str
    quantity: float
    unit: str
    destination_unit_id: str


class SupplyConvoy(BaseModel):
    id: str
    callsign: str
    display_name: str
    location_id: str
    movement_status: str
    route_summary: str
    selected_route_variant_id: str | None = None
    selected_route_name: str | None = None
    route_location_ids: list[str]
    supply_load: list[SupplyLoadItem]


class RouteEvaluation(BaseModel):
    status: Literal["avoids_denied_areas", "conflicts_with_denied_area"]
    conflicting_denied_area_ids: list[str]


class GeneratedRouteVariant(BaseModel):
    route_id: str
    name: str
    summary: str
    source: str
    requested_avoid_polygon_count: int
    distance_km: float
    estimated_minutes: int
    geometry: list[Coordinate]
    evaluation: RouteEvaluation


class CoaLogpacItem(BaseModel):
    tracked_supply: str
    class_of_supply: str
    quantity: float
    unit: str
    destination_unit_id: str
    destination_callsign: str
    reason: str


class CoaMovement(BaseModel):
    movement_id: str
    movement_status: str
    route_variant_id: str | None
    route_name: str
    depart_at: str
    arrive_at: str
    logpac: list[CoaLogpacItem]
    assumptions: list[str]
    risks: list[str]
    projected_effect: str


class ExecutableCourseOfAction(BaseModel):
    coa_id: str
    name: str
    source_event_ids: list[str]
    rationale: str
    movements: list[CoaMovement]
    decision_status: Literal["proposed", "approved", "rejected"] = "proposed"
    decision_event_id: str | None = None


class ProjectionMetadata(BaseModel):
    source: str = "Scenario Seed"
    accepted_event_count: int = 0


class LogisticsPictureScenario(BaseModel):
    scenario_id: str
    name: str
    updated_at: str
    radio_channel: str
    agent_callsign: str
    logistics_watch_officer: str
    area_of_operations: AreaOfOperations
    friendly_callsigns: list[FriendlyCallsign]
    locations: list[NamedLocation]
    supported_units: list[SupportedUnit]
    supply_convoy: SupplyConvoy
    denied_areas: list[DeniedArea] = Field(default_factory=list)
    generated_routes: list[GeneratedRouteVariant] = Field(default_factory=list)
    executable_coas: list[ExecutableCourseOfAction] = Field(default_factory=list)
    projection: ProjectionMetadata = Field(default_factory=ProjectionMetadata)
    event_ledger: list[AcceptedDomainEvent] = Field(default_factory=list)


DEFAULT_SCENARIO_PATH = (
    Path(__file__).resolve().parents[4]
    / "data"
    / "scenarios"
    / "kaohsiung_tainan_logistics_picture.json"
)


@lru_cache(maxsize=1)
def load_kaohsiung_tainan_logistics_picture(
    path: Path = DEFAULT_SCENARIO_PATH,
) -> LogisticsPictureScenario:
    return LogisticsPictureScenario.model_validate(json.loads(path.read_text(encoding="utf-8")))


def project_logistics_picture(
    scenario: LogisticsPictureScenario,
    accepted_events: list[AcceptedDomainEvent],
) -> LogisticsPictureScenario:
    projected = scenario.model_copy(deep=True)
    initialize_inventory_projections(projected)

    for event in accepted_events:
        if event.event_type == "position_update":
            apply_position_update(projected, event)
        elif event.event_type == "denied_area_created":
            apply_denied_area(projected, event)
        elif event.event_type == "supply_signal":
            apply_supply_signal(projected, event)

    projected.projection = ProjectionMetadata(
        source="Event Ledger" if accepted_events else "Scenario Seed",
        accepted_event_count=len(accepted_events),
    )
    projected.generated_routes = generate_route_variants(projected)
    projected.executable_coas = generate_executable_coas(projected, accepted_events)
    apply_coa_decisions(projected, accepted_events)
    projected.event_ledger = accepted_events
    return projected


def initialize_inventory_projections(scenario: LogisticsPictureScenario) -> None:
    for unit in scenario.supported_units:
        for item in unit.inventory:
            baseline_daily_burn_rate = daily_burn_rate(
                quantity=item.quantity,
                days_of_supply=item.days_of_supply,
            )
            item.projection = InventoryProjection(
                source="Scenario Seed",
                source_event_id=None,
                baseline_days_of_supply=item.days_of_supply,
                projected_days_of_supply=item.days_of_supply,
                baseline_daily_burn_rate=baseline_daily_burn_rate,
                projected_daily_burn_rate=baseline_daily_burn_rate,
                burn_rate_change="baseline",
                status_before=item.status,
                status_after=item.status,
                projected_black_time=item.projected_black_time,
            )


def apply_position_update(
    scenario: LogisticsPictureScenario,
    event: AcceptedDomainEvent,
) -> None:
    if event.position is None:
        return

    location_id = projected_location_id_for_subject(scenario, event.subject_id)
    if location_id is None:
        return

    for location in scenario.locations:
        if location.id == location_id:
            location.coordinate = Coordinate(
                latitude=event.position.latitude,
                longitude=event.position.longitude,
            )
            location.description = "Projected from accepted Position Update."
            return


def apply_denied_area(
    scenario: LogisticsPictureScenario,
    event: AcceptedDomainEvent,
) -> None:
    if event.denied_area is None:
        return

    for denied_area in scenario.denied_areas:
        if denied_area.denied_area_id == event.denied_area.denied_area_id:
            return

    scenario.denied_areas.append(event.denied_area)


def apply_supply_signal(
    scenario: LogisticsPictureScenario,
    event: AcceptedDomainEvent,
) -> None:
    if event.supply_signal is None:
        return

    item = inventory_item_for_supply_signal(scenario, event.supply_signal)
    if item is None or item.projection is None:
        return

    signal = event.supply_signal
    baseline_days = item.projection.baseline_days_of_supply
    baseline_daily_burn_rate = item.projection.baseline_daily_burn_rate
    if baseline_days is None or baseline_daily_burn_rate is None:
        return

    current_quantity = signal.current_quantity
    raw_baseline_daily_burn_rate = item.quantity / baseline_days
    projected_daily_burn_rate = (
        raw_baseline_daily_burn_rate * signal.daily_burn_rate_multiplier
    )
    projected_days = current_quantity / projected_daily_burn_rate
    projected_status = status_for_days_of_supply(projected_days)
    projected_black_time = format_utc_timestamp(
        event.occurred_at + timedelta(days=projected_days)
    )

    item.quantity = current_quantity
    item.days_of_supply = round(projected_days, 1)
    item.projected_black_time = projected_black_time
    item.status = projected_status
    item.projection = InventoryProjection(
        source="Event Ledger",
        source_event_id=event.event_id,
        baseline_days_of_supply=baseline_days,
        projected_days_of_supply=round(projected_days, 1),
        baseline_daily_burn_rate=baseline_daily_burn_rate,
        projected_daily_burn_rate=round(projected_daily_burn_rate, 1),
        burn_rate_change=f"{signal.daily_burn_rate_multiplier:g}x baseline",
        status_before=item.projection.status_before,
        status_after=projected_status,
        projected_black_time=projected_black_time,
    )


def inventory_item_for_supply_signal(
    scenario: LogisticsPictureScenario,
    signal: SupplySignal,
) -> InventoryItem | None:
    for unit in scenario.supported_units:
        if unit.id != signal.unit_id:
            continue

        for item in unit.inventory:
            if item.tracked_supply == signal.tracked_supply:
                return item

    return None


def apply_coa_decisions(
    scenario: LogisticsPictureScenario,
    accepted_events: list[AcceptedDomainEvent],
) -> None:
    for event in accepted_events:
        if event.event_type == "coa_decision":
            apply_coa_decision(scenario, event)


def apply_coa_decision(
    scenario: LogisticsPictureScenario,
    event: AcceptedDomainEvent,
) -> None:
    decision = event.coa_decision
    if decision is None:
        return

    coa = executable_coa_by_id(scenario, decision.coa_id)
    if coa is None:
        return

    coa.decision_status = decision.decision
    coa.decision_event_id = event.event_id
    if decision.decision != "approved":
        return

    movement = selected_coa_movement(coa, decision.movement_id)
    if movement is None:
        return

    movement.movement_status = "Approved Movement Status"
    selected_route_variant_id = decision.selected_route_variant_id or movement.route_variant_id
    selected_route_name = decision.selected_route_name or movement.route_name
    scenario.supply_convoy.movement_status = "Approved Movement Status"
    scenario.supply_convoy.selected_route_variant_id = selected_route_variant_id
    scenario.supply_convoy.selected_route_name = selected_route_name
    scenario.supply_convoy.route_summary = selected_route_name
    scenario.supply_convoy.supply_load = [
        SupplyLoadItem(
            tracked_supply=item.tracked_supply,
            class_of_supply=item.class_of_supply,
            quantity=item.quantity,
            unit=item.unit,
            destination_unit_id=item.destination_unit_id,
        )
        for item in movement.logpac
    ]


def executable_coa_by_id(
    scenario: LogisticsPictureScenario,
    coa_id: str,
) -> ExecutableCourseOfAction | None:
    return next((coa for coa in scenario.executable_coas if coa.coa_id == coa_id), None)


def selected_coa_movement(
    coa: ExecutableCourseOfAction,
    movement_id: str | None,
) -> CoaMovement | None:
    if movement_id is None:
        return coa.movements[0] if coa.movements else None

    return next((movement for movement in coa.movements if movement.movement_id == movement_id), None)


def projected_location_id_for_subject(
    scenario: LogisticsPictureScenario,
    subject_id: str,
) -> str | None:
    if subject_id == scenario.supply_convoy.id:
        return scenario.supply_convoy.location_id

    for unit in scenario.supported_units:
        if subject_id == unit.id:
            return unit.location_id

    return None


def generate_route_variants(scenario: LogisticsPictureScenario) -> list[GeneratedRouteVariant]:
    if not scenario.denied_areas:
        return []

    locations = {location.id: location for location in scenario.locations}
    lsa = locations.get("lsa-south-dock")
    lrp = locations.get("lrp-bravo")
    checkpoint = locations.get("checkpoint-slate")
    if lsa is None or lrp is None or checkpoint is None:
        return []

    baseline_geometry = [lsa.coordinate, checkpoint.coordinate, lrp.coordinate]
    western_bypass_geometry = [
        lsa.coordinate,
        Coordinate(latitude=22.704, longitude=120.18),
        Coordinate(latitude=22.822, longitude=120.168),
        lrp.coordinate,
    ]

    return [
        route_variant(
            route_id="route-variant-route-dagger-baseline",
            name="Route Dagger Baseline",
            summary="Baseline Route Dagger from LSA South Dock to LRP Bravo through Checkpoint Slate.",
            distance_km=31.4,
            estimated_minutes=52,
            geometry=baseline_geometry,
            denied_areas=scenario.denied_areas,
        ),
        route_variant(
            route_id="route-variant-route-dagger-western-bypass",
            name="Route Dagger Western Bypass",
            summary="Western bypass from LSA South Dock to LRP Bravo avoiding Checkpoint Slate.",
            distance_km=36.8,
            estimated_minutes=64,
            geometry=western_bypass_geometry,
            denied_areas=scenario.denied_areas,
        ),
    ]


def route_variant(
    route_id: str,
    name: str,
    summary: str,
    distance_km: float,
    estimated_minutes: int,
    geometry: list[Coordinate],
    denied_areas: list[DeniedArea],
) -> GeneratedRouteVariant:
    conflicting_denied_area_ids = [
        denied_area.denied_area_id
        for denied_area in denied_areas
        if route_conflicts_with_denied_area(geometry, denied_area)
    ]
    status: Literal["avoids_denied_areas", "conflicts_with_denied_area"] = (
        "conflicts_with_denied_area"
        if conflicting_denied_area_ids
        else "avoids_denied_areas"
    )

    return GeneratedRouteVariant(
        route_id=route_id,
        name=name,
        summary=summary,
        source="Deterministic Local Route Generator",
        requested_avoid_polygon_count=len(denied_areas),
        distance_km=distance_km,
        estimated_minutes=estimated_minutes,
        geometry=geometry,
        evaluation=RouteEvaluation(
            status=status,
            conflicting_denied_area_ids=conflicting_denied_area_ids,
        ),
    )


def route_conflicts_with_denied_area(
    geometry: list[Coordinate],
    denied_area: DeniedArea,
) -> bool:
    return any(
        point_inside_denied_area(coordinate, denied_area)
        for coordinate in geometry
    )


def point_inside_denied_area(
    coordinate: Coordinate,
    denied_area: DeniedArea,
) -> bool:
    latitude_delta = coordinate.latitude - denied_area.center.latitude
    longitude_delta = coordinate.longitude - denied_area.center.longitude
    return (latitude_delta * latitude_delta + longitude_delta * longitude_delta) <= 0.0001


def generate_executable_coas(
    scenario: LogisticsPictureScenario,
    accepted_events: list[AcceptedDomainEvent],
) -> list[ExecutableCourseOfAction]:
    denied_area_event = next(
        (event for event in accepted_events if event.event_type == "denied_area_created"),
        None,
    )
    supply_signal_event = next(
        (
            event
            for event in accepted_events
            if event.event_type == "supply_signal" and event.supply_signal is not None
        ),
        None,
    )
    if denied_area_event is None and supply_signal_event is None:
        return []

    route = selected_route_variant(scenario)
    route_name = route.name if route is not None else "Route Dagger Baseline"
    route_variant_id = route.route_id if route is not None else "route-variant-route-dagger-baseline"
    estimated_minutes = route.estimated_minutes if route is not None else 52
    depart_at = parse_utc_timestamp("2026-05-17T04:00:00Z")
    arrive_at = format_utc_timestamp(depart_at + timedelta(minutes=estimated_minutes))
    logpac = coa_logpac_items(scenario, supply_signal_event)
    route_slug = "western-bypass" if route_name == "Route Dagger Western Bypass" else "baseline"

    if supply_signal_event is not None:
        coa_id = f"coa-route-dagger-{route_slug}-nomad-jp8-resupply"
        name = f"{route_name} / Nomad JP-8 Resupply"
        movement_id = f"mov-route-dagger-{route_slug}-nomad-jp8"
    else:
        coa_id = f"coa-route-dagger-{route_slug}"
        name = route_name
        movement_id = f"mov-route-dagger-{route_slug}"

    return [
        ExecutableCourseOfAction(
            coa_id=coa_id,
            name=name,
            source_event_ids=[
                event.event_id
                for event in accepted_events
                if event in [denied_area_event, supply_signal_event]
            ],
            rationale=coa_rationale(denied_area_event, supply_signal_event),
            movements=[
                CoaMovement(
                    movement_id=movement_id,
                    movement_status="Proposed Movement Status",
                    route_variant_id=route_variant_id,
                    route_name=route_name,
                    depart_at=format_utc_timestamp(depart_at),
                    arrive_at=arrive_at,
                    logpac=logpac,
                    assumptions=coa_assumptions(route_name),
                    risks=coa_risks(scenario, supply_signal_event),
                    projected_effect=coa_projected_effect(scenario, supply_signal_event),
                )
            ],
        )
    ]


def selected_route_variant(
    scenario: LogisticsPictureScenario,
) -> GeneratedRouteVariant | None:
    avoiding_routes = [
        route
        for route in scenario.generated_routes
        if route.evaluation.status == "avoids_denied_areas"
    ]
    if avoiding_routes:
        return avoiding_routes[0]

    return scenario.generated_routes[0] if scenario.generated_routes else None


def coa_logpac_items(
    scenario: LogisticsPictureScenario,
    supply_signal_event: AcceptedDomainEvent | None,
) -> list[CoaLogpacItem]:
    if supply_signal_event is None or supply_signal_event.supply_signal is None:
        return [
            CoaLogpacItem(
                tracked_supply=item.tracked_supply,
                class_of_supply=item.class_of_supply,
                quantity=item.quantity,
                unit=item.unit,
                destination_unit_id=item.destination_unit_id,
                destination_callsign=destination_callsign(scenario, item.destination_unit_id),
                reason="Maintain existing Mule 2 LOGPAC load.",
            )
            for item in scenario.supply_convoy.supply_load
        ]

    signal = supply_signal_event.supply_signal
    unit = supported_unit(scenario, signal.unit_id)
    item = inventory_item_for_supply_signal(scenario, signal)
    if unit is None or item is None:
        return []

    return [
        CoaLogpacItem(
            tracked_supply=signal.tracked_supply,
            class_of_supply=item.class_of_supply,
            quantity=480.0,
            unit=item.unit,
            destination_unit_id=unit.id,
            destination_callsign=unit.callsign,
            reason="Restore Nomad JP-8 above red after 3.2x burn-rate Supply Signal.",
        )
    ]


def coa_rationale(
    denied_area_event: AcceptedDomainEvent | None,
    supply_signal_event: AcceptedDomainEvent | None,
) -> str:
    if denied_area_event is not None and supply_signal_event is not None:
        return "Accepted Denied Area and Supply Signal require a bypass LOGPAC revision."

    if denied_area_event is not None:
        return "Accepted Denied Area requires Route Dagger bypass movement."

    return "Accepted Supply Signal requires LOGPAC revision."


def coa_assumptions(route_name: str) -> list[str]:
    return [
        "Mule 2 remains available for one LOGPAC movement.",
        f"{route_name} remains clear of accepted Denied Areas.",
    ]


def coa_risks(
    scenario: LogisticsPictureScenario,
    supply_signal_event: AcceptedDomainEvent | None,
) -> list[str]:
    risks = []
    if scenario.denied_areas:
        risks.append(
            "Route Dagger baseline conflicts with Route Dagger Checkpoint Slate Denied Area."
        )

    if supply_signal_event is not None and supply_signal_event.supply_signal is not None:
        item = inventory_item_for_supply_signal(scenario, supply_signal_event.supply_signal)
        if item is not None and item.projected_black_time is not None:
            risks.append(
                f"Nomad JP-8 reaches projected black time at {item.projected_black_time} without resupply."
            )

    return risks


def coa_projected_effect(
    scenario: LogisticsPictureScenario,
    supply_signal_event: AcceptedDomainEvent | None,
) -> str:
    if supply_signal_event is None or supply_signal_event.supply_signal is None:
        return "Mule 2 avoids the accepted Denied Area while preserving the existing LOGPAC."

    item = inventory_item_for_supply_signal(scenario, supply_signal_event.supply_signal)
    if item is None or item.projection is None or item.projection.projected_daily_burn_rate is None:
        return "Nomad JP-8 receives priority resupply before projected black time."

    replenished_days = round((item.quantity + 480.0) / item.projection.projected_daily_burn_rate, 1)
    replenished_status = status_for_days_of_supply(replenished_days)
    return (
        f"Nomad JP-8 improves from {item.days_of_supply} DOS {item.status} "
        f"to {replenished_days} DOS {replenished_status} before projected black time "
        f"{item.projected_black_time}."
    )


def supported_unit(
    scenario: LogisticsPictureScenario,
    unit_id: str,
) -> SupportedUnit | None:
    return next((unit for unit in scenario.supported_units if unit.id == unit_id), None)


def destination_callsign(
    scenario: LogisticsPictureScenario,
    unit_id: str,
) -> str:
    unit = supported_unit(scenario, unit_id)
    return unit.callsign if unit is not None else unit_id


def daily_burn_rate(
    quantity: float,
    days_of_supply: float | None,
) -> float | None:
    if days_of_supply is None or days_of_supply <= 0:
        return None

    return round(quantity / days_of_supply, 1)


def status_for_days_of_supply(days_of_supply: float) -> SupplyStatus:
    if days_of_supply <= 0:
        return "black"

    if days_of_supply < 1:
        return "red"

    if days_of_supply < 2:
        return "amber"

    return "green"


def format_utc_timestamp(value: datetime) -> str:
    return (
        value.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def parse_utc_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
