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


def test_accepted_supply_signal_updates_inventory_projection_and_status_band() -> None:
    ledger_store = InMemoryEventLedgerStore()
    client = TestClient(create_app(event_ledger_store=ledger_store))

    seeded_picture_response = client.get("/scenarios/kaohsiung-tainan/logistics-picture")

    assert seeded_picture_response.status_code == 200
    seeded_nomad_jp8 = inventory_item(
        seeded_picture_response.json(),
        unit_id="nomad",
        tracked_supply="JP-8",
    )
    assert seeded_nomad_jp8["projection"] == {
        "source": "Scenario Seed",
        "source_event_id": None,
        "baseline_days_of_supply": 2.8,
        "projected_days_of_supply": 2.8,
        "baseline_daily_burn_rate": 182.1,
        "projected_daily_burn_rate": 182.1,
        "burn_rate_change": "baseline",
        "status_before": "green",
        "status_after": "green",
        "projected_black_time": None,
    }

    transmission_response = client.post(
        "/radio/transmissions",
        json={"clip_id": "lognet-1-nomad-6-jp8-burn-rate"},
    )

    assert transmission_response.status_code == 201
    transmission = transmission_response.json()
    assert transmission["interpretations"] == [
        {
            "interpretation_id": "interp-rt-lognet-1-nomad-6-jp8-burn-rate-supply-signal",
            "kind": "auto_accepted",
            "domain_event_id": "evt-rt-lognet-1-nomad-6-jp8-burn-rate-supply-signal",
            "summary": "Nomad 6 reports JP-8 burn rate at 3.2x baseline.",
            "extracted_callsigns": ["Hammer 4", "Nomad 6"],
        }
    ]

    ledger_response = client.get("/events/accepted")

    assert ledger_response.status_code == 200
    accepted_event = ledger_response.json()[0]
    assert accepted_event["event_type"] == "supply_signal"
    assert accepted_event["supply_signal"] == {
        "unit_id": "nomad",
        "tracked_supply": "JP-8",
        "current_quantity": 510.0,
        "daily_burn_rate_multiplier": 3.2,
        "reason": "contact increased screen-line fuel consumption",
    }

    projected_picture_response = client.get("/scenarios/kaohsiung-tainan/logistics-picture")

    assert projected_picture_response.status_code == 200
    projected_nomad_jp8 = inventory_item(
        projected_picture_response.json(),
        unit_id="nomad",
        tracked_supply="JP-8",
    )
    assert projected_nomad_jp8["quantity"] == 510.0
    assert projected_nomad_jp8["days_of_supply"] == 0.9
    assert projected_nomad_jp8["projected_black_time"] == "2026-05-18T00:24:00Z"
    assert projected_nomad_jp8["status"] == "red"
    assert projected_nomad_jp8["projection"] == {
        "source": "Event Ledger",
        "source_event_id": "evt-rt-lognet-1-nomad-6-jp8-burn-rate-supply-signal",
        "baseline_days_of_supply": 2.8,
        "projected_days_of_supply": 0.9,
        "baseline_daily_burn_rate": 182.1,
        "projected_daily_burn_rate": 582.9,
        "burn_rate_change": "3.2x baseline",
        "status_before": "green",
        "status_after": "red",
        "projected_black_time": "2026-05-18T00:24:00Z",
    }


