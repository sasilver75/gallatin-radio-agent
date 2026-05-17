from fastapi.testclient import TestClient

from gallatin_api.event_ledger import InMemoryEventLedgerStore
from gallatin_api.main import create_app
from gallatin_api.radio import InMemoryProposedInterpretationStore


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


def test_seeded_hazard_radio_transmission_creates_review_required_interpretation_without_changing_picture() -> None:
    ledger_store = InMemoryEventLedgerStore()
    proposed_store = InMemoryProposedInterpretationStore()
    client = TestClient(
        create_app(
            event_ledger_store=ledger_store,
            proposed_interpretation_store=proposed_store,
        )
    )

    transmission_response = client.post(
        "/radio/transmissions",
        json={"clip_id": "lognet-1-nomad-6-route-dagger-hazard"},
    )

    assert transmission_response.status_code == 201
    transmission = transmission_response.json()
    assert transmission["interpretations"] == [
        {
            "interpretation_id": "interp-rt-lognet-1-nomad-6-route-dagger-hazard",
            "kind": "review_required",
            "domain_event_id": None,
            "status": "pending",
            "summary": "Nomad 6 reports a possible route hazard near Checkpoint Slate.",
            "extracted_callsigns": ["Hammer 4", "Nomad 6"],
            "proposed_hazard": {
                "hazard_type": "possible_ied",
                "route_name": "Route Dagger",
                "location_name": "Checkpoint Slate",
                "center": {
                    "latitude": 22.812,
                    "longitude": 120.318,
                },
                "buffer_radius_meters": 750,
                "buffer_rule": "possible_ied hazards require a 750m denied-area buffer",
            },
        }
    ]

    ledger_response = client.get("/events/accepted")

    assert ledger_response.status_code == 200
    assert ledger_response.json() == []

    picture_response = client.get("/scenarios/kaohsiung-tainan/logistics-picture")

    assert picture_response.status_code == 200
    assert picture_response.json()["denied_areas"] == []


def test_accepting_seeded_hazard_interpretation_creates_denied_area_from_buffer_rules() -> None:
    ledger_store = InMemoryEventLedgerStore()
    proposed_store = InMemoryProposedInterpretationStore()
    client = TestClient(
        create_app(
            event_ledger_store=ledger_store,
            proposed_interpretation_store=proposed_store,
        )
    )
    interpretation_id = "interp-rt-lognet-1-nomad-6-route-dagger-hazard"

    transmission_response = client.post(
        "/radio/transmissions",
        json={"clip_id": "lognet-1-nomad-6-route-dagger-hazard"},
    )
    accept_response = client.post(f"/interpretations/proposed/{interpretation_id}/accept")

    assert transmission_response.status_code == 201
    assert accept_response.status_code == 201
    accepted_event = accept_response.json()
    assert accepted_event["event_id"] == "evt-rt-lognet-1-nomad-6-route-dagger-hazard-denied-area"
    assert accepted_event["event_type"] == "denied_area_created"
    assert accepted_event["subject_id"] == "route-dagger"
    assert accepted_event["source_callsign"] == "Nomad 6"
    assert accepted_event["summary"] == "Denied Area created for possible IED indicators near Checkpoint Slate."
    assert accepted_event["evidence"] == [
        {
            "kind": "radio_transmission",
            "reference": "rt-lognet-1-nomad-6-route-dagger-hazard",
        },
        {
            "kind": "proposed_interpretation",
            "reference": interpretation_id,
        },
    ]
    assert accepted_event["denied_area"]["denied_area_id"] == "da-route-dagger-checkpoint-slate"
    assert accepted_event["denied_area"]["name"] == "Route Dagger Checkpoint Slate Denied Area"
    assert accepted_event["denied_area"]["hazard_type"] == "possible_ied"
    assert accepted_event["denied_area"]["route_name"] == "Route Dagger"
    assert accepted_event["denied_area"]["center"] == {
        "latitude": 22.812,
        "longitude": 120.318,
    }
    assert accepted_event["denied_area"]["radius_meters"] == 750
    assert accepted_event["denied_area"]["buffer_rule"] == (
        "possible_ied hazards require a 750m denied-area buffer"
    )
    assert len(accepted_event["denied_area"]["polygon"]) == 8

    picture_response = client.get("/scenarios/kaohsiung-tainan/logistics-picture")

    assert picture_response.status_code == 200
    picture = picture_response.json()
    assert picture["denied_areas"] == [accepted_event["denied_area"]]
    assert picture["projection"]["source"] == "Event Ledger"
    assert picture["projection"]["accepted_event_count"] == 1
    assert len(picture["event_ledger"]) == 1
    assert picture["event_ledger"][0]["event_id"] == accepted_event["event_id"]
    assert picture["event_ledger"][0]["denied_area"] == accepted_event["denied_area"]


