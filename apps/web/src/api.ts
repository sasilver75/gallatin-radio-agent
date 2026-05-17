export type DependencyStatus = {
  name: string;
  status: "ready" | "unavailable";
  details: string;
};

export type ReadinessResponse = {
  service: string;
  status: "ready" | "unavailable";
  dependencies: DependencyStatus[];
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function fetchReadiness(): Promise<ReadinessResponse> {
  const response = await fetch(`${API_BASE_URL}/readyz`);
  const body = (await response.json()) as ReadinessResponse;

  if (!response.ok && body.status !== "unavailable") {
    throw new Error(`Readiness check failed with HTTP ${response.status}`);
  }

  return body;
}
