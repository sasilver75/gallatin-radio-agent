# Agent Instructions

This repository is the Gallatin Radio Agent demo app.

Use the domain language in `CONTEXT.md`. Prefer established terms such as `Tactical Radio Audio`, `Logistics Picture`, `Event Ledger`, `Proposed Interpretation`, `Denied Area`, `Route Variant`, `Executable Course of Action`, `COA Approval`, and `Outbound Audio`.

Follow the ADRs in `docs/adr` unless a new ADR supersedes them.

Keep slices vertical and demoable:

- UI behavior should connect to API behavior.
- API behavior should use typed schemas and durable or fixture-backed state.
- Tests should prove the path is not hardcoded display-only markup.
- External services such as transcription, TTS, OpenRouteService, and map tiles should have deterministic local/test fixtures where practical.

Preserve human authority boundaries. Quarterback may propose, summarize, and draft; consequential operational state changes should flow through accepted events or explicit operator actions.
