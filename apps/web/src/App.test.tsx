import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";

describe("App", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders API readiness returned by the backend", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          service: "gallatin-radio-agent-api",
          status: "ready",
          dependencies: [
            {
              name: "postgis",
              status: "ready",
              details: "POSTGIS='3.4.0'"
            }
          ]
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      )
    );

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("API Ready")).toBeInTheDocument();
    });

    expect(globalThis.fetch).toHaveBeenCalledWith("http://localhost:8000/readyz");
    expect(screen.getByText("gallatin-radio-agent-api")).toBeInTheDocument();
    expect(screen.getByText("postgis")).toBeInTheDocument();
    expect(screen.getAllByText("ready")).toHaveLength(2);
    expect(screen.getByText("POSTGIS='3.4.0'")).toBeInTheDocument();
  });

  it("renders dependency failures from the readiness response", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          service: "gallatin-radio-agent-api",
          status: "unavailable",
          dependencies: [
            {
              name: "postgis",
              status: "unavailable",
              details: "PostGIS readiness check failed: connection refused"
            }
          ]
        }),
        { status: 503, headers: { "Content-Type": "application/json" } }
      )
    );

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("API Unavailable")).toBeInTheDocument();
    });

    expect(screen.getByText("PostGIS readiness check failed: connection refused")).toBeInTheDocument();
  });
});
