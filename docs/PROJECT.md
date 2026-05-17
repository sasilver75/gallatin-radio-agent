# Project Contract

## Product Goal

Build a credible interview demo for Gallatin: a map-first logistics decision-support app where tactical radio traffic updates a sustainment picture and helps a Logistics Watch Officer approve executable resupply actions.

## App Boundary

The app owns:

- Scenario data and playback.
- Tactical radio audio ingestion.
- Transcript evidence.
- Interpretation and review workflows.
- Event Ledger and Logistics Picture projection.
- Denied areas and route variants.
- Inventory projections and status bands.
- Executable COAs and approval/rejection.
- Grounded Quarterback rollups and outbound audio.

## First Demo Thread

The initial implementation thread is the Linear chain `SAM-77` through `SAM-89`. The intended shape is a set of thin vertical slices that starts with a runnable local workspace and ends with scripted scenario playback.