def test_accepted_operational_changes_regenerate_executable_coa_from_route_and_inventory_state() -> None:
    ledger_store = InMemoryEventLedgerStore()
    proposed_store = InMemoryProposedInterpretationStore()
    client = TestClient(
        create_app(
            event_ledger_store=ledger_store,
            proposed_interpretation_store=proposed_store,
        )
    )
    hazard_interpretation_id = "interp-rt-lognet-1-nomad-6-route-dagger-hazard"

    client.post(
        "/radio/transmissions",
        json={"clip_id": "lognet-1-nomad-6-route-dagger-hazard"},
    )
    client.post(f"/interpretations/proposed/{hazard_interpretation_id}/accept")
    client.post(
        "/radio/transmissions",
        json={"clip_id": "lognet-1-nomad-6-jp8-burn-rate"},
    )
    picture_response = client.get("/scenarios/kaohsiung-tainan/logistics-picture")

    assert picture_response.status_code == 200
    picture = picture_response.json()
    coas = picture["executable_coas"]
    assert [coa["coa_id"] for coa in coas] == [
        "coa-route-dagger-western-bypass-nomad-jp8-resupply"
    ]

    coa = coas[0]
    assert coa["name"] == "Route Dagger Western Bypass / Nomad JP-8 Resupply"
    assert coa["source_event_ids"] == [
        "evt-rt-lognet-1-nomad-6-route-dagger-hazard-denied-area",
        "evt-rt-lognet-1-nomad-6-jp8-burn-rate-supply-signal",
    ]
    assert coa["rationale"] == (
        "Accepted Denied Area and Supply Signal require a bypass LOGPAC revision."
    )
    assert len(coa["movements"]) == 1

    movement = coa["movements"][0]
    assert movement["movement_id"] == "mov-route-dagger-western-bypass-nomad-jp8"
    assert movement["movement_status"] == "Proposed Movement Status"
    assert movement["route_variant_id"] == "route-variant-route-dagger-western-bypass"
    assert movement["route_name"] == "Route Dagger Western Bypass"
    assert movement["depart_at"] == "2026-05-17T04:00:00Z"
    assert movement["arrive_at"] == "2026-05-17T05:04:00Z"
    assert movement["logpac"] == [
        {
            "tracked_supply": "JP-8",
            "class_of_supply": "Class III",
            "quantity": 480.0,
            "unit": "gal",
            "destination_unit_id": "nomad",
            "destination_callsign": "Nomad",
            "reason": "Restore Nomad JP-8 above red after 3.2x burn-rate Supply Signal.",
        }
    ]
    assert movement["assumptions"] == [
        "Mule 2 remains available for one LOGPAC movement.",
        "Route Dagger Western Bypass remains clear of accepted Denied Areas.",
    ]
    assert movement["risks"] == [
        "Route Dagger baseline conflicts with Route Dagger Checkpoint Slate Denied Area.",
        "Nomad JP-8 reaches projected black time at 2026-05-18T00:24:00Z without resupply.",
    ]
    assert movement["projected_effect"] == (
        "Nomad JP-8 improves from 0.9 DOS red to 1.7 DOS amber before projected black time 2026-05-18T00:24:00Z."
    )


def test_coa_approval_applies_selected_route_and_logpac_only_after_operator_action() -> None:
    client = coa_decision_test_client()
    build_nomad_route_dagger_coa(client)

    proposed_picture_response = client.get("/scenarios/kaohsiung-tainan/logistics-picture")

    assert proposed_picture_response.status_code == 200
    proposed_picture = proposed_picture_response.json()
    proposed_coa = proposed_picture["executable_coas"][0]
    assert proposed_coa["coa_id"] == "coa-route-dagger-western-bypass-nomad-jp8-resupply"
    assert proposed_coa["decision_status"] == "proposed"
    assert proposed_coa["decision_event_id"] is None
    assert proposed_picture["supply_convoy"]["movement_status"] == "Proposed Movement Status"
    assert proposed_picture["supply_convoy"]["selected_route_variant_id"] is None
    assert proposed_picture["supply_convoy"]["selected_route_name"] is None
    assert proposed_picture["supply_convoy"]["supply_load"] == [
        {
            "tracked_supply": "JP-8",
            "class_of_supply": "Class III",
            "quantity": 1200.0,
            "unit": "gal",
            "destination_unit_id": "viper",
        },
        {
            "tracked_supply": "155mm HE",
            "class_of_supply": "Class V",
            "quantity": 96.0,
            "unit": "rd",
            "destination_unit_id": "archer",
        },
        {
            "tracked_supply": "Meals",
            "class_of_supply": "Class I",
            "quantity": 800.0,
            "unit": "ea",
            "destination_unit_id": "nomad",
        },
    ]

    approval_response = client.post(
        "/coas/coa-route-dagger-western-bypass-nomad-jp8-resupply/approve"
    )

    assert approval_response.status_code == 201
    approval_event = approval_response.json()
    assert approval_event["event_id"] == (
        "evt-coa-route-dagger-western-bypass-nomad-jp8-resupply-approval"
    )
    assert approval_event["event_type"] == "coa_decision"
    assert approval_event["subject_id"] == "coa-route-dagger-western-bypass-nomad-jp8-resupply"
    assert approval_event["source_callsign"] == "Hammer 4"
    assert approval_event["summary"] == (
        "Hammer 4 approved Route Dagger Western Bypass / Nomad JP-8 Resupply."
    )
    assert approval_event["coa_decision"] == {
        "coa_id": "coa-route-dagger-western-bypass-nomad-jp8-resupply",
        "decision": "approved",
        "decided_by": "Hammer 4",
        "movement_id": "mov-route-dagger-western-bypass-nomad-jp8",
        "selected_route_variant_id": "route-variant-route-dagger-western-bypass",
        "selected_route_name": "Route Dagger Western Bypass",
    }

    approved_picture_response = client.get("/scenarios/kaohsiung-tainan/logistics-picture")

    assert approved_picture_response.status_code == 200
    approved_picture = approved_picture_response.json()
    approved_coa = approved_picture["executable_coas"][0]
    assert approved_coa["decision_status"] == "approved"
    assert approved_coa["decision_event_id"] == approval_event["event_id"]
    assert approved_coa["movements"][0]["movement_status"] == "Approved Movement Status"
    assert approved_picture["supply_convoy"]["movement_status"] == "Approved Movement Status"
    assert (
        approved_picture["supply_convoy"]["selected_route_variant_id"]
        == "route-variant-route-dagger-western-bypass"
    )
    assert approved_picture["supply_convoy"]["selected_route_name"] == "Route Dagger Western Bypass"
    assert approved_picture["supply_convoy"]["route_summary"] == "Route Dagger Western Bypass"
    assert approved_picture["supply_convoy"]["supply_load"] == [
        {
            "tracked_supply": "JP-8",
            "class_of_supply": "Class III",
            "quantity": 480.0,
            "unit": "gal",
            "destination_unit_id": "nomad",
        }
    ]
    assert [event["event_id"] for event in approved_picture["event_ledger"]] == [
        "evt-rt-lognet-1-nomad-6-route-dagger-hazard-denied-area",
        "evt-rt-lognet-1-nomad-6-jp8-burn-rate-supply-signal",
        "evt-coa-route-dagger-western-bypass-nomad-jp8-resupply-approval",
    ]


