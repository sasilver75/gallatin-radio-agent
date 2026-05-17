from fastapi.testclient import TestClient

from gallatin_api.event_ledger import InMemoryEventLedgerStore
from gallatin_api.main import create_app


def test_kaohsiung_tainan_logistics_picture_returns_seed_entities() -> None:
    client = TestClient(create_app(event_ledger_store=InMemoryEventLedgerStore()))

    response = client.get("/scenarios/kaohsiung-tainan/logistics-picture")

    assert response.status_code == 200
    body = response.json()
    assert body["scenario_id"] == "kaohsiung-tainan-v1"
    assert body["area_of_operations"]["name"] == "Kaohsiung-Tainan Corridor AO"
    assert body["logistics_watch_officer"] == "Hammer 4"
    assert body["radio_channel"] == "LOGNET-1"

    location_roles = {location["role"] for location in body["locations"]}
    assert "Logistics Support Area" in location_roles
    assert "Logistics Release Point" in location_roles

    supported_units = {unit["callsign"]: unit for unit in body["supported_units"]}
    assert set(supported_units) == {"Viper", "Archer", "Nomad"}
    assert supported_units["Viper"]["inventory"][0]["status"] == "red"
    assert supported_units["Archer"]["inventory"][0]["class_of_supply"] == "Class V"
    assert supported_units["Nomad"]["inventory"][0]["class_of_supply"] == "Class I"

    convoy = body["supply_convoy"]
    assert convoy["callsign"] == "Mule 2"
    assert convoy["route_location_ids"] == [
        "lsa-south-dock",
        "mule-2-current",
        "lrp-bravo",
    ]
    assert {item["class_of_supply"] for item in convoy["supply_load"]} == {
        "Class I",
        "Class III",
        "Class V",
    }
