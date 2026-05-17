import json
import math
import re
from collections.abc import Callable
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal, Protocol, TypeAlias

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from pydantic import BaseModel, Field

from gallatin_api.event_ledger import (
    AcceptedDomainEvent,
    DeniedArea,
    EventCoordinate,
    EventEvidence,
    SupplySignal,
)


class AudioMetadata(BaseModel):
    filename: str
    content_type: str
    duration_seconds: float
    fixture_uri: str


class TranscriptionFixture(BaseModel):
    fixture_id: str
    transcript: str


class PrerecordedRadioClip(BaseModel):
    clip_id: str
    title: str
    radio_channel: str
    source_callsign: str
    recorded_at: str
    audio: AudioMetadata
    transcription_fixture: TranscriptionFixture


class PublicPrerecordedRadioClip(BaseModel):
    clip_id: str
    title: str
    radio_channel: str
    source_callsign: str
    recorded_at: str
    audio: AudioMetadata


class RadioTransmissionRequest(BaseModel):
    clip_id: str


class TranscriptionMetadata(BaseModel):
    pipeline: str
    fixture_id: str


class AutoAcceptedRadioInterpretation(BaseModel):
    interpretation_id: str
    kind: Literal["auto_accepted"]
    domain_event_id: str
    summary: str
    extracted_callsigns: list[str]


class ProposedHazardMeaning(BaseModel):
    hazard_type: str
    route_name: str
    location_name: str
    center: EventCoordinate
    buffer_radius_meters: int
    buffer_rule: str


class ReviewRequiredRadioInterpretation(BaseModel):
    interpretation_id: str
    kind: Literal["review_required"]
    domain_event_id: str | None = None
    status: Literal["pending", "accepted", "rejected"]
    summary: str
    extracted_callsigns: list[str]
    proposed_hazard: ProposedHazardMeaning


RadioInterpretation: TypeAlias = Annotated[
    AutoAcceptedRadioInterpretation | ReviewRequiredRadioInterpretation,
    Field(discriminator="kind"),
]


class RadioTransmission(BaseModel):
    transmission_id: str
    clip_id: str
    radio_channel: str
    source_callsign: str
    recorded_at: str
    audio: AudioMetadata
    transcript: str
    transcription: TranscriptionMetadata
    interpretations: list[RadioInterpretation] = Field(default_factory=list)


class RadioInterpretationResult(BaseModel):
    interpretations: list[RadioInterpretation]
    accepted_events: list[AcceptedDomainEvent]


class TranscriptionPipeline(Protocol):
    def list_prerecorded_clips(self) -> list[PublicPrerecordedRadioClip]: ...

    def transcribe_prerecorded_clip(self, clip_id: str) -> RadioTransmission: ...


class ProposedInterpretationStore(Protocol):
    def upsert(
        self,
        interpretation: ReviewRequiredRadioInterpretation,
    ) -> ReviewRequiredRadioInterpretation: ...

    def get(self, interpretation_id: str) -> ReviewRequiredRadioInterpretation: ...

    def mark_accepted(
        self,
        interpretation_id: str,
        domain_event_id: str,
    ) -> ReviewRequiredRadioInterpretation: ...

    def mark_rejected(self, interpretation_id: str) -> ReviewRequiredRadioInterpretation: ...


class PrerecordedRadioClipNotFound(Exception):
    pass


class ProposedInterpretationNotFound(Exception):
    pass


class InMemoryProposedInterpretationStore:
    def __init__(
        self,
        interpretations: list[ReviewRequiredRadioInterpretation] | None = None,
    ) -> None:
        self.interpretations = {
            interpretation.interpretation_id: interpretation
            for interpretation in interpretations or []
        }

    def upsert(
        self,
        interpretation: ReviewRequiredRadioInterpretation,
    ) -> ReviewRequiredRadioInterpretation:
        existing = self.interpretations.get(interpretation.interpretation_id)
        if existing is not None:
            return existing

        self.interpretations[interpretation.interpretation_id] = interpretation
        return interpretation

    def get(self, interpretation_id: str) -> ReviewRequiredRadioInterpretation:
        interpretation = self.interpretations.get(interpretation_id)
        if interpretation is None:
            raise ProposedInterpretationNotFound(interpretation_id)
        return interpretation

    def mark_accepted(
        self,
        interpretation_id: str,
        domain_event_id: str,
    ) -> ReviewRequiredRadioInterpretation:
        interpretation = self.get(interpretation_id).model_copy(
            update={
                "domain_event_id": domain_event_id,
                "status": "accepted",
            }
        )
        self.interpretations[interpretation_id] = interpretation
        return interpretation

    def mark_rejected(self, interpretation_id: str) -> ReviewRequiredRadioInterpretation:
        interpretation = self.get(interpretation_id).model_copy(update={"status": "rejected"})
        self.interpretations[interpretation_id] = interpretation
        return interpretation


