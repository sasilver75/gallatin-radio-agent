# Radio-to-Map Logistics Agent

This context defines the domain language for a Gallatin-inspired demo that turns tactical radio audio into geospatial logistics state and recommended sustainment actions.

## Language

**Radio-to-Map Logistics Agent**:
An agentic system that converts tactical radio audio into a maintained logistics picture and recommended actions.
_Avoid_: Radio agent, map agent, audio dashboard

**Agent Callsign**:
The radio-net identity used by the Radio-to-Map Logistics Agent when acknowledging requests or responding with summaries and recommendations.
_Avoid_: Bot name, assistant name, username

**Passive Monitoring**:
The agent behavior of listening to radio traffic and updating the Logistics Picture without transmitting on the radio net.
_Avoid_: Background mode, silent mode

**Addressed Response**:
An agent transmission made only after a human participant calls the Agent Callsign or asks the agent for information.
_Avoid_: Auto-response, proactive broadcast

**Tactical Radio Audio**:
Spoken field communications from live or prerecorded radio-like audio that may contain logistics-relevant facts.
_Avoid_: Transcript, message, clip when referring to the source audio itself

**Prerecorded Radio Clip**:
A saved Tactical Radio Audio file used to drive a repeatable demo through the same transcription path as live audio.
_Avoid_: Scripted transcript, canned event

**Transcription Pipeline**:
The shared process that converts Tactical Radio Audio into text for interpretation, regardless of whether the source is live or prerecorded.
_Avoid_: Hardcoded transcript, audio mock

**Radio Channel**:
A named source lane for Tactical Radio Audio in the Live Radio View.
_Avoid_: Net, stream

**LOGNET-1**:
The single Radio Channel used for v1 tactical logistics traffic.
_Avoid_: HANDHELD-1, command net

**Field Radio Console**:
The walkie-talkie simulator for transmitting Tactical Radio Audio as a selected callsign.
_Avoid_: Convoy UI, field dashboard

**Logistics Picture**:
The system's current representation of units, routes, supplies, hazards, and events relevant to sustainment decisions.
_Avoid_: Reality, database, backend state

**Logistics Common Operating Picture**:
The shared map-first view of sustainment state across units, supplies, movements, routes, and hazards.
_Avoid_: Dashboard, map when referring to the full sustainment picture

**Event Ledger**:
The append-only record of interpreted observations, reports, and decisions that explain how the Logistics Picture was derived.
_Avoid_: Activity log, audit log, map history

**Radio Transmission**:
An observed radio communication preserved as evidence before interpretation.
_Avoid_: Message, report when referring to the raw communication

**Semantic Output**:
The structured meaning produced from a Radio Transmission after transcription and interpretation.
_Avoid_: Parsed text, extracted data

**Domain Event**:
A Semantic Output that describes or changes the operational world.
_Avoid_: Intent, UI action

**Interaction Intent**:
A Semantic Output that asks Quarterback to respond or perform an interaction without directly changing the operational world.
_Avoid_: Domain event, command when it is just a request for response

**Addressed Intent**:
An Interaction Intent directed at Quarterback by callsign.
_Avoid_: Addressed query, radio event

**Operator Action**:
A Logistics Watch Officer action taken through the Supply Officer View.
_Avoid_: Radio event, agent action

**COA Approval**:
An Operator Action that accepts an Executable Course of Action for execution.
_Avoid_: Route approval when the whole plan is accepted

**COA Feedback**:
An Operator Action that asks for revision to an Executable Course of Action without approving it.
_Avoid_: v1 workflow

**COA Rejection**:
An Operator Action that declines an Executable Course of Action.
_Avoid_: Feedback when the plan should not be pursued

**COA Application**:
The deterministic workflow that applies an approved Executable Course of Action to the Logistics Picture.
_Avoid_: Quarterback applying state, agent mutation

**Draft Transmission**:
A proposed radio instruction or response generated from approved state for Hammer 4 to send through Quarterback.
_Avoid_: Autonomous tasking, agent order

**Outbound Audio**:
Audio spoken by Quarterback for an Addressed Response or approved Draft Transmission.
_Avoid_: Silent text response

