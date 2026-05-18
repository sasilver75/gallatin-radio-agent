# LCOP PRD Draft

Status: living PRD draft produced from product discovery using the `$to-prd` structure. This document captures functionality and implementation direction. `CONTEXT.md` remains the home for settled language and domain relationships.

## Problem Statement

Logistics Watch Officers need a credible Logistics Common Operating Picture that makes sustainment risk legible from a map-first workspace. Their job is not primarily to operate a radio agent or read AI output; their job is to maintain the Logistics Picture, understand which Units are at sustainment risk, and coordinate resupply activity quickly enough to matter.

The previous prototype taught useful domain lessons, but it started from an input surface. The rebuilt product needs to start from the Logistics Watch Officer's workflow: select Units, inspect inventory posture, understand projected shortages, correct trusted current inventory, and coordinate Movements through the LOGSYNC Matrix.

## Solution

Build a map-first Logistics Common Operating Picture centered on Units, Reporting Units, inventory projections, BRAG Status, and LOGSYNC Movements.

The initial application opens on `3rd Infantry Brigade Combat Team` in a Taiwan Scenario with fictional Unit disposition. The Logistics Watch Officer can select subordinate Reporting Units from map pins or the Unit Summary Pane, inspect item-level inventory in a Detail Pane, correct On-Hand Inventory, add and remove Inventory Lines, and see projections and Class of Supply Rollups update. The LOGSYNC Matrix organizes resupply Movements by Movement Destination Unit and day, with compact cards for status, time window, vehicle/personnel counts, and Movement Class Rollup.

The v1 model should be deliberately simple but coherent:

- Inventory is tracked for Class I, Class III, and Class V.
- Inventory projections use On-Hand Inventory, integer Burn Rate per 24 hours, and standard Forecast Horizons.
- BRAG Status is derived from Supply Percentage against a positive Requirement Baseline.
- Requirement Baseline and Burn Rate are stored per Unit and Tracked Supply.
- Add Items uses an existing Supply Catalog and creates active Inventory Lines.
- Edit mode batches On-Hand Inventory Corrections and Inventory Removals.
- LOGSYNC cards summarize Movement Payloads, but the payload itself is Tracked Supplies and quantities.

## User Stories