class PostgresProposedInterpretationStore:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def upsert(
        self,
        interpretation: ReviewRequiredRadioInterpretation,
    ) -> ReviewRequiredRadioInterpretation:
        existing = self.find(interpretation.interpretation_id)
        if existing is not None:
            return existing

        self.ensure_schema()
        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                """
                insert into proposed_interpretations (
                    interpretation_id,
                    status,
                    payload
                )
                values (%s, %s, %s)
                on conflict (interpretation_id) do nothing
                """,
                (
                    interpretation.interpretation_id,
                    interpretation.status,
                    Jsonb(interpretation.model_dump(mode="json")),
                ),
            )
        return interpretation

    def get(self, interpretation_id: str) -> ReviewRequiredRadioInterpretation:
        interpretation = self.find(interpretation_id)
        if interpretation is None:
            raise ProposedInterpretationNotFound(interpretation_id)
        return interpretation

    def mark_accepted(
        self,
        interpretation_id: str,
        domain_event_id: str,
    ) -> ReviewRequiredRadioInterpretation:
        interpretation = self.get(interpretation_id).model_copy(
            update={
                "domain_event_id": domain_event_id,
                "status": "accepted",
            }
        )
        self.save(interpretation)
        return interpretation

    def mark_rejected(self, interpretation_id: str) -> ReviewRequiredRadioInterpretation:
        interpretation = self.get(interpretation_id).model_copy(update={"status": "rejected"})
        self.save(interpretation)
        return interpretation

    def find(self, interpretation_id: str) -> ReviewRequiredRadioInterpretation | None:
        self.ensure_schema()
        with psycopg.connect(self.database_url, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                select payload
                from proposed_interpretations
                where interpretation_id = %s
                """,
                (interpretation_id,),
            ).fetchone()

        if row is None:
            return None

        return ReviewRequiredRadioInterpretation.model_validate(row["payload"])

    def save(self, interpretation: ReviewRequiredRadioInterpretation) -> None:
        self.ensure_schema()
        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                """
                update proposed_interpretations
                set status = %s,
                    payload = %s,
                    updated_at = now()
                where interpretation_id = %s
                """,
                (
                    interpretation.status,
                    Jsonb(interpretation.model_dump(mode="json")),
                    interpretation.interpretation_id,
                ),
            )

    def ensure_schema(self) -> None:
        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                """
                create table if not exists proposed_interpretations (
                    interpretation_id text primary key,
                    status text not null,
                    payload jsonb not null,
                    created_at timestamptz not null default now(),
                    updated_at timestamptz not null default now()
                )
                """
            )


CALLSIGN_PATTERN = re.compile(r"\b[A-Z][a-z]+ \d\b")
POSITION_UPDATE_PATTERN = re.compile(
    r"\b(?P<callsign>[A-Z][a-z]+ \d) passing (?P<location>Checkpoint Slate) now\b"
)
KNOWN_POSITION_UPDATE_LOCATIONS = {
    "Checkpoint Slate": EventCoordinate(latitude=22.812, longitude=120.318)
}
KNOWN_HAZARD_LOCATIONS = {
    "Checkpoint Slate": EventCoordinate(latitude=22.812, longitude=120.318)
}


def interpret_radio_transmission(transmission: RadioTransmission) -> RadioInterpretationResult:
    position_update = POSITION_UPDATE_PATTERN.search(transmission.transcript)
    if transmission.clip_id == "lognet-1-mule-2-checkpoint-slate" and position_update:
        source_callsign = position_update.group("callsign")
        location_name = position_update.group("location")
        position = KNOWN_POSITION_UPDATE_LOCATIONS[location_name]
        event_id = "evt-rt-lognet-1-mule-2-checkpoint-slate-position-update"
        summary = f"{source_callsign} reports passing {location_name}."
        interpretation = AutoAcceptedRadioInterpretation(
            interpretation_id="interp-rt-lognet-1-mule-2-checkpoint-slate-position-update",
            kind="auto_accepted",
            domain_event_id=event_id,
            summary=summary,
            extracted_callsigns=extract_callsigns(transmission.transcript),
        )
        accepted_at = parse_fixture_timestamp(transmission.recorded_at)
        event = AcceptedDomainEvent(
            event_id=event_id,
            event_type="position_update",
            subject_id="mule-2",
            source_callsign=source_callsign,
            occurred_at=accepted_at,
            accepted_at=accepted_at,
            summary=summary,
            evidence=[
                EventEvidence(
                    kind="radio_transmission",
                    reference=transmission.transmission_id,
                )
            ],
            position=position,
        )
        return RadioInterpretationResult(interpretations=[interpretation], accepted_events=[event])

    if transmission.clip_id == "lognet-1-nomad-6-route-dagger-hazard":
        summary = "Nomad 6 reports a possible route hazard near Checkpoint Slate."
        interpretation = ReviewRequiredRadioInterpretation(
            interpretation_id="interp-rt-lognet-1-nomad-6-route-dagger-hazard",
            kind="review_required",
            status="pending",
            summary=summary,
            extracted_callsigns=extract_callsigns(transmission.transcript),
            proposed_hazard=ProposedHazardMeaning(
                hazard_type="possible_ied",
                route_name="Route Dagger",
                location_name="Checkpoint Slate",
                center=KNOWN_HAZARD_LOCATIONS["Checkpoint Slate"],
                buffer_radius_meters=750,
                buffer_rule="possible_ied hazards require a 750m denied-area buffer",
            ),
        )
        return RadioInterpretationResult(interpretations=[interpretation], accepted_events=[])

    if transmission.clip_id == "lognet-1-nomad-6-jp8-burn-rate":
        event_id = "evt-rt-lognet-1-nomad-6-jp8-burn-rate-supply-signal"
        summary = "Nomad 6 reports JP-8 burn rate at 3.2x baseline."
        interpretation = AutoAcceptedRadioInterpretation(
            interpretation_id="interp-rt-lognet-1-nomad-6-jp8-burn-rate-supply-signal",
            kind="auto_accepted",
            domain_event_id=event_id,
            summary=summary,
            extracted_callsigns=extract_callsigns(transmission.transcript),
        )
        accepted_at = parse_fixture_timestamp(transmission.recorded_at)
        event = AcceptedDomainEvent(
            event_id=event_id,
            event_type="supply_signal",
            subject_id="nomad",
            source_callsign="Nomad 6",
            occurred_at=accepted_at,
            accepted_at=accepted_at,
            summary=summary,
            evidence=[
                EventEvidence(
                    kind="radio_transmission",
                    reference=transmission.transmission_id,
                )
            ],
            supply_signal=SupplySignal(
                unit_id="nomad",
                tracked_supply="JP-8",
                current_quantity=510.0,
                daily_burn_rate_multiplier=3.2,
                reason="contact increased screen-line fuel consumption",
            ),
        )
        return RadioInterpretationResult(interpretations=[interpretation], accepted_events=[event])

    return RadioInterpretationResult(interpretations=[], accepted_events=[])


def extract_callsigns(transcript: str) -> list[str]:
    return list(dict.fromkeys(CALLSIGN_PATTERN.findall(transcript)))


def parse_fixture_timestamp(value: str) -> datetime:
    timestamp = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(timestamp)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def accepted_denied_area_event_for_interpretation(
    interpretation: ReviewRequiredRadioInterpretation,
) -> AcceptedDomainEvent:
    hazard = interpretation.proposed_hazard
    transmission_id = interpretation.interpretation_id.removeprefix("interp-")
    route_slug = slugify(hazard.route_name)
    location_slug = slugify(hazard.location_name)
    denied_area = DeniedArea(
        denied_area_id=f"da-{route_slug}-{location_slug}",
        name=f"{hazard.route_name} {hazard.location_name} Denied Area",
        hazard_type=hazard.hazard_type,
        route_name=hazard.route_name,
        center=hazard.center,
        radius_meters=hazard.buffer_radius_meters,
        buffer_rule=hazard.buffer_rule,
        polygon=build_buffer_polygon(hazard.center, hazard.buffer_radius_meters),
    )
    event_id = f"evt-{transmission_id}-denied-area"
    event_time = parse_fixture_timestamp("2026-05-17T03:19:00Z")
    source_callsign = (
        interpretation.extracted_callsigns[-1]
        if interpretation.extracted_callsigns
        else "Unknown"
    )

    return AcceptedDomainEvent(
        event_id=event_id,
        event_type="denied_area_created",
        subject_id=route_slug,
        source_callsign=source_callsign,
        occurred_at=event_time,
        accepted_at=event_time,
        summary=f"Denied Area created for possible IED indicators near {hazard.location_name}.",
        evidence=[
            EventEvidence(
                kind="radio_transmission",
                reference=transmission_id,
            ),
            EventEvidence(
                kind="proposed_interpretation",
                reference=interpretation.interpretation_id,
            ),
        ],
        denied_area=denied_area,
    )


def build_buffer_polygon(
    center: EventCoordinate,
    radius_meters: int,
    segments: int = 8,
) -> list[EventCoordinate]:
    latitude_delta = radius_meters / 111_320
    longitude_delta = radius_meters / (111_320 * math.cos(math.radians(center.latitude)))

    return [
        EventCoordinate(
            latitude=round(
                center.latitude + latitude_delta * math.sin((2 * math.pi * index) / segments),
                6,
            ),
            longitude=round(
                center.longitude + longitude_delta * math.cos((2 * math.pi * index) / segments),
                6,
            ),
        )
        for index in range(segments)
    ]


def slugify(value: str) -> str:
    return "-".join(re.findall(r"[a-z0-9]+", value.lower()))


class FixtureTranscriptionPipeline:
    pipeline_name = "Fixture Transcription Pipeline"

    def __init__(
        self,
        clips_provider: Callable[[], list[PrerecordedRadioClip]] | None = None,
    ) -> None:
        self.clips_provider = clips_provider or load_kaohsiung_tainan_prerecorded_radio_clips

    def list_prerecorded_clips(self) -> list[PublicPrerecordedRadioClip]:
        return [
            PublicPrerecordedRadioClip.model_validate(clip.model_dump(exclude={"transcription_fixture"}))
            for clip in self.clips_provider()
        ]

    def transcribe_prerecorded_clip(self, clip_id: str) -> RadioTransmission:
        for clip in self.clips_provider():
            if clip.clip_id == clip_id:
                return RadioTransmission(
                    transmission_id=f"rt-{clip.clip_id}",
                    clip_id=clip.clip_id,
                    radio_channel=clip.radio_channel,
                    source_callsign=clip.source_callsign,
                    recorded_at=clip.recorded_at,
                    audio=clip.audio,
                    transcript=clip.transcription_fixture.transcript,
                    transcription=TranscriptionMetadata(
                        pipeline=self.pipeline_name,
                        fixture_id=clip.transcription_fixture.fixture_id,
                    ),
                )

        raise PrerecordedRadioClipNotFound(clip_id)


DEFAULT_PRERECORDED_RADIO_CLIPS_PATH = (
    Path(__file__).resolve().parents[4]
    / "data"
    / "scenarios"
    / "kaohsiung_tainan_prerecorded_radio_clips.json"
)


@lru_cache(maxsize=1)
def load_kaohsiung_tainan_prerecorded_radio_clips(
    path: Path = DEFAULT_PRERECORDED_RADIO_CLIPS_PATH,
) -> list[PrerecordedRadioClip]:
    return [
        PrerecordedRadioClip.model_validate(clip)
        for clip in json.loads(path.read_text(encoding="utf-8"))
    ]
