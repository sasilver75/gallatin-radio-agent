# Agent Instructions

This repository is the Gallatin LCOP rebuild: a map-first Logistics Common Operating Picture for a Logistics Watch Officer.

Use the domain language in `CONTEXT.md`. Prefer established terms such as `Logistics Common Operating Picture`, `Logistics Watch Officer`, `Logistics Picture`, `Unit`, `Selected Unit`, `Reporting Unit`, `MGRS Grid Reference`, `Inventory Line`, `Tracked Supply`, `Class of Supply`, `BRAG Status`, `Forecast Horizon`, `Inventory Projection Matrix`, `Inventory Correction`, `Inventory Update`, `Inventory Addition`, `Inventory Removal`, `LOGSTAT`, `LOGSYNC Matrix`, `Movement`, `Movement Payload`, `Course of Action`, and `COA Regeneration`.

Use `docs/LCOP_PRD_DRAFT.md` for the current product requirements. If ADRs are added later, follow them unless a new ADR supersedes them.

## Current Product Direction

The active application is being built around the Logistics Watch Officer's job

Focus first on:

- Taiwan Scenario geography with fictional Unit disposition.
- `3rd Infantry Brigade Combat Team` as the default Selected Unit.
- Reporting Units including `HHC, 3IBCT`, `2-27 IN`, `2-35 IN`, `3-4 CAV`, `3-7 FA`, `325 BSB`, and `65 BEB`.
- Unit headers with Unit Display Name, Unit Short Label, MGRS Grid Reference, headcount, and Unit Tags.
- Map-first LCOP interaction where selecting map pins or Reporting Units changes the Selected Unit.
- Parent Unit sustainment summaries by Class of Supply Rollup.
- Reporting Unit inventory views by Inventory Line and Tracked Supply.
- Initial inventory scope limited to Class I, Class III, and Class V.
- On-Hand Inventory plus 24, 48, 72, and 96 hour Forecast Horizons.
- BRAG Status derived from quantities and Status Cutoffs, not manually entered colors.
- Inventory Updates that may batch multiple On-Hand Inventory Corrections and Inventory Removals.
- Add Items as the separate path for Inventory Additions.
- LOGSYNC Matrix planning by Movement Destination Unit and day.
- Movements with payloads made of Tracked Supplies and quantities.

Radio-derived workflows, Tactical Radio Audio, transcription, interpretation review, Outbound Audio, Denied Areas, Supply Convoys, and detailed COA workflows are deferred until the LCOP data and UI foundation is coherent.

## Engineering Expectations

Keep slices vertical and demoable:

- UI behavior should connect to API behavior.
- API behavior should use typed schemas and durable or fixture-backed state.
- Tests should prove the path is not hardcoded display-only markup.
- External services such as map tiles, routing, transcription, and TTS should have deterministic local/test fixtures where practical.

When pursuing tickets, follow red-green-refactor TDD loops where practical:

- Write one failing behavior test against a public interface before implementing the next slice.
- Implement the smallest vertical path that makes that test pass.
- Refactor only while the tests are green, then repeat with the next behavior.
- Prefer integration-style tests that use project domain language and survive internal refactors.
- If a spike or scaffolding step cannot reasonably start test-first, call that out explicitly and add behavior coverage before the work is ready for review.

Preserve human authority boundaries. The application may summarize, project, and propose; consequential operational state changes should flow through accepted events or explicit Logistics Watch Officer actions.

## Frontend Direction

The map is the primary workspace. Side panels should support map-centered sustainment work rather than becoming a generic dashboard.

For UI work:

- Treat the Selected Unit as the driver of the left information panel and map focus.
- Keep operator-facing inventory displays dense, scannable, and work-focused.
- Use BRAG colors carefully as status semantics, not decoration.
- Make On-Hand Inventory visibly distinct from projected Forecast Horizons when editing.
- Do not add landing-page or marketing-style UI.

## Local Development

Application code has been removed during the LCOP reorientation. Add accurate install, run, and verification commands here when the new app scaffold is created.
