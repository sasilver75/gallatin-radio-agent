# Agent Instructions

This repository is the Gallatin Radio Agent demo app.

Use the domain language in `CONTEXT.md`. Prefer established terms such as `Tactical Radio Audio`, `Logistics Picture`, `Event Ledger`, `Proposed Interpretation`, `Denied Area`, `Route Variant`, `Executable Course of Action`, `COA Approval`, and `Outbound Audio`.

Follow the ADRs in `docs/adr` unless a new ADR supersedes them.

Keep slices vertical and demoable:

- UI behavior should connect to API behavior.
- API behavior should use typed schemas and durable or fixture-backed state.
- Tests should prove the path is not hardcoded display-only markup.
- External services such as transcription, TTS, OpenRouteService, and map tiles should have deterministic local/test fixtures where practical.

When pursuing tickets, follow red-green-refactor TDD loops where practical:

- Write one failing behavior test against a public interface before implementing the next slice.
- Implement the smallest vertical path that makes that test pass.
- Refactor only while the tests are green, then repeat with the next behavior.
- Prefer integration-style tests that use project domain language and survive internal refactors.
- If a spike or scaffolding step cannot reasonably start test-first, call that out explicitly and add behavior coverage before the work is ready for review.

Preserve human authority boundaries. Quarterback may propose, summarize, and draft; consequential operational state changes should flow through accepted events or explicit operator actions.