**Radio Brevity**:
The constraint that Quarterback transmissions should be short radio-appropriate summaries or instructions, not full COA narration.
_Avoid_: Reading the full plan over the radio

**Position Update**:
A Domain Event that updates the known position of a unit, convoy, or other tracked entity.
_Avoid_: Location report

**Proposed Interpretation**:
An agent-derived meaning of a Radio Transmission that has not yet been accepted into the Logistics Picture.
_Avoid_: Supposition, guess

**Auto-Accepted Interpretation**:
A low-risk Proposed Interpretation accepted without Logistics Watch Officer review.
_Avoid_: Unreviewed change

**Review-Required Interpretation**:
A Proposed Interpretation that must be accepted, edited, or rejected by the Logistics Watch Officer before it affects consequential operational state.
_Avoid_: Flagged item, uncertain event

**Rejected Interpretation**:
A Proposed Interpretation the Logistics Watch Officer decides should not affect the Logistics Picture.
_Avoid_: Deleted event, ignored report

**Interpretation Judge**:
An agent role that decides whether a Proposed Interpretation can be auto-accepted or requires review.
_Avoid_: Confidence scorer, approval bot

**Agentic Boundary**:
The rule that only tasks requiring language judgment, ambiguity handling, or user-facing reasoning should be implemented as agents.
_Avoid_: Agent for everything, persistent agent swarm

**Review Trigger**:
A scenario guideline the Interpretation Judge uses when deciding whether a Proposed Interpretation requires Logistics Watch Officer review.
_Avoid_: Hard rule, policy

**Interpreted Report**:
A structured event derived from Tactical Radio Audio that preserves the reported fact, source, timing, and evidence.
_Avoid_: Extracted data, parsed message

**Supported Unit**:
A field unit whose supply status, location, or mission creates sustainment demand.
_Avoid_: Customer, requester, receiver

**Logistics Watch Officer**:
The coordination user responsible for maintaining the Logistics Picture and deciding how new reports affect the resupply plan.
_Avoid_: Dispatcher, commander, radio operator

**Supply Convoy**:
The execution element that moves supplies to Supported Units along assigned routes.
_Avoid_: Truck, delivery, asset

**Supply Load**:
The supplies currently carried by a Supply Convoy.
_Avoid_: Cargo, payload, inventory when referring to convoy-carried supplies

**Inventory**:
The quantity of Tracked Supplies held at a location, carried by a LOGPAC, or reported by a Supported Unit.
_Avoid_: Stocks, stockpile

**LOGPAC**:
A logistics package: a planned resupply package and convoy organized to replenish supported units.
_Avoid_: Resupply plan when referring to the package/convoy itself

**Resupply Plan**:
The broader plan for how sustainment needs will be met, including LOGPACs, routes, destinations, timing, and approvals.
_Avoid_: LOGPAC when referring to the overall planning state

**Course of Action**:
A proposed way to accomplish a sustainment mission through movements, loads, routes, timing, priorities, assumptions, and risks.
_Avoid_: Suggestion, option

**Executable Course of Action**:
A Course of Action specified enough for approval and execution in v1.
_Avoid_: High-level concept when the plan is ready to approve

**COA Regeneration**:
The recalculation of Courses of Action after accepted operational changes or relevant Operator Actions.
_Avoid_: Automatic reaction to transcripts, background refresh

**Sustainment Requirement**:
A need inferred from a Supported Unit's projected supply state for a Tracked Supply by a relevant time.
_Avoid_: Task, request

**Requirement Coverage**:
The extent to which a Course of Action satisfies one or more Sustainment Requirements.
_Avoid_: User-managed requirement, supersession

**Opportunistic Load**:
Lower-urgency supplies added to a LOGPAC when remaining Carrying Capacity is available after urgent requirements are covered.
_Avoid_: Extra cargo, filler

**Movement**:
A directive or plan that moves a LOGPAC from origin to destination with route, timing, and execution constraints.
_Avoid_: Trip, delivery

**Movement Status**:
The lifecycle state of a Movement.
_Avoid_: Movement alert

**Proposed Movement Status**:
A Movement Status indicating the movement has been generated but not approved.
_Avoid_: Draft

