# API

FastAPI backend for health/readiness, tactical audio ingestion, transcription, interpretation, event persistence, projections, routing, COA generation, and outbound audio.

## Local Endpoints

- `GET /healthz`: process-level liveness.
- `GET /readyz`: dependency readiness. This checks PostGIS with `postgis_full_version()` and returns `503` when the spatial database is unavailable.
- `GET /scenarios/kaohsiung-tainan/playback`: deterministic Scenario Playback timeline used by the web demo run control.

Run API tests from the repository root:

```sh
uv run pytest
```
