import json
import re
from collections.abc import Callable
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Literal, Protocol

from pydantic import BaseModel, Field

from gallatin_api.event_ledger import AcceptedDomainEvent, EventCoordinate, EventEvidence


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


class RadioInterpretation(BaseModel):
    interpretation_id: str
    kind: Literal["auto_accepted"]
    domain_event_id: str
    summary: str
    extracted_callsigns: list[str]


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


class PrerecordedRadioClipNotFound(Exception):
    pass


CALLSIGN_PATTERN = re.compile(r"\b[A-Z][a-z]+ \d\b")
POSITION_UPDATE_PATTERN = re.compile(
    r"\b(?P<callsign>[A-Z][a-z]+ \d) passing (?P<location>Checkpoint Slate) now\b"
)
KNOWN_POSITION_UPDATE_LOCATIONS = {
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
        interpretation = RadioInterpretation(
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

    return RadioInterpretationResult(interpretations=[], accepted_events=[])


def extract_callsigns(transcript: str) -> list[str]:
    return list(dict.fromkeys(CALLSIGN_PATTERN.findall(transcript)))


def parse_fixture_timestamp(value: str) -> datetime:
    timestamp = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(timestamp)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


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
