# Gallatin Radio Agent

Interview demo application: Tactical Radio Audio becomes a logistics common operating picture, event ledger, denied areas, route variants, inventory projections, executable COAs, operator approvals, grounded rollups, and outbound radio audio.

## Repository Boundary

This repository is for the Gallatin Radio Agent demo app.

It should contain:

- Product context, domain glossary, ADRs, and scenario data.
- The React/TypeScript operator UI under `apps/web`.
- The FastAPI backend under `apps/api`.
- Shared schema artifacts under `packages/schemas`.
- Local app infrastructure under `infra`.

## Linear

Project: Gallatin Radio Agent

Initial ticket chain:

- `SAM-77` Bootstrap Local Quarterback Workspace
- `SAM-78` Render Seed Kaohsiung-Tainan Logistics Common Operating Picture
- `SAM-79` Persist Event Ledger and Project Accepted Domain Events
- `SAM-80` Ingest Prerecorded Radio Clips Through Transcription Pipeline
- `SAM-81` Interpret Radio Into Position Updates and Supply Signals
- `SAM-82` Review Hazard Observations and Create Denied Areas
- `SAM-83` Generate ORS Route Variants Around Denied Areas
- `SAM-84` Show Inventory Projections, Days of Supply, and Burn Rate Changes
- `SAM-85` Regenerate Executable COAs From Accepted Operational Changes
- `SAM-86` Approve or Reject Executable COAs Deterministically
- `SAM-87` Answer Addressed Intents With Quarterback Radio Rollups
- `SAM-88` Generate Quarterback Outbound Audio for Rollups and Approved Instructions
- `SAM-89` Assemble Demo Scenario Playback

## Current Contents

- `CONTEXT.md`: domain glossary and naming rules for the Radio-to-Map Logistics Agent.
- `GALLATIN_CONTEXT.md`: Gallatin company/product research context.
- `docs/adr`: early architecture decisions.
- `docs/GALLATIN_ML_INTERVIEW_PREP.md`: interview prep and data/ML framing.
- `explainers/military-logistics-for-gallatin.md`: domain explainer.
- `artifacts/transcripts`: captured audio/transcript material for demo exploration.

The copied WAV artifact is intentionally ignored by Git because it is large. Use Git LFS, a smaller fixture, or a documented download/regeneration step before relying on audio assets in CI or hosted demos.

## Local Development

Prerequisites:

- Docker with Compose.
- Node.js 24+ and npm.
- Python 3.12+ with `uv`.

Install dependencies:

```sh
npm install
uv sync --dev
```

Start the local Quarterback workspace:

```sh
npm run dev
```

The command starts PostGIS, the FastAPI backend, and the React web shell.

- Web: http://localhost:5173
- API health: http://localhost:8000/healthz
- API readiness: http://localhost:8000/readyz
- PostGIS: `localhost:55432`, database/user/password `quarterback`

Copy `.env.example` to `.env` if you need to override local defaults.

Run focused verification:

```sh
npm test
```

## Intended Stack

See `docs/adr/0003-fastapi-react-postgis-stack.md`.

- React/TypeScript frontend.
- Python FastAPI backend.
- Postgres/PostGIS persistence.
- MapLibre map rendering.
- OpenRouteService routing with deterministic fixtures for local tests.
