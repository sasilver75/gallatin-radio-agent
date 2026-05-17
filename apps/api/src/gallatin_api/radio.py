import json
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel


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


class RadioTransmission(BaseModel):
    transmission_id: str
    clip_id: str
    radio_channel: str
    source_callsign: str
    recorded_at: str
    audio: AudioMetadata
    transcript: str
    transcription: TranscriptionMetadata


class TranscriptionPipeline(Protocol):
    def list_prerecorded_clips(self) -> list[PublicPrerecordedRadioClip]: ...

    def transcribe_prerecorded_clip(self, clip_id: str) -> RadioTransmission: ...


class PrerecordedRadioClipNotFound(Exception):
    pass


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
