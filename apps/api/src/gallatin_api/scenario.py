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

    projected.event_ledger = accepted_events
    projected.projection = ProjectionMetadata(
        source="Event Ledger" if accepted_events else "Scenario Seed",
        accepted_event_count=len(accepted_events),
    )
    projected.generated_routes = generate_route_variants(projected)
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
