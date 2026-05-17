import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from gallatin_api.event_ledger import AcceptedDomainEvent


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


class InventoryItem(BaseModel):
    tracked_supply: str
    class_of_supply: str
    quantity: float
    unit: str
    status: SupplyStatus
    days_of_supply: float | None
    projected_black_time: str | None


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

    for event in accepted_events:
        if event.event_type == "position_update":
            apply_position_update(projected, event)

    projected.event_ledger = accepted_events
    projected.projection = ProjectionMetadata(
        source="Event Ledger" if accepted_events else "Scenario Seed",
        accepted_event_count=len(accepted_events),
    )
    return projected


def apply_position_update(
    scenario: LogisticsPictureScenario,
    event: AcceptedDomainEvent,
) -> None:
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