**Approved Movement Status**:
A Movement Status indicating the movement has been approved but is not yet underway.
_Avoid_: Selected

**In Progress Movement Status**:
A Movement Status indicating the movement is underway.
_Avoid_: Active when referring to lifecycle status

**Reroute Required Movement Status**:
A Movement Status indicating the movement is underway but its selected route is no longer acceptable.
_Avoid_: Movement alert

**Completed Movement Status**:
A Movement Status indicating the movement has finished.
_Avoid_: Done

**Transport Asset**:
Any vehicle, vessel, aircraft, unmanned system, or other conveyance used to move supplies in a LOGPAC.
_Avoid_: Prime mover when the asset is not specifically a truck or tractor

**Carrying Capacity**:
The amount of supply a Transport Asset, Supply Convoy, or LOGPAC can carry by relevant measures such as weight, volume, or item count.
_Avoid_: Inventory, load when referring to capacity

**COA Concept**:
The conceptual portion of a Course of Action, describing the purpose, time-space idea, and broad sustainment approach.
_Avoid_: Full movement details

**COA Detail**:
The detailed portion of a Course of Action, describing the supporting movements, LOGPACs, routes, loads, timing, and assumptions.
_Avoid_: Concept when referring to executable details

**Decision Support Matrix**:
A planning product that connects expected events, decision points, indicators, and recommended decisions.
_Avoid_: COA comparison table

**Storage Capacity**:
The amount of supply a Logistics Support Area or Supported Unit can hold by relevant measures such as quantity, weight, volume, or days of supply.
_Avoid_: Inventory, warehouse size

**LOGSYNC Matrix**:
A planning view that organizes sustainment movements by unit and time.
_Avoid_: Calendar, schedule

**Class of Supply**:
A military logistics category used to group supplies by type.
_Avoid_: Category, inventory type

**Class I**:
Subsistence supplies such as food, water, and rations.
_Avoid_: Food category

**Class III**:
Petroleum, oils, and lubricants, including fuel.
_Avoid_: Fuel category

**Class V**:
Ammunition and associated explosive items.
_Avoid_: Ammo category

**Tracked Supply**:
A specific supply item tracked in v1 for supported-unit inventory and convoy loads.
_Avoid_: Resource, item

**Supply Status**:
The color-band state of a Tracked Supply for a Supported Unit.
_Avoid_: Health, severity

**Green Supply Status**:
A Supply Status indicating sufficient supply for current planning needs.
_Avoid_: Good, normal

**Amber Supply Status**:
A Supply Status indicating degraded supply that needs attention before it becomes mission-limiting.
_Avoid_: Yellow, warning

**Red Supply Status**:
A Supply Status indicating critically low supply before it becomes effectively unavailable.
_Avoid_: Critical, severe

**Black Supply Status**:
A Supply Status indicating a supply is effectively out or mission-limiting.
_Avoid_: Empty, zero

**Status Cutoff**:
A scenario-specific threshold that maps a Tracked Supply quantity or time-to-depletion into a Supply Status.
_Avoid_: Universal cutoff, doctrine threshold

**Burn Rate**:
The expected consumption rate of a Tracked Supply by a Supported Unit.
_Avoid_: Usage, depletion speed

**Burn Rate Change**:
An event that changes a Supported Unit's expected consumption rate because mission conditions changed.
_Avoid_: Inventory update, status change

**Projected Black Time**:
The estimated time when a Tracked Supply will reach Black Supply Status if conditions do not change.
_Avoid_: Deadline, depletion time

**Days of Supply**:
The amount of time a unit can sustain itself with current and projected inventory.
_Avoid_: Stock duration, inventory runway

**Supply Signal**:
An observation that indicates current or future sustainment demand.
_Avoid_: Demand signal, LOGSTAT when the signal is not a formal report

**LOGSTAT**:
A logistics status report from a unit about supplies, equipment, or sustainment needs.
_Avoid_: Any supply signal

**Logistics Support Area**:
The supply origin where sustainment resources and Supply Convoys are staged before movement.
_Avoid_: Depot, base, warehouse

**Logistics Release Point**:
A planned handoff location where a Supply Convoy transfers supplies toward a Supported Unit.
_Avoid_: Destination, drop-off, depot