1. As a Logistics Watch Officer, I want the LCOP to open on `3rd Infantry Brigade Combat Team`, so that I start from the brigade-level logistics picture.
2. As a Logistics Watch Officer, I want the scenario to use Taiwan geography with fictional Unit disposition, so that the product is grounded in real terrain without copying the reference demo scenario.
3. As a Logistics Watch Officer, I want to see Units on a real base map, so that logistics status is tied to geography.
4. As a Logistics Watch Officer, I want map pins to show compact Unit identity, so that I can understand the operating picture without opening every Unit.
5. As a Logistics Watch Officer, I want selecting a map pin to change the Selected Unit, so that the Unit Summary Pane and map focus follow my selection.
6. As a Logistics Watch Officer, I want the Unit Summary Pane to show Unit Display Name, MGRS Grid Reference, headcount, and Unit Tags, so that I can identify the selected Unit quickly.
7. As a Logistics Watch Officer, I want the parent Unit overview to show Reporting Units, so that I can inspect subordinate sustainment posture from the brigade view.
8. As a Logistics Watch Officer, I want clicking a Reporting Unit in the Unit Summary Pane to select that Reporting Unit, so that I can move from brigade-level view to unit-level detail.
9. As a Logistics Watch Officer, I want selecting a Reporting Unit to preserve Parent Unit Context, so that I can return to the parent Unit predictably.
10. As a Logistics Watch Officer, I want Parent Unit Navigation in the Detail Pane, so that returning to the immediate parent Unit is distinct from browser-like history.
11. As a Logistics Watch Officer, I want the Unit Summary Pane to remain a stable description of the Selected Unit, so that detailed workflows do not overload the sidebar.
12. As a Logistics Watch Officer, I want Detail Panes for detailed workflows, so that Inventory and LOGSYNC work have enough room for dense operational data.
13. As a Logistics Watch Officer, I want parent Unit inventory summarized by Class of Supply Rollup, so that I can scan subordinate sustainment risk quickly.
14. As a Logistics Watch Officer, I want Class of Supply Rollups to use the worst underlying BRAG Status, so that a single critical item is not hidden by healthier supplies.
15. As a Logistics Watch Officer, I want Reporting Unit inventory shown by Inventory Line, so that I can see the specific Tracked Supplies causing sustainment risk.
16. As a Logistics Watch Officer, I want each Inventory Line to show its Class of Supply and Unit of Issue, so that item quantities are interpretable.
17. As a Logistics Watch Officer, I want inventory quantities shown for On-Hand Inventory and +24/+48/+72/+96 hours, so that I can see current and projected sustainment posture.
18. As a Logistics Watch Officer, I want projected inventory cells to be read-only, so that projections remain system-derived rather than manually colored or overwritten.
19. As a Logistics Watch Officer, I want displayed projected inventory to floor at zero, so that the matrix does not show confusing negative quantities.
20. As a Logistics Watch Officer, I want BRAG colors derived from backing quantities, so that status colors remain explainable.
21. As a Logistics Watch Officer, I want BRAG Status to derive from Supply Percentage, so that raw quantities are normalized against what that Unit is expected to maintain.
22. As a Logistics Watch Officer, I want v1 Default BRAG Bands, so that the product has predictable status semantics before doctrine-grade configuration exists.
23. As a Logistics Watch Officer, I want active Inventory Lines to require a positive Requirement Baseline, so that BRAG math is well-defined.
24. As a Logistics Watch Officer, I want Burn Rate expressed as an integer quantity per 24 hours, so that v1 projections are simple and legible.
25. As a Logistics Watch Officer, I want Edit mode to make only On-Hand Inventory editable, so that corrections represent trusted current state.
26. As a Logistics Watch Officer, I want On-Hand Inventory Corrections not to change Burn Rate, so that current quantity updates do not silently alter consumption assumptions.
27. As a Logistics Watch Officer, I want to stage multiple On-Hand Inventory Corrections before saving, so that I can submit one coherent Inventory Update.
28. As a Logistics Watch Officer, I want Cancel to discard staged inventory edits, so that I can back out of mistakes before changing the Logistics Picture.
29. As a Logistics Watch Officer, I want Save to submit a batch Inventory Update, so that multiple corrections and removals are applied together.
30. As a Logistics Watch Officer, I want saving Inventory Corrections to recalculate projections and BRAG Status, so that the Logistics Picture reflects trusted current state.
31. As a Logistics Watch Officer, I want to remove an Inventory Line in Edit mode, so that inactive supplies no longer appear in the active matrix.
32. As a Logistics Watch Officer, I want removed Inventory Lines to stop contributing to active Class of Supply Rollups, so that parent summaries reflect current tracked inventory.
33. As a Logistics Watch Officer, I want Add Items to be separate from Edit, so that creating an Inventory Line is distinct from correcting or removing existing lines.
34. As a Logistics Watch Officer, I want Add Items to select from an existing Supply Catalog, so that Unit inventory uses known Tracked Supplies.
35. As a Logistics Watch Officer, I want Add Items to require On-Hand Inventory, Requirement Baseline, and Burn Rate, so that new Inventory Lines can immediately project status.
36. As a Logistics Watch Officer, I want the LOGSYNC Matrix to open from the parent Unit overview, so that resupply planning is scoped to the selected parent Unit.
37. As a Logistics Watch Officer, I want LOGSYNC rows to represent Movement Destination Units, so that the grid is organized by who is being supplied.
38. As a Logistics Watch Officer, I want LOGSYNC columns to represent days in a horizontally scrollable planning window, so that I can review several days of sustainment activity.
39. As a Logistics Watch Officer, I want Daily Movement Capacity visible per day, so that I can see scheduling constraints such as `Max 3`.
40. As a Logistics Watch Officer, I want Movement cards to show Movement Status, so that I can distinguish Proposed Movements from In-Progress Movements.
41. As a Logistics Watch Officer, I want Movement cards to show Movement Window, so that I can understand when each Movement is scheduled.
42. As a Logistics Watch Officer, I want Movement cards to show vehicle and personnel counts, so that I can estimate movement scale quickly.
43. As a Logistics Watch Officer, I want Movement cards to show a Movement Class Rollup, so that I can scan whether a Movement carries Class I, III, V, or some combination.
44. As a Logistics Watch Officer, I want Movement Payloads to contain Tracked Supplies and quantities, so that opening a Movement can show what is actually being moved.
45. As a Logistics Watch Officer, I want Movement Class Rollup derived from Movement Payload, so that compact card labels stay consistent with actual contents.
46. As a Logistics Watch Officer, I want Movement Destination Unit to be distinct from movement executor or convoy owner, so that the LOGSYNC row semantics remain clear.
47. As a Logistics Watch Officer, I want List/Grid/Filter controls visible on the LOGSYNC Matrix, so that the product can grow into alternate views without changing the core planning model.