def test_coa_rejection_records_operator_decision_without_applying_proposed_movement() -> None:
    client = coa_decision_test_client()
    build_nomad_route_dagger_coa(client)

    proposed_picture = client.get("/scenarios/kaohsiung-tainan/logistics-picture").json()
    proposed_supply_convoy = proposed_picture["supply_convoy"]

    rejection_response = client.post(
        "/coas/coa-route-dagger-western-bypass-nomad-jp8-resupply/reject"
    )

    assert rejection_response.status_code == 201
    rejection_event = rejection_response.json()
    assert rejection_event["event_id"] == (
        "evt-coa-route-dagger-western-bypass-nomad-jp8-resupply-rejection"
    )
    assert rejection_event["event_type"] == "coa_decision"
    assert rejection_event["subject_id"] == "coa-route-dagger-western-bypass-nomad-jp8-resupply"
    assert rejection_event["source_callsign"] == "Hammer 4"
    assert rejection_event["summary"] == (
        "Hammer 4 rejected Route Dagger Western Bypass / Nomad JP-8 Resupply."
    )
    assert rejection_event["coa_decision"] == {
        "coa_id": "coa-route-dagger-western-bypass-nomad-jp8-resupply",
        "decision": "rejected",
        "decided_by": "Hammer 4",
    }

    rejected_picture_response = client.get("/scenarios/kaohsiung-tainan/logistics-picture")

    assert rejected_picture_response.status_code == 200
    rejected_picture = rejected_picture_response.json()
    rejected_coa = rejected_picture["executable_coas"][0]
    assert rejected_coa["decision_status"] == "rejected"
    assert rejected_coa["decision_event_id"] == rejection_event["event_id"]
    assert rejected_coa["movements"][0]["movement_status"] == "Proposed Movement Status"
    assert rejected_picture["supply_convoy"]["movement_status"] == "Proposed Movement Status"
    assert rejected_picture["supply_convoy"]["selected_route_variant_id"] is None
    assert rejected_picture["supply_convoy"]["selected_route_name"] is None
    assert rejected_picture["supply_convoy"]["route_summary"] == proposed_supply_convoy["route_summary"]
    assert rejected_picture["supply_convoy"]["supply_load"] == proposed_supply_convoy["supply_load"]
    assert [event["event_id"] for event in rejected_picture["event_ledger"]] == [
        "evt-rt-lognet-1-nomad-6-route-dagger-hazard-denied-area",
        "evt-rt-lognet-1-nomad-6-jp8-burn-rate-supply-signal",
        "evt-coa-route-dagger-western-bypass-nomad-jp8-resupply-rejection",
    ]