**Point of Interest**:
A named fixed location that matters to movement or sustainment, such as a bridge, port, airfield, base, checkpoint, or forward operating base.
_Avoid_: Marker, pin, place

**Hazard Observation**:
A reported event or condition that may affect movement, safety, or sustainment decisions.
_Avoid_: Enemy marker, incident, threat when the report is still observational

**Denied Area**:
A derived geospatial area where movement is currently considered unacceptable or strongly discouraged because of hazards or command guidance.
_Avoid_: Enemy contact, hazard, no-go zone

**Hazard Buffer Rule**:
A simple scenario rule that turns a Hazard Observation type into a Denied Area size.
_Avoid_: Threat model, confidence model

**Named Location Directory**:
The scenario's list of named places and their coordinates, used to resolve radio references into map locations.
_Avoid_: Gazetteer, location database

**Relative Location Reference**:
A described location based on a named place, bearing, and distance.
_Avoid_: Offset, relative point

**Candidate Route**:
A route option for a Supply Convoy, represented on the map and available for evaluation or approval.
_Avoid_: Route segment, map line

**Generated Route**:
A Candidate Route produced by a routing service from an origin, destination, and active Denied Areas.
_Avoid_: Automatic reroute, route segment

**Route Variant**:
An alternative path for a Movement that does not by itself change the broader sustainment concept.
_Avoid_: COA when only the path changes

**Route Evaluation**:
The assessment of a Candidate Route against denied areas, hazards, timing, and delivery impact.
_Avoid_: Route score, route status

**Taiwan Scenario**:
A real Taiwan geospatial setting with fictional units, named places, events, and sustainment problems layered onto the map.
_Avoid_: Taiwan war plan, fictional island

**Kaohsiung-Tainan Corridor**:
The bounded Taiwan Scenario area for v1, centered on a single-night contested resupply operation between Kaohsiung and Tainan.
_Avoid_: Island-wide theater, whole Taiwan map

**Quarterback**:
The Agent Callsign used by the Radio-to-Map Logistics Agent in the v1 scenario.
_Avoid_: Godfather, radio bot

**Hammer 4**:
The callsign for the v1 Logistics Watch Officer.
_Avoid_: Overlord, Sentinel 6

**Mule 2**:
The callsign for the v1 Supply Convoy.
_Avoid_: Mule 3

**Viper**:
A v1 company-sized Supported Unit with fuel-critical sustainment risk.
_Avoid_: Crusader

**Archer**:
A v1 battery-sized Supported Unit with ammunition-critical sustainment risk.
_Avoid_: Crusader

**Nomad**:
A v1 company-sized Supported Unit with lower-urgency Class I sustainment risk.
_Avoid_: Crusader

**Viper 6**:
The radio callsign for the leader or command element speaking for Viper.
_Avoid_: Viper when referring to the speaker

**Archer 6**:
The radio callsign for the leader or command element speaking for Archer.
_Avoid_: Archer when referring to the speaker

**Nomad 6**:
The radio callsign for the leader or command element speaking for Nomad.
_Avoid_: Nomad when referring to the speaker

**Radio Rollup**:
An Addressed Response that summarizes recent radio traffic, geospatial changes, logistics implications, and unresolved uncertainties.
_Avoid_: Chat summary, transcript summary

**Reroute Recommendation**:
An Addressed Response or planning output that proposes how a Supply Convoy should change route after a blockage or risk report.
_Avoid_: Navigation instruction, map direction

**Live Radio View**:
The operator view that shows radio traffic over time by channel, transcript, and agent-derived activity.
_Avoid_: Audio player, chat log

**Supply Officer View**:
The main operator workspace that shows the Logistics Picture, inventory status, convoy status, synchronized radio evidence, and action choices for the Logistics Watch Officer.
_Avoid_: Dashboard, admin view

**Evidence Pane**:
The synchronized part of the Supply Officer View that presents Live Radio View material supporting current logistics state and decisions.
_Avoid_: Separate radio app, transcript sidebar

**Approved Reroute**:
A Reroute Recommendation selected by the Logistics Watch Officer for transmission or dispatch.
_Avoid_: Automatic reroute, agent reroute

