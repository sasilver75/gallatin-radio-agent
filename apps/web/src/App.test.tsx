import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import { LogisticsPictureScenario, ReadinessResponse } from "./api";

const readyResponse: ReadinessResponse = {
  service: "gallatin-radio-agent-api",
  status: "ready",
  dependencies: [
    {
      name: "postgis",
      status: "ready",
      details: "POSTGIS='3.4.0'"
    }
  ]
};

const scenarioResponse: LogisticsPictureScenario = {
  scenario_id: "test-corridor",
  name: "Test Corridor Logistics Picture",
  updated_at: "2026-05-17T02:00:00Z",
  radio_channel: "TESTNET-7",
  agent_callsign: "Backstop",
  logistics_watch_officer: "Anvil 3",
  area_of_operations: {
    id: "test-ao",
    name: "Test Corridor AO",
    corridor: "Test Corridor",
    bounds: {
      west: 120,
      south: 22,
      east: 121,
      north: 23
    },
    polygon: [
      { latitude: 22.9, longitude: 120.1 },
      { latitude: 22.8, longitude: 120.9 },
      { latitude: 22.1, longitude: 120.8 },
      { latitude: 22.2, longitude: 120.2 }
    ]
  },
  friendly_callsigns: [
    { callsign: "Anvil 3", role: "Logistics Watch Officer", entity_id: null },
    { callsign: "Backstop", role: "Radio-to-Map Logistics Agent", entity_id: null },
    { callsign: "Hauler 8", role: "Supply Convoy", entity_id: "hauler-8" },
    { callsign: "Raven 6", role: "Supported Unit Speaker", entity_id: "raven" }
  ],
  locations: [
    {
      id: "test-lsa",
      name: "Test LSA Raven",
      role: "Logistics Support Area",
      coordinate: { latitude: 22.2, longitude: 120.2 },
      description: "Test supply origin."
    },
    {
      id: "test-lrp",
      name: "Test LRP Cobalt",
      role: "Logistics Release Point",
      coordinate: { latitude: 22.7, longitude: 120.4 },
      description: "Test handoff point."
    },
    {
      id: "hauler-position",
      name: "Hauler 8 Current Position",
      role: "Supply Convoy Position",
      coordinate: { latitude: 22.45, longitude: 120.32 },
      description: "Test convoy position."
    },
    {
      id: "raven-position",
      name: "Raven Assembly Area",
      role: "Supported Unit Position",
      coordinate: { latitude: 22.82, longitude: 120.62 },
      description: "Test supported unit position."
    }
  ],
  supported_units: [
    {
      id: "raven",
      callsign: "Raven",
      radio_callsign: "Raven 6",
      display_name: "Raven Company",
      echelon: "Company",
      location_id: "raven-position",
      mission: "Test mission",
      inventory: [
        {
          tracked_supply: "Test Fuel",
          class_of_supply: "Class III",
          quantity: 17,
          unit: "gal",
          status: "red",
          days_of_supply: 0.4,
          projected_black_time: "2026-05-17T06:00:00Z"
        }
      ]
    }
  ],
  supply_convoy: {
    id: "hauler-8",
    callsign: "Hauler 8",
    display_name: "Hauler 8 LOGPAC",
    location_id: "hauler-position",
    movement_status: "Proposed Movement Status",
    route_summary: "Test LSA Raven to Test LRP Cobalt",
    route_location_ids: ["test-lsa", "hauler-position", "test-lrp"],
    supply_load: [
      {
        tracked_supply: "Test Fuel",
        class_of_supply: "Class III",
        quantity: 300,
        unit: "gal",
        destination_unit_id: "raven"
      }
    ]
  }
};

describe("App", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders API readiness and scenario logistics picture returned by the backend", async () => {
    mockApiFetch();

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("API Ready")).toBeInTheDocument();
    });

    expect(globalThis.fetch).toHaveBeenCalledWith("http://localhost:8000/readyz");
    expect(globalThis.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/scenarios/kaohsiung-tainan/logistics-picture"
    );
    expect(screen.getByText("gallatin-radio-agent-api")).toBeInTheDocument();
    expect(screen.getByText("postgis")).toBeInTheDocument();
    expect(screen.getByText("POSTGIS='3.4.0'")).toBeInTheDocument();

    expect(screen.getByRole("heading", { name: "Test Corridor Logistics Picture" })).toBeInTheDocument();
    expect(screen.getByText("Test Corridor AO")).toBeInTheDocument();
    expect(screen.getByText("Test LSA Raven")).toBeInTheDocument();
    expect(screen.getByText("Test LRP Cobalt")).toBeInTheDocument();
    expect(screen.getAllByText("Raven")).not.toHaveLength(0);
    expect(screen.getAllByText("Hauler 8")).not.toHaveLength(0);
    expect(screen.getAllByText("Class III / Test Fuel")).toHaveLength(2);
    expect(screen.getByText("17 gal")).toBeInTheDocument();
    expect(screen.getByText("0.4 DOS")).toBeInTheDocument();
    expect(screen.getByText("Anvil 3 monitors TESTNET-7.")).toBeInTheDocument();
  });

  it("renders dependency failures from the readiness response", async () => {
    mockApiFetch({
      readiness: {
        service: "gallatin-radio-agent-api",
        status: "unavailable",
        dependencies: [
          {
            name: "postgis",
            status: "unavailable",
            details: "PostGIS readiness check failed: connection refused"
          }
        ]
      },
      readinessStatus: 503
    });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("API Unavailable")).toBeInTheDocument();
    });

    expect(screen.getByText("PostGIS readiness check failed: connection refused")).toBeInTheDocument();
    expect(screen.getByText("Test Corridor AO")).toBeInTheDocument();
  });

  it("renders scenario endpoint errors without falling back to fixed logistics entities", async () => {
    mockApiFetch({ scenarioStatus: 500 });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Logistics Picture Unavailable")).toBeInTheDocument();
    });

    expect(screen.getAllByText("Logistics Picture fetch failed with HTTP 500")).toHaveLength(2);
    expect(screen.queryByText("Test LSA Raven")).not.toBeInTheDocument();
    expect(screen.queryByText("Raven")).not.toBeInTheDocument();
  });
});

function mockApiFetch({
  readiness = readyResponse,
  readinessStatus = 200,
  scenario = scenarioResponse,
  scenarioStatus = 200
}: {
  readiness?: ReadinessResponse;
  readinessStatus?: number;
  scenario?: LogisticsPictureScenario;
  scenarioStatus?: number;
} = {}) {
  vi.spyOn(globalThis, "fetch").mockImplementation((input: RequestInfo | URL) => {
    const url = typeof input === "string" ? input : input instanceof URL ? input.href : input.url;

    if (url === "http://localhost:8000/readyz") {
      return Promise.resolve(jsonResponse(readiness, readinessStatus));
    }

    if (url === "http://localhost:8000/scenarios/kaohsiung-tainan/logistics-picture") {
      return Promise.resolve(jsonResponse(scenario, scenarioStatus));
    }

    return Promise.reject(new Error(`Unhandled fetch to ${url}`));
  });
}

function jsonResponse(body: unknown, status: number) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" }
  });
}