## Implementation Decisions

### Product Boundary

- The product is an LCOP for the Logistics Watch Officer, not a radio-agent-first experience.
- `CONTEXT.md` is the source of truth for settled language and domain relationships.
- This PRD is the source of truth for desired functionality, workflows, user stories, and implementation direction.
- Application code has been removed during reorientation; the next implementation should start from this product model rather than reviving the old direct radio-agent prototype.

### Scenario And Unit Model

- The initial scenario uses Taiwan geography with fictional Unit disposition.
- `3rd Infantry Brigade Combat Team` is the default Selected Unit.
- Initial Reporting Units are `HHC, 3IBCT`, `2-27 IN`, `2-35 IN`, `3-4 CAV`, `3-7 FA`, `325 BSB`, and `65 BEB`.
- A Unit should have Unit Display Name, optional Unit Short Label, MGRS Grid Reference, headcount, and Unit Tags.
- Reporting Units contribute logistics status to a parent Unit and may become the Selected Unit.
- Parent Unit Context should be retained when a subordinate Reporting Unit is selected from the parent view.

### Product Surfaces

- The map is the primary workspace.
- The Unit Summary Pane is persistent and describes the Selected Unit.
- Detail Panes are expanded working surfaces opened from Unit Summary Pane sections.
- Parent Unit Navigation belongs in the Detail Pane when a subordinate Selected Unit has Parent Unit Context.
- Returning through Parent Unit Navigation returns to the immediate parent Unit, not arbitrary prior history.

### Inventory Model

- Initial supply scope is Class I, Class III, and Class V.
- A Supply Catalog contains known Tracked Supplies.
- An Inventory Line represents one Tracked Supply in one Unit's active Inventory.
- Active Inventory Lines require a positive Requirement Baseline in v1.
- Requirement Baseline is stored per Unit and Tracked Supply.
- Burn Rate is stored per Unit and Tracked Supply.
- Burn Rate is an integer quantity consumed per 24 hours in the Tracked Supply item's Unit of Issue.
- On-Hand Inventory, Requirement Baseline, Burn Rate, and displayed Projected Inventory are integer quantities for v1.
- Quantities use the Tracked Supply item's Unit of Issue.

### Projection Engine

The projection engine is a deep module candidate. It should expose a small interface that accepts On-Hand Inventory, Burn Rate, and Forecast Horizon, and returns displayed projected quantities.

V1 projection rule:

```text
projected_quantity = max(0, on_hand_quantity - burn_rate_per_24h * horizon_days)
```