**Route Tradeoff**:
A simple comparison between reroute options, usually emphasizing speed, risk, and delivery impact.
_Avoid_: Full logistics optimization, multi-convoy planning

**Sustainment-Preserving Plan**:
A future planning concept that changes supply sequencing, partial delivery, or staging to prevent critical units from going black.
_Avoid_: Basic reroute, fastest route

**Quarterback Capability**:
A user-visible ability of Quarterback to listen, extract, update, georeference, assess, recommend, or respond.
_Avoid_: Internal tool, backend service

## Relationships

- **Tactical Radio Audio** is interpreted by the **Radio-to-Map Logistics Agent**.
- A **Prerecorded Radio Clip** is **Tactical Radio Audio**.
- All **Tactical Radio Audio** passes through the **Transcription Pipeline** before interpretation.
- **LOGNET-1** is the v1 **Radio Channel**.
- The **Field Radio Console** transmits **Tactical Radio Audio** to **LOGNET-1**.
- The **Radio-to-Map Logistics Agent** may use an **Agent Callsign** when participating in radio-style exchanges.
- **Passive Monitoring** updates the **Logistics Picture** without an **Addressed Response**.
- An **Addressed Response** occurs only when a human participant invokes the **Agent Callsign**.
- **Quarterback** is the **Agent Callsign** in the **Kaohsiung-Tainan Corridor** scenario.
- **Hammer 4** is the v1 **Logistics Watch Officer**.
- **Mule 2** is the v1 **Supply Convoy**.
- **Viper**, **Archer**, and **Nomad** are v1 **Supported Units**.
- **Viper 6**, **Archer 6**, and **Nomad 6** are radio speakers for their corresponding **Supported Units**.
- v1 has one active **LOGPAC** and may show multiple proposed **Movements** as **Courses of Action**.
- **Tactical Radio Audio** may produce one or more **Interpreted Reports**.
- A **Radio Transmission** may produce one or more **Semantic Outputs**.
- A **Semantic Output** may be a **Domain Event** or an **Interaction Intent**.
- A **Position Update**, **Supply Signal**, and **Hazard Observation** are v1 **Domain Events**.
- An **Addressed Intent** is a v1 **Interaction Intent**.
- An **Operator Action** originates from the **Supply Officer View**, not radio interpretation.
- **COA Approval** and **COA Rejection** are v1 **Operator Actions**.
- **COA Approval** triggers **COA Application**.
- **COA Application** is deterministic and not performed by **Quarterback**.
- **Quarterback** may create a **Draft Transmission** from approved state.
- **Outbound Audio** may be produced for an **Addressed Response** or approved **Draft Transmission**.
- **Outbound Audio** follows **Radio Brevity**.
- A **Radio Transmission** may produce one or more **Proposed Interpretations**.
- A **Proposed Interpretation** may become an **Auto-Accepted Interpretation**, a **Review-Required Interpretation**, or a **Rejected Interpretation**.
- The **Agentic Boundary** keeps deterministic work in tools or services rather than agents.
- An **Interpretation Judge** classifies a **Proposed Interpretation** for auto-acceptance or review.
- A **Review Trigger** guides the **Interpretation Judge** but does not replace agent judgment.
- A **Review-Required Interpretation** does not affect consequential operational state until the **Logistics Watch Officer** accepts it.
- A **Radio Rollup** explains recent **Interpreted Reports** and their impact on the **Logistics Picture**.
- A **Reroute Recommendation** may follow from a blocked route, delayed **Supply Convoy**, or changed risk in the **Logistics Picture**.
- The **Live Radio View** visualizes **Tactical Radio Audio**, transcripts, and agent-derived activity over time.
- The **Supply Officer View** visualizes the **Logistics Picture** and lets the **Logistics Watch Officer** select an **Approved Reroute**.
- The **Evidence Pane** embeds **Live Radio View** material inside the **Supply Officer View**.
- **Quarterback** may propose a **Reroute Recommendation**, but only the **Logistics Watch Officer** can create an **Approved Reroute**.
- A v1 **Reroute Recommendation** presents **Route Tradeoffs**, not a full **Sustainment-Preserving Plan**.
- An **Interpreted Report** is appended to the **Event Ledger**.
- The **Radio-to-Map Logistics Agent** updates the **Logistics Picture**.
- The **Logistics Picture** is derived from the **Event Ledger**.
- The **Logistics Common Operating Picture** is the map-first presentation of the **Logistics Picture**.
- A map visualizes selected parts of the **Logistics Picture**.
- A **Supported Unit** may generate sustainment demand.
- A **Logistics Watch Officer** decides how the **Logistics Picture** affects the resupply plan.
- A **Supply Convoy** executes resupply for one or more **Supported Units**.
- A **Logistics Support Area**, **LOGPAC**, and **Supported Unit** may each have **Inventory**.
- A **LOGPAC** may include a **Supply Convoy** and its **Supply Load**.
- A **Resupply Plan** may include one or more **LOGPACs**.
- **COA Regeneration** follows accepted **Domain Events** or relevant **Operator Actions**.
- **COA Approval** accepts an **Executable Course of Action** as a whole.
- A **Course of Action** may create or update one or more **Movements**.
- A v1 **Executable Course of Action** specifies a **LOGPAC**, **Movement**, assigned **Supply Convoy**, route, timing, assumptions, risks, and projected effect.
- In v1, each **Course of Action** contains one **Movement**.
- A **Course of Action** has **Requirement Coverage** over one or more **Sustainment Requirements**.
- A v1 **Sustainment Requirement** is inferred from projected supply state, not managed directly by the **Logistics Watch Officer**.
- A **LOGPAC** may include an **Opportunistic Load** when urgent **Sustainment Requirements** are covered and **Carrying Capacity** remains.
- A **Movement** may be shown in the **LOGSYNC Matrix**.
- A **Movement** has one **Movement Status**.
- A **Movement** directs one **LOGPAC** from origin to destination.
- A **Movement** may assign one **Supply Convoy** to execute it.
- A **Supply Convoy** executes one active **Movement** at a time.
- A **LOGPAC** may fulfill one active **Movement** at a time.
- A **Transport Asset** carries part or all of a **Supply Load**.
- A **Transport Asset**, **Supply Convoy**, or **LOGPAC** has **Carrying Capacity**.
- A **Course of Action** has a **COA Concept** and **COA Detail**.
- A **Course of Action** may be prepared for wargaming through a **LOGSYNC Matrix** or **Decision Support Matrix**.
- A **Logistics Support Area** or **Supported Unit** may have **Storage Capacity**.
- A **Supply Convoy** carries one **Supply Load** at a time.
- A **Supply Load** contains one or more **Tracked Supplies**.
- A **Tracked Supply** belongs to one **Class of Supply**.
- A **Tracked Supply** for a **Supported Unit** has one **Supply Status**.
- A **Status Cutoff** may vary by **Supported Unit**, **Tracked Supply**, and mission context.
- A **Burn Rate** may vary by **Supported Unit** and **Tracked Supply**.
- A **Burn Rate Change** may alter a **Projected Black Time** without an immediate **Inventory** quantity update.
- A **Projected Black Time** depends on current supply, **Burn Rate**, and **Status Cutoff**.
- **Days of Supply** depends on **Inventory**, **Burn Rate**, and mission context.
- A **Supply Signal** may update **Inventory**, **Supply Status**, or **Projected Black Time**.
- A **LOGSTAT** is one kind of **Supply Signal**.
- A **Supply Convoy** may originate from a **Logistics Support Area**.
- A **Supply Convoy** may deliver to a **Logistics Release Point** or directly to a **Supported Unit**.
- A **Logistics Release Point** may be separate from or co-located with a **Supported Unit**.
- A **Point of Interest** may be used as a **Logistics Support Area**, **Logistics Release Point**, checkpoint, bridge, base, port, or airfield.
- A **Hazard Observation** may contribute to a **Denied Area**.
- A **Hazard Buffer Rule** derives a **Denied Area** from a **Hazard Observation**.
- A **Denied Area** influences **Route Tradeoffs**.
- A **Named Location Directory** resolves named places in **Tactical Radio Audio** into coordinates.
- A **Relative Location Reference** uses a **Point of Interest** from the **Named Location Directory**.
- A **Denied Area** may be derived from a georeferenced **Relative Location Reference**.
- A **Candidate Route** is evaluated through a **Route Evaluation**.
- A **Generated Route** is a **Candidate Route**.
- A **Route Variant** may be a **Generated Route**.
- A **Movement** may have one selected **Route Variant**.
- A **Route Evaluation** may determine that a **Candidate Route** intersects a **Denied Area**.
- **Quarterback Capabilities** define what the product must demonstrate externally, regardless of the internal agent/tool split.

