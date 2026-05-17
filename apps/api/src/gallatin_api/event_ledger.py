from datetime import datetime, timezone
from typing import Literal, Protocol

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from pydantic import BaseModel, Field


class EventCoordinate(BaseModel):
    latitude: float
    longitude: float


class EventEvidence(BaseModel):
    kind: str
    reference: str


class AcceptedDomainEvent(BaseModel):
    event_id: str
    event_type: Literal["position_update"]
    subject_id: str
    source_callsign: str
    occurred_at: datetime
    accepted_at: datetime
    summary: str
    evidence: list[EventEvidence] = Field(default_factory=list)
    position: EventCoordinate


class EventLedgerStore(Protocol):
    def append(self, event: AcceptedDomainEvent) -> AcceptedDomainEvent: ...

    def list_events(self) -> list[AcceptedDomainEvent]: ...


class InMemoryEventLedgerStore:
    def __init__(self, events: list[AcceptedDomainEvent] | None = None) -> None:
        self.events = events or []

    def append(self, event: AcceptedDomainEvent) -> AcceptedDomainEvent:
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
                    Jsonb({"position": event.position.model_dump()}),
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
                    "position": row["payload"]["position"],
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
