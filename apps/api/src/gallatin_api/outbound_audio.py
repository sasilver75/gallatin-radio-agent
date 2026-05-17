from typing import Literal

from pydantic import BaseModel


class OutboundAudio(BaseModel):
    audio_id: str
    source_kind: Literal["addressed_response", "draft_transmission"]
    source_id: str
    voice: str
    content_type: Literal["audio/wav"]
    duration_seconds: float
    fixture_uri: str
    generated_at: str
    transcript: str


def deterministic_outbound_audio(
    source_kind: Literal["addressed_response", "draft_transmission"],
    source_id: str,
    transcript: str,
    generated_at: str,
    duration_seconds: float,
) -> OutboundAudio:
    audio_id = f"oa-{source_id}"
    return OutboundAudio(
        audio_id=audio_id,
        source_kind=source_kind,
        source_id=source_id,
        voice="Quarterback deterministic fixture voice",
        content_type="audio/wav",
        duration_seconds=duration_seconds,
        fixture_uri=f"fixture://outbound-audio/{audio_id}.wav",
        generated_at=generated_at,
        transcript=transcript,
    )