## Example dialogue

> **Dev:** "Does the map own the latest unit and route state?"
> **Domain expert:** "No. The map visualizes the **Logistics Picture**; it is not the source of truth."
> **Dev:** "If two radio calls disagree, do we overwrite the older one?"
> **Domain expert:** "No. Both become **Interpreted Reports** in the **Event Ledger**, and the **Logistics Picture** reflects the best current interpretation."
> **Dev:** "When Mule 2 reports a disabled HEMTT, who is the UI primarily helping?"
> **Domain expert:** "The **Logistics Watch Officer**, because they need to know what the report does to tonight's resupply plan."
> **Dev:** "Can the system answer Overlord 6 directly on the net?"
> **Domain expert:** "Yes, through its **Agent Callsign**, but the answer must be grounded in the **Event Ledger** and **Logistics Picture**."
> **Dev:** "Should the agent announce every route update as it detects one?"
> **Domain expert:** "No. During **Passive Monitoring** it updates the **Logistics Picture** silently; it transmits only as an **Addressed Response**."
> **Dev:** "Is the first scenario island-wide?"
> **Domain expert:** "No. v1 focuses on the **Kaohsiung-Tainan Corridor**, and the agent answers as **Quarterback**."
> **Dev:** "Do we need separate commander and logistics officer callsigns?"
> **Domain expert:** "No. v1 keeps **Hammer 4** as the single coordinating logistics officer."
> **Dev:** "Is the rollup the whole demo?"
> **Domain expert:** "No. The **Radio Rollup** is the primary demo moment, and a later **Reroute Recommendation** shows how the same picture drives convoy planning."
> **Dev:** "Can Quarterback reroute Mule 2 on its own?"
> **Domain expert:** "No. **Quarterback** can recommend and answer directly, but a **Logistics Watch Officer** must select an **Approved Reroute**."
> **Dev:** "Does v1 optimize multi-convoy supply sequencing?"
> **Domain expert:** "No. v1 shows **Route Tradeoffs**; a **Sustainment-Preserving Plan** is a later capability."
> **Dev:** "Is an enemy contact itself a no-go polygon?"
> **Domain expert:** "No. The contact is a **Hazard Observation**; the system may derive a **Denied Area** from it."
> **Dev:** "Does v1 perform advanced threat modeling?"
> **Domain expert:** "No. v1 uses **Hazard Buffer Rules** to derive simple **Denied Areas**."
> **Dev:** "Do we compute every road route dynamically?"
> **Domain expert:** "No. v1 uses **Generated Routes** from a routing service and lets the **Logistics Watch Officer** approve one."
> **Dev:** "Does Hammer 4 review every interpretation?"
> **Domain expert:** "No. The **Interpretation Judge** can auto-accept low-risk interpretations; **Review-Required Interpretations** need Hammer 4 before affecting consequential operational state."
> **Dev:** "Are review triggers hard-coded doctrine?"
> **Domain expert:** "No. **Review Triggers** guide the **Interpretation Judge**, and we can tune them as the demo matures."
> **Dev:** "Should every subsystem be an agent?"
> **Domain expert:** "No. The **Agentic Boundary** says everything that can avoid being an agent should avoid being an agent."

## Flagged ambiguities

- "Radio agent" was used loosely; resolved term: **Radio-to-Map Logistics Agent**, with **Agent Callsign** for radio-net participation.
- "Reality" was used to mean backend-maintained operational state; resolved term: **Logistics Picture**.
- "Taiwan" means a **Taiwan Scenario** with real geography and fictional tactical overlays, not a real operational war plan.