The standard Forecast Horizons are 24, 48, 72, and 96 hours.

### BRAG Engine

The BRAG engine is a deep module candidate. It should expose a small interface that accepts displayed inventory quantity and Requirement Baseline, then returns BRAG Status.

V1 Supply Percentage rule:

```text
supply_percentage = displayed_inventory_quantity / requirement_baseline
```

Default BRAG Bands:

- Green: `>= 80%`
- Amber: `50% to < 80%`
- Red: `30% to < 50%`
- Black: `< 30%`

These are product defaults, not authoritative doctrine.

### Rollup Engine

The Class of Supply Rollup engine is a deep module candidate. It should compute the most constrained BRAG Status among active Inventory Lines for a given Unit, Class of Supply, and inventory point.

- Parent Unit views summarize subordinate Reporting Unit status by Class of Supply.
- A Class of Supply Rollup uses the worst BRAG Status among the underlying active Inventory Lines for the same Forecast Horizon.
- Removed Inventory Lines do not contribute to active rollups.

### Inventory Update Workflow

- The Edit action handles Inventory Corrections and Inventory Removals.
- Edit mode makes On-Hand Inventory editable and keeps projected horizon cells read-only.
- Edit mode can stage multiple changes.
- Save submits one Inventory Update containing staged corrections and removals.
- Cancel discards staged changes.
- Inventory Corrections directly adjust On-Hand Inventory.
- Inventory Corrections do not change Burn Rate.
- Inventory Corrections trigger recalculation of Projected Inventory and BRAG Status.
- Inventory Removals remove Inventory Lines from active Inventory displays and rollups.

### Inventory Addition Workflow

- Add Items is separate from Edit.
- Add Items selects an existing Tracked Supply from the Supply Catalog.
- Add Items creates a new active Inventory Line for the selected Unit.
- Add Items requires On-Hand Inventory, Requirement Baseline, and Burn Rate.
- Add Items does not create new Supply Catalog entries in v1.

### LOGSYNC Matrix Model

- LOGSYNC Matrix is a Detail Pane opened from a parent Unit Summary Pane.
- LOGSYNC Matrix organizes Movements by Movement Destination Unit and day.
- Grid view is the default observed view.
- List view and Filters are visible controls but can be deferred until their behavior is understood.
- Daily Movement Capacity is shown per day and constrains Movements scheduled across the selected parent Unit on that day.
- The row Unit is the Movement Destination Unit, not the executor or convoy owner.

### Movement Model

- A Movement is planned or executed for a Unit over a scheduled Movement Window.
- Initial observed Movement Status values are Proposed and In Progress.
- A Movement has a Movement Destination Unit.
- A Movement has a Movement Payload.
- A Movement may display vehicle count and personnel count.
- Movement Payload contains Tracked Supplies and quantities.
- Movement Class Rollup is derived from Movement Payload and displayed on compact LOGSYNC cards.

### Interfaces To Expect

Do not treat these as final API names. They describe public behavior the implementation should support:

- Read the current Logistics Picture for the initial scenario.
- Select a Unit and retrieve Unit Summary Pane data.
- Retrieve Inventory Projection Matrix data for a selected Reporting Unit.
- Submit an Inventory Update containing corrections and removals.
- Submit an Inventory Addition for a selected Unit.
- Retrieve parent Unit Class of Supply Rollups.
- Retrieve LOGSYNC Matrix data for a selected parent Unit.
- Retrieve Movement detail, including Movement Payload.

## Testing Decisions

Good tests should verify behavior through public interfaces and product language. Avoid tests that only prove display markup is hardcoded.

### Deep Module Tests

- Projection engine: given On-Hand Inventory and Burn Rate, returns integer projected quantities for 24, 48, 72, and 96 hours with display floor at zero.
- BRAG engine: given displayed quantity and positive Requirement Baseline, returns Green, Amber, Red, or Black according to Default BRAG Bands.
- Class of Supply Rollup engine: given multiple active Inventory Lines, returns the most constrained BRAG Status for each Forecast Horizon.
- Movement Class Rollup engine: given Movement Payload, returns the Classes of Supply represented in that payload.

