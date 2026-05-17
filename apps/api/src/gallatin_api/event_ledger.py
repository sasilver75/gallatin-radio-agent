from datetime import datetime, timezone
from typing import Literal, Protocol

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from pydantic import BaseModel, Field, model_validator


class EventCoordinate(BaseModel):
    latitude: float
    longitude: float


class EventEvidence(BaseModel):
    kind: str
    reference: str


class DeniedArea(BaseModel):
    denied_area_id: str
    name: str
    hazard_type: str
    route_name: str
    center: EventCoordinate
    radius_meters: int
    buffer_rule: str
    polygon: list[EventCoordinate]


class SupplySignal(BaseModel):
    unit_id: str
    tracked_supply: str
    current_quantity: float
    daily_burn_rate_multiplier: float
    reason: str


class AcceptedDomainEvent(BaseModel):
    event_id: str
    event_type: Literal["position_update", "denied_area_created", "supply_signal"]
    subject_id: str
    source_callsign: str
    occurred_at: datetime
    accepted_at: datetime
    summary: str
    evidence: list[EventEvidence] = Field(default_factory=list)
    position: EventCoordinate | None = None
    denied_area: DeniedArea | None = None
    supply_signal: SupplySignal | None = None

    @model_validator(mode="after")
    def require_event_payload(self) -> "AcceptedDomainEvent":
        if self.event_type == "position_update" and self.position is None:
            raise ValueError("position_update events require a position payload")

        if self.event_type == "denied_area_created" and self.denied_area is None:
            raise ValueError("denied_area_created events require a denied_area payload")

        if self.event_type == "supply_signal" and self.supply_signal is None:
            raise ValueError("supply_signal events require a supply_signal payload")

        return self


class EventLedgerStore(Protocol):
    def append(self, event: AcceptedDomainEvent) -> AcceptedDomainEvent: ...

    def list_events(self) -> list[AcceptedDomainEvent]: ...


class InMemoryEventLedgerStore:
    def __init__(self, events: list[AcceptedDomainEvent] | None = None) -> None:
        self.events = events or []

    def append(self, event: AcceptedDomainEvent) -> AcceptedDomainEvent:
        for existing_event in self.events:
            if existing_event.event_id == event.event_id:
                return existing_event

        self.events.append(event)
        return event

    def list_events(self) -> list[AcceptedDomainEvent]:
        return list(self.events)


class PostgresEventLedgerStore:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def append(self, event: AcceptedDomainEvent) -> AcceptedDomainEvent:
        self.ensure_schema()
        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                """
                insert into event_ledger (
                    event_id,
                    event_type,
                    subject_id,
                    source_callsign,
                    occurred_at,
                    accepted_at,
                    summary,
                    evidence,
                    payload
                )
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                on conflict (event_id) do nothing
                """,
                (
                    event.event_id,
                    event.event_type,
                    event.subject_id,
                    event.source_callsign,
                    event.occurred_at,
                    event.accepted_at,
                    event.summary,
                    Jsonb([evidence.model_dump() for evidence in event.evidence]),
                    Jsonb(accepted_event_payload(event)),
                ),
            )
        return event

    def list_events(self) -> list[AcceptedDomainEvent]:
        self.ensure_schema()
        with psycopg.connect(self.database_url, row_factory=dict_row) as connection:
            rows = connection.execute(
                """
                select
                    event_id,
                    event_type,
                    subject_id,
                    source_callsign,
                    occurred_at,
                    accepted_at,
                    summary,
                    evidence,
                    payload
                from event_ledger
                order by accepted_at asc, event_id asc
                """
            ).fetchall()

        return [
            AcceptedDomainEvent.model_validate(
                {
                    "event_id": row["event_id"],
                    "event_type": row["event_type"],
                    "subject_id": row["subject_id"],
                    "source_callsign": row["source_callsign"],
                    "occurred_at": normalize_utc(row["occurred_at"]),
                    "accepted_at": normalize_utc(row["accepted_at"]),
                    "summary": row["summary"],
                    "evidence": row["evidence"],
                    "position": row["payload"].get("position"),
                    "denied_area": row["payload"].get("denied_area"),
                    "supply_signal": row["payload"].get("supply_signal"),
                }
            )
            for row in rows
        ]

    def clear(self) -> None:
        self.ensure_schema()
        with psycopg.connect(self.database_url) as connection:
            connection.execute("delete from event_ledger")

    def ensure_schema(self) -> None:
        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                """
                create table if not exists event_ledger (
                    event_id text primary key,
                    event_type text not null,
                    subject_id text not null,
                    source_callsign text not null,
                    occurred_at timestamptz not null,
                    accepted_at timestamptz not null,
                    summary text not null,
                    evidence jsonb not null default '[]'::jsonb,
                    payload jsonb not null,
                    inserted_at timestamptz not null default now()
                )
                """
            )


def normalize_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def accepted_event_payload(event: AcceptedDomainEvent) -> dict[str, object]:
    payload: dict[str, object] = {}

    if event.position is not None:
        payload["position"] = event.position.model_dump()

    if event.denied_area is not None:
        payload["denied_area"] = event.denied_area.model_dump()

    if event.supply_signal is not None:
        payload["supply_signal"] = event.supply_signal.model_dump()

    return payload
