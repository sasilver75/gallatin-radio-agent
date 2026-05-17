import os

import pytest
from fastapi.testclient import TestClient

from gallatin_api.event_ledger import PostgresEventLedgerStore
from gallatin_api.main import create_app


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


@pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="TEST_DATABASE_URL is required for Postgres Event Ledger tests.",
)
def test_accepted_position_update_persists_and_projects_logistics_picture(
) -> None:
    assert TEST_DATABASE_URL is not None
    store = PostgresEventLedgerStore(TEST_DATABASE_URL)
    store.clear()
    client = TestClient(create_app(event_ledger_store=store))

    response = client.post(
        "/events/accepted",
        json={
            "event_id": "evt-mule-2-position-checkpoint-slate",
            "event_type": "position_update",
            "subject_id": "mule-2",
            "source_callsign": "Mule 2",
            "occurred_at": "2026-05-17T03:12:00Z",
            "accepted_at": "2026-05-17T03:14:00Z",
            "summary": "Mule 2 reports passing Checkpoint Slate.",
            "evidence": [
                {
                    "kind": "radio_transmission",
                    "reference": "LOGNET-1 transmission 004",
                }
            ],
            "position": {
                "latitude": 22.812,
                "longitude": 120.318,
            },
        },
    )

    assert response.status_code == 201
    accepted_event = response.json()
    assert accepted_event["event_id"] == "evt-mule-2-position-checkpoint-slate"
    assert accepted_event["event_type"] == "position_update"
    assert accepted_event["source_callsign"] == "Mule 2"
    assert accepted_event["evidence"][0]["reference"] == "LOGNET-1 transmission 004"

    duplicate_response = client.post("/events/accepted", json=accepted_event)

    assert duplicate_response.status_code == 201

    ledger_response = client.get("/events/accepted")

    assert ledger_response.status_code == 200
    assert ledger_response.json() == [accepted_event]

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
    assert mule_location["description"] == "Projected from accepted Position Update."
    assert picture["projection"]["source"] == "Event Ledger"
    assert picture["projection"]["accepted_event_count"] == 1
    assert picture["event_ledger"] == [accepted_event]
