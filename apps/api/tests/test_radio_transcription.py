from fastapi.testclient import TestClient

from gallatin_api.event_ledger import InMemoryEventLedgerStore
from gallatin_api.main import create_app


def test_prerecorded_tactical_radio_audio_transcribes_with_source_metadata() -> None:
    client = TestClient(create_app(event_ledger_store=InMemoryEventLedgerStore()))

    clips_response = client.get("/radio/prerecorded-clips")

    assert clips_response.status_code == 200
    clips = clips_response.json()
    assert clips[0]["clip_id"] == "lognet-1-mule-2-checkpoint-slate"
    assert clips[0]["radio_channel"] == "LOGNET-1"
    assert clips[0]["source_callsign"] == "Mule 2"
    assert clips[0]["audio"]["filename"] == "lognet-1-mule-2-checkpoint-slate.wav"

    transmission_response = client.post(
        "/radio/transmissions",
        json={"clip_id": "lognet-1-mule-2-checkpoint-slate"},
    )

    assert transmission_response.status_code == 201
    transmission = transmission_response.json()
    assert transmission["transmission_id"] == "rt-lognet-1-mule-2-checkpoint-slate"
    assert transmission["radio_channel"] == "LOGNET-1"
    assert transmission["source_callsign"] == "Mule 2"
    assert transmission["audio"]["filename"] == "lognet-1-mule-2-checkpoint-slate.wav"
    assert transmission["transcription"]["pipeline"] == "Fixture Transcription Pipeline"
    assert transmission["transcription"]["fixture_id"] == "mule-2-checkpoint-slate-transcript"
    assert (
        transmission["transcript"]
        == "Hammer 4, Mule 2 passing Checkpoint Slate now. Convoy remains green, estimate LRP Bravo in 18 mikes."
    )
