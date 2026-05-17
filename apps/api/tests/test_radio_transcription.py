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


def test_seeded_radio_transmission_auto_accepts_position_update_and_projects_logistics_picture() -> None:
    ledger_store = InMemoryEventLedgerStore()
    client = TestClient(create_app(event_ledger_store=ledger_store))

    transmission_response = client.post(
        "/radio/transmissions",
        json={"clip_id": "lognet-1-mule-2-checkpoint-slate"},
    )

    assert transmission_response.status_code == 201
    transmission = transmission_response.json()
    assert transmission["interpretations"] == [
        {
            "interpretation_id": "interp-rt-lognet-1-mule-2-checkpoint-slate-position-update",
            "kind": "auto_accepted",
            "domain_event_id": "evt-rt-lognet-1-mule-2-checkpoint-slate-position-update",
            "summary": "Mule 2 reports passing Checkpoint Slate.",
            "extracted_callsigns": ["Hammer 4", "Mule 2"],
        }
    ]

    ledger_response = client.get("/events/accepted")

    assert ledger_response.status_code == 200
    accepted_events = ledger_response.json()
    assert accepted_events[0]["event_id"] == "evt-rt-lognet-1-mule-2-checkpoint-slate-position-update"
    assert accepted_events[0]["event_type"] == "position_update"
    assert accepted_events[0]["subject_id"] == "mule-2"
    assert accepted_events[0]["source_callsign"] == "Mule 2"
    assert accepted_events[0]["summary"] == "Mule 2 reports passing Checkpoint Slate."
    assert accepted_events[0]["evidence"] == [
        {
            "kind": "radio_transmission",
            "reference": "rt-lognet-1-mule-2-checkpoint-slate",
        }
    ]
    assert accepted_events[0]["position"] == {
        "latitude": 22.812,
        "longitude": 120.318,
    }

    picture_response = client.get("/scenarios/kaohsiung-tainan/logistics-picture")

    assert picture_response.status_code == 200
    picture = picture_response.json()
    mule_location = next(
        location
        for location in picture["locations"]
        if location["id"] == picture["supply_convoy"]["location_id"]
    )
    assert mule_location["coordinate"] == {
        "latitude": 22.812,
        "longitude": 120.318,
    }
    assert picture["projection"]["source"] == "Event Ledger"
    assert picture["projection"]["accepted_event_count"] == 1


def test_retransmitting_seeded_radio_clip_does_not_duplicate_auto_accepted_event() -> None:
    ledger_store = InMemoryEventLedgerStore()
    client = TestClient(create_app(event_ledger_store=ledger_store))

    first_response = client.post(
        "/radio/transmissions",
        json={"clip_id": "lognet-1-mule-2-checkpoint-slate"},
    )
    second_response = client.post(
        "/radio/transmissions",
        json={"clip_id": "lognet-1-mule-2-checkpoint-slate"},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    ledger_response = client.get("/events/accepted")

    assert ledger_response.status_code == 200
    accepted_events = ledger_response.json()
    assert [event["event_id"] for event in accepted_events] == [
        "evt-rt-lognet-1-mule-2-checkpoint-slate-position-update"
    ]