def test_addressed_last_thirty_intent_returns_grounded_rollup_without_mutating_state() -> None:
    client = coa_decision_test_client()
    build_nomad_route_dagger_coa(client)
    events_before = client.get("/events/accepted").json()
    picture_before = client.get("/scenarios/kaohsiung-tainan/logistics-picture").json()

    response = client.post(
        "/radio/transmissions",
        json={"clip_id": "lognet-1-hammer-4-quarterback-last-thirty"},
    )

    assert response.status_code == 201
    transmission = response.json()
    assert transmission["transmission_id"] == "rt-lognet-1-hammer-4-quarterback-last-thirty"
    assert transmission["source_callsign"] == "Hammer 4"
    assert transmission["transcript"] == (
        "Quarterback, Hammer 4. Give me the last thirty and impact to tonight's resupply."
    )
    assert transmission["interpretations"] == [
        {
            "interpretation_id": "interp-rt-lognet-1-hammer-4-quarterback-last-thirty",
            "kind": "addressed_intent",
            "intent_type": "last_thirty_resupply_impact",
            "addressed_to": "Quarterback",
            "summary": "Hammer 4 asks Quarterback for the last thirty and resupply impact.",
            "extracted_callsigns": ["Hammer 4"],
            "response": {
                "response_id": (
                    "resp-rt-lognet-1-hammer-4-quarterback-last-thirty-"
                    "last-thirty-resupply-impact"
                ),
                "agent_callsign": "Quarterback",
                "summary": (
                    "Quarterback rollup grounded in 2 Event Ledger entries, "
                    "0 pending Proposed Interpretations, and 1 generated Executable COA."
                ),
                "radio_brevity": (
                    "Hammer 4, Quarterback. Last thirty: Route Dagger denied near "
                    "Checkpoint Slate; Nomad JP-8 red, 0.9 DOS, black at "
                    "2026-05-18T00:24:00Z. Review Route Dagger Western Bypass / "
                    "Nomad JP-8 Resupply."
                ),
                "grounding": [
                    {
                        "kind": "event_ledger",
                        "reference": "evt-rt-lognet-1-nomad-6-route-dagger-hazard-denied-area",
                        "label": "Denied Area created for possible IED indicators near Checkpoint Slate.",
                    },
                    {
                        "kind": "event_ledger",
                        "reference": "evt-rt-lognet-1-nomad-6-jp8-burn-rate-supply-signal",
                        "label": "Nomad 6 reports JP-8 burn rate at 3.2x baseline.",
                    },
                    {
                        "kind": "logistics_picture",
                        "reference": "inventory:nomad:JP-8",
                        "label": "Nomad JP-8 red / 0.9 DOS / projected black 2026-05-18T00:24:00Z.",
                    },
                    {
                        "kind": "proposed_interpretations",
                        "reference": "pending:0",
                        "label": "0 pending Review-Required Interpretations.",
                    },
                    {
                        "kind": "executable_coa",
                        "reference": "coa-route-dagger-western-bypass-nomad-jp8-resupply",
                        "label": "Route Dagger Western Bypass / Nomad JP-8 Resupply.",
                    },
                ],
            },
        }
    ]

    assert client.get("/events/accepted").json() == events_before
    picture_after = client.get("/scenarios/kaohsiung-tainan/logistics-picture").json()
    assert picture_after["supply_convoy"] == picture_before["supply_convoy"]
    assert picture_after["executable_coas"][0]["decision_status"] == "proposed"


def inventory_item(
    picture: dict[str, object],
    unit_id: str,
    tracked_supply: str,
) -> dict[str, object]:
    units = picture["supported_units"]
    assert isinstance(units, list)
    unit = next(
        unit
        for unit in units
        if isinstance(unit, dict) and unit["id"] == unit_id
    )
    return next(
        item
        for item in unit["inventory"]
        if isinstance(item, dict) and item["tracked_supply"] == tracked_supply
    )


def coa_decision_test_client() -> TestClient:
    ledger_store = InMemoryEventLedgerStore()
    proposed_store = InMemoryProposedInterpretationStore()
    return TestClient(
        create_app(
            event_ledger_store=ledger_store,
            proposed_interpretation_store=proposed_store,
        )
    )


def build_nomad_route_dagger_coa(client: TestClient) -> None:
    hazard_interpretation_id = "interp-rt-lognet-1-nomad-6-route-dagger-hazard"
    client.post(
        "/radio/transmissions",
        json={"clip_id": "lognet-1-nomad-6-route-dagger-hazard"},
    )
    client.post(f"/interpretations/proposed/{hazard_interpretation_id}/accept")
    client.post(
        "/radio/transmissions",
        json={"clip_id": "lognet-1-nomad-6-jp8-burn-rate"},
    )