### Workflow Tests

- Selecting a Reporting Unit updates Selected Unit and preserves Parent Unit Context.
- Parent Unit Navigation returns from a subordinate Selected Unit to the immediate parent Unit.
- Inventory Update can batch multiple On-Hand Inventory Corrections.
- Inventory Update can batch corrections and Inventory Removals together.
- Inventory Correction recalculates Projected Inventory and BRAG Status without changing Burn Rate.
- Inventory Removal removes an Inventory Line from active matrix displays and Class of Supply Rollups.
- Inventory Addition requires Tracked Supply, On-Hand Inventory, Requirement Baseline, and Burn Rate.
- Inventory Addition selects from the Supply Catalog rather than creating a new Tracked Supply.
- LOGSYNC rows represent Movement Destination Units.
- Daily Movement Capacity is shown for LOGSYNC days.
- Compact Movement cards derive Movement Class Rollup from Movement Payload.

### UI Behavior Tests

- Default application state opens on `3rd Infantry Brigade Combat Team`.
- Selecting a map pin updates the Unit Summary Pane.
- Selecting a Reporting Unit from the parent pane updates the Unit Summary Pane and map focus.
- Opening Inventory from the Unit Summary Pane displays the Detail Pane.
- In Inventory edit mode, On-Hand cells are editable and forecast cells are read-only.
- Save applies staged inventory edits; Cancel discards them.
- Opening LOGSYNC Matrix displays rows by Movement Destination Unit and columns by day.

## Out of Scope

- Radio-derived state updates.
- Tactical Radio Audio.
- Transcription and interpretation review.
- Outbound Audio.
- Denied Areas.
- Supply Convoys as separate map entities.
- Mission-specific demand modeling.
- Deriving Requirement Baseline from headcount, equipment, mission profile, weather, or operational tempo.
- Creating new Supply Catalog entries through Add Items.
- Full audit trail for all inventory mutations.
- Doctrine-grade configurable BRAG thresholds.
- Detailed Course of Action workflows.
- Movement completion effects on inventory until the Movement detail and execution lifecycle are understood.
- List view behavior for LOGSYNC until later slices clarify it.
- Filter behavior for LOGSYNC until later slices clarify it.

## Further Notes

### Artifact Split

- `CONTEXT.md` should remain concise and glossary-like.
- This PRD should capture behavior, workflows, product requirements, testing expectations, and open questions.
- If a future decision is hard to reverse, surprising without context, and based on a real tradeoff, it should become an ADR.

### Demo Slices Captured

- Default 3rd Infantry Brigade Combat Team overview.
- Selecting a Reporting Unit such as 3-4 CAV.
- Expanded Unit Inventory table grouped by Class of Supply.
- Edit mode for On-Hand Inventory Corrections and Inventory Removals.
- Add Items as a separate Inventory Addition path.
- Parent Unit Navigation from a subordinate Detail Pane.
- LOGSYNC Matrix grid view with Movement cards by destination Unit and day.

### Open Questions

- Should Movement Payload quantities use the same Unit of Issue as Inventory Lines?
- What details appear when the officer opens a Movement card?
- What does New Movement Group mean, and how does it differ from New Movement?
- Are Movement statuses limited to Proposed and In Progress for v1, or do we need Scheduled, Completed, Cancelled, Failed, or Completed?
- Should Daily Movement Capacity apply to all Movements across the parent Unit, or only to a subset such as vehicle movements?
- How should Movement completion affect On-Hand Inventory at the Movement Destination Unit?
- How should LOGSYNC interact with Course of Action generation?
- Which app scaffold and stack should be used for the rebuild now that the prior code has been removed?