def test_rejecting_seeded_hazard_interpretation_preserves_rejection_without_changing_picture() -> None:
    ledger_store = InMemoryEventLedgerStore()
    proposed_store = InMemoryProposedInterpretationStore()
    client = TestClient(
        create_app(
            event_ledger_store=ledger_store,
            proposed_interpretation_store=proposed_store,
        )
    )
    interpretation_id = "interp-rt-lognet-1-nomad-6-route-dagger-hazard"

    transmission_response = client.post(
        "/radio/transmissions",
        json={"clip_id": "lognet-1-nomad-6-route-dagger-hazard"},
    )
    reject_response = client.post(f"/interpretations/proposed/{interpretation_id}/reject")
    preserved_response = client.get(f"/interpretations/proposed/{interpretation_id}")

    assert transmission_response.status_code == 201
    assert reject_response.status_code == 200
    rejected_interpretation = reject_response.json()
    assert rejected_interpretation["interpretation_id"] == interpretation_id
    assert rejected_interpretation["kind"] == "review_required"
    assert rejected_interpretation["status"] == "rejected"
    assert rejected_interpretation["domain_event_id"] is None
    assert rejected_interpretation["summary"] == (
        "Nomad 6 reports a possible route hazard near Checkpoint Slate."
    )

    assert preserved_response.status_code == 200
    assert preserved_response.json() == rejected_interpretation

    ledger_response = client.get("/events/accepted")

    assert ledger_response.status_code == 200
    assert ledger_response.json() == []

    picture_response = client.get("/scenarios/kaohsiung-tainan/logistics-picture")

    assert picture_response.status_code == 200
    picture = picture_response.json()
    assert picture["denied_areas"] == []
    assert picture["projection"]["source"] == "Scenario Seed"
    assert picture["projection"]["accepted_event_count"] == 0


def test_accepted_denied_area_generates_route_variants_with_avoid_polygon_evaluation() -> None:
    ledger_store = InMemoryEventLedgerStore()
    proposed_store = InMemoryProposedInterpretationStore()
    client = TestClient(
        create_app(
            event_ledger_store=ledger_store,
            proposed_interpretation_store=proposed_store,
        )
    )
    interpretation_id = "interp-rt-lognet-1-nomad-6-route-dagger-hazard"

    client.post(
        "/radio/transmissions",
        json={"clip_id": "lognet-1-nomad-6-route-dagger-hazard"},
    )
    client.post(f"/interpretations/proposed/{interpretation_id}/accept")
    picture_response = client.get("/scenarios/kaohsiung-tainan/logistics-picture")

    assert picture_response.status_code == 200
    picture = picture_response.json()
    assert picture["denied_areas"][0]["denied_area_id"] == "da-route-dagger-checkpoint-slate"

    generated_routes = picture["generated_routes"]
    assert [route["route_id"] for route in generated_routes] == [
        "route-variant-route-dagger-baseline",
        "route-variant-route-dagger-western-bypass",
    ]
    assert generated_routes[0]["source"] == "Deterministic Local Route Generator"
    assert generated_routes[0]["requested_avoid_polygon_count"] == 1
    assert generated_routes[0]["evaluation"] == {
        "status": "conflicts_with_denied_area",
        "conflicting_denied_area_ids": ["da-route-dagger-checkpoint-slate"],
    }
    assert generated_routes[1]["requested_avoid_polygon_count"] == 1
    assert generated_routes[1]["evaluation"] == {
        "status": "avoids_denied_areas",
        "conflicting_denied_area_ids": [],
    }
    assert generated_routes[1]["summary"] == (
        "Western bypass from LSA South Dock to LRP Bravo avoiding Checkpoint Slate."
    )
