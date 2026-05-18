# Gallatin LCOP

Gallatin LCOP is a rebuilt Logistics Common Operating Picture for a Logistics Watch Officer.

The product direction is a map-first sustainment workspace: the officer starts from a real geographic operating picture, selects Units, inspects their logistics posture, sees inventory risk across time, and updates trusted logistics state through explicit operator actions.

## Product Focus

The application should make the Logistics Picture legible first. The map is the primary workspace; side panels exist to explain the selected Unit, its Reporting Units, and its sustainment risk.

Current product foundation:

- `3rd Infantry Brigade Combat Team` is the default Selected Unit.
- The scenario uses Taiwan geography with fictional Unit disposition.
- Units carry display names, short labels, MGRS Grid References, headcount, and Unit Tags.
- Reporting Units can be selected from the map or from the parent Unit panel.
- Parent Unit views summarize subordinate sustainment by Class of Supply Rollup.
- Reporting Unit views show item-level Inventory Lines.
- Initial supply scope is Class I, Class III, and Class V.
- Inventory displays On-Hand Inventory plus 24, 48, 72, and 96 hour Forecast Horizons.
- BRAG Status is derived from quantities and Status Cutoffs.
- Inventory Updates can batch multiple On-Hand Inventory Corrections and Inventory Removals.
- Add Items is the separate path for Inventory Additions.

## Design Principles

- Build around the Logistics Watch Officer's job, not a generic dashboard.
- Keep the Logistics Common Operating Picture map-first.
- Treat `CONTEXT.md` as the source of truth for domain language.
- Preserve human authority: consequential logistics state changes should flow through explicit operator actions.
- Prefer vertical slices where UI behavior, API behavior, typed schemas, and fixture-backed state move together.
- Use the Gallatin Navigator reference to learn interaction patterns, but do not copy its scenario wholesale.

## Current Repository Shape

This repository is currently a planning and domain-foundation workspace. Application code has been removed while the product is reoriented around the Logistics Common Operating Picture.

Important files:

- `CONTEXT.md`: canonical domain glossary and relationships.
- `docs/LCOP_PRD_DRAFT.md`: living product requirements draft from the demo walkthrough and grilling sessions.
- `AGENTS.md`: instructions for coding agents working in this repository.
- `GALLATIN_CONTEXT.md`: public Gallatin AI product and company context.
- `GALLATIN_DEMO_TRANSCRIPT.md`: reference transcript from the Gallatin Navigator demo.
- `explainers/military-logistics-for-gallatin.md`: practical logistics background for the product.

## Next Build Direction

The next implementation should begin with the LCOP foundation:

1. Unit and Reporting Unit data model.
2. Taiwan map base layer with fictional Unit positions.
3. Selected Unit interaction from map pins and Reporting Unit lists.
4. Parent Unit Class of Supply Rollups.
5. Reporting Unit Inventory Projection Matrix.
6. Inventory edit flow for On-Hand corrections and removals.
7. Add Items flow for new Inventory Lines.

Once those foundations are credible, LOGSYNC and Course of Action workflows can be designed from the same Logistics Picture.
