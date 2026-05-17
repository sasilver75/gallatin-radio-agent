# Gallatin ML / Data Science Interview Prep

This note is for preparing for a Gallatin conversation that is more data science,
machine learning, optimization, and production AI than general app engineering.

## Public Signals

As of May 16, 2026, Gallatin publicly describes itself as building AI-powered
decision support for defense logistics: a platform that spans first, middle, and
last-mile logistics and turns operational data into actionable decisions.

Useful public references:

- Gallatin homepage: https://www.gallatin.ai/
- Gallatin careers page: https://www.gallatin.ai/careers
- Army PORTAL / Navigator announcement: https://www.gallatin.ai/news/gallatin-ai-army-portal-contract
- Routing and network optimization role: https://jobs.ashbyhq.com/gallatin/9a4877a3-b3c6-4b1a-a942-d6f46abcfdae/
- Decision and optimization systems role: https://jobs.ashbyhq.com/gallatin/f1eedfc1-21dc-4be2-932c-417da823ab93
- Allocation and packing role mirror: https://www.indeed.com/viewjob?jk=af237c0f02baec9d
- AI software engineer role mirror: https://simplify.jobs/p/81a458d2-3a10-4061-89f6-53504d7b711f/AI-Software-Engineer

The strongest signal from the postings is that Gallatin is not hiring for
"model building" in isolation. The center of gravity is production decision
systems: prediction, optimization, constraints, data quality, simulation, and
human trust all tied together.

## The Core Mental Model

The clean way to describe Gallatin's ML/data-science surface area:

> ML estimates the current and future state of the logistics system.
> Optimization chooses feasible courses of action.
> Constraint systems decide what actions are allowed.
> Simulation tests plans under uncertainty and adversarial disruption.
> Human-facing explanations make the system trusted and usable.

That framing fits the public product language:

- Navigator: AI decision support for logisticians, demand/consumption insight,
  resupply planning, and courses of action.
- Burrow: secure third-party logistics, inventory, storage, transportation, and
  fulfillment.
- Phalanx: automated asset visibility using reporting, hardware sensors, and
  computer vision.

It also fits the Army PORTAL announcement: predictive demand forecasting,
modern optimization, constraint-validated plans, consumption shortfall alerts,
route denial, environmental factors, adversary-aware simulation, and degraded
communications.

## Primary Use Cases

### 1. Demand, Consumption, and Runout Forecasting

This is the supply stock prediction problem: when does a unit run out of fuel,
water, batteries, ammunition, repair parts, food, medical supplies, or other
mission-critical materiel?

Inputs could include:

- Mission profile, echelon, personnel, equipment, and operational tempo.
- Historical consumption rates by unit type, terrain, season, and mission.
- Weather, road conditions, temperature, and forecasted environmental stress.
- Current inventory, planned resupply, known delays, and asset readiness.
- Sensor feeds, logistics reports, user-entered updates, and systems of record.

Relevant methods:

- Hierarchical time-series forecasting.
- Quantile forecasting and prediction intervals.
- Bayesian or probabilistic models where data is sparse.
- Survival/runout models: probability of stockout by time horizon.
- Drift detection and model monitoring when the operating environment changes.

The interview angle: do not only talk about forecast accuracy. Talk about
decision usefulness. A forecast that improves resupply timing, reduces stockout
risk, or changes the chosen plan is more valuable than a model with a better
offline metric but no operational effect.

Good metrics to mention:

- Calibration of prediction intervals.
- Precision/recall for shortfall alerts.
- Lead time gained before stockout.
- Downstream plan quality: fewer infeasible plans, fewer emergency resupplies,
  less wasted lift capacity, higher mission readiness.

### 2. Routing and Network Optimization

This is probably one of the highest-signal Gallatin use cases because the
current role language explicitly mentions dynamic, capacity-constrained,
risk-aware networks; multi-hop routing; time-expanded networks; vehicle routing;
min-cost flow; and large-scale graphs.

The practical problem:

- Move supplies, vehicles, and materiel through contested logistics networks.
- Respect capacity, timing windows, asset readiness, route risk, route denial,
  degraded infrastructure, and changing demand.
- Update plans as conditions change.

ML/data science can support this by estimating:

- Travel time and delay distributions.
- Route risk, interdiction likelihood, and weather impact.
- Node throughput: depot, port, warehouse, airfield, or transfer point capacity.
- Asset availability and failure risk.

Optimization then chooses:

- Which supplies move where.
- Which route each convoy/vehicle/asset takes.
- When each movement occurs.
- Which plan is robust enough under uncertainty.

Use the language from operations research more than the formal phrase "optimal
transport." "Optimal transport" is a useful intuition, but Gallatin's public
roles are closer to capacitated routing, min-cost flow, vehicle routing with time
windows, multi-commodity flow, stochastic optimization, and rolling-horizon
planning.

### 3. Allocation, Prioritization, and Packing

This is your "allocate scarce resources to places of need" intuition, plus the
physical execution layer.

Allocation decides:

- Which unit gets scarce supply first.
- How to trade off urgency, mission priority, fairness, commander intent, and
  probability of failure.
- How to reroute limited lift capacity when demand exceeds supply.

Packing/loading decides:

- Which items fit in which vehicle, pallet, container, or aircraft.
- Whether weight, volume, compatibility, sequencing, and unloading order are
  valid.
- Whether a theoretically optimal allocation can actually be executed.

Methods to be ready for:

- Assignment, matching, knapsack, bin packing, and multidimensional packing.
- Mixed-integer programming, linear programming, constraint programming.
- Approximation and heuristic methods for NP-hard cases.
- Explainable priority scores or utility functions.

The interview angle: physical feasibility matters. A model that recommends a
plan that violates vehicle capacity, compatibility, authority, or loading order
is worse than useless in this setting. Gallatin's allocation/packing role
explicitly emphasizes deterministic, testable code, edge cases, incomplete data,
and preventing AI-generated plans from bypassing feasibility checks.

### 4. Feasibility, Authority, and Constraint Systems

This is a surprisingly central use case because Gallatin has a dedicated
"Decision & Optimization Systems" role around feasibility and authority.

The problem:

- AI agents, planners, and probabilistic models may generate suggestions.
- Before any plan is optimized or executed, the system must decide whether that
  plan is allowed to exist.
- Rules may come from command hierarchy, policy, asset availability, readiness,
  safety, timing, and physical constraints.

This is where ML and deterministic systems meet:

- LLMs or probabilistic models can help interpret messy intent, reports, or
  policy-like inputs.
- Deterministic constraint systems should gate execution.
- Violations need clear diagnostics: what failed, why, and what would need to
  change.

Good phrase for the interview:

> I would treat ML outputs as hypotheses or inputs, not authority. The execution
> path should go through deterministic feasibility, policy, and physical
> constraint checks, with auditability and human-readable failure reasons.

### 5. Asset Visibility, Sensor Fusion, and Computer Vision

Gallatin's Phalanx product points directly at automated asset visibility:
traditional reporting plus hardware sensors and computer vision for in-transit
visibility and inventory management.

Potential ML/data-science use cases:

- Computer vision for inventory counts, pallet/container recognition, vehicle
  loading state, labels, damage, or anomalies.
- OCR/NLP for logistics forms, manifests, requests, and status reports.
- Sensor fusion from RFID, GPS, telematics, barcode scans, user reports, and
  warehouse systems.
- Entity resolution: reconciling the same asset across inconsistent systems.
- Anomaly detection: missing asset, impossible location, suspicious inventory
  movement, stale report, duplicate record.

The interview angle: operational data is delayed, noisy, duplicated, and
incomplete. A strong candidate talks about data contracts, confidence scores,
human review workflows, and graceful degradation, not just model architecture.

### 6. Simulation, Stress Testing, and Counterfactual Planning

The PORTAL announcement mentions adversary-aware sustainment simulation and
stress-testing logistics plans against disruptions.

Use cases:

- Generate scenarios where routes are denied, supply points are targeted,
  weather worsens, vehicles fail, or demand spikes.
- Compare courses of action under uncertainty.
- Estimate robustness, not just optimality under the mean forecast.
- Train and evaluate models when real-world data is sparse or sensitive.

Methods:

- Discrete-event simulation.
- Monte Carlo scenario generation.
- Digital twins of logistics networks.
- Robust and stochastic optimization.
- Offline policy evaluation.

The interview angle: simulation is how you safely test high-stakes decision
systems before users rely on them. It is also how you benchmark changes when
live A/B tests are infeasible or unethical.

### 7. LLMs, RAG, and Human-in-the-Loop Decision Support

The AI Software Engineer role mentions LLMs, open-source models, RAG, LangChain,
model monitoring, prompt engineering, and LLM security.

Likely use cases:

- Ingest unstructured reports and convert them into structured logistics facts.
- Let users ask natural-language questions about inventory, shortages, and plan
  feasibility.
- Summarize why a plan is risky, infeasible, or preferred.
- Generate draft courses of action that are then validated by optimization and
  constraint layers.

The interview angle: LLMs are useful at the interface and interpretation layer,
but they should not be trusted as the final source of truth for executable
logistics decisions. Talk about grounding, RAG quality, citation/provenance,
guardrails, red-teaming, and deterministic validation.

### 8. Predictive Maintenance and Readiness

This is not as explicit in the postings, but it is a natural adjacent use case.

Questions the system could answer:

- Which vehicles are likely to fail before or during a mission?
- Which repair parts should be staged forward?
- Which equipment readiness changes will affect resupply capacity?

Methods:

- Failure prediction.
- Survival analysis.
- Anomaly detection on telemetry and maintenance logs.
- Spare-parts demand forecasting.

The interview angle: readiness forecasts feed routing and allocation. If the
optimizer assumes assets exist but the readiness model says they are unlikely to
be available, the plan should change.

## Cross-Cutting Data Science Problems

### Data Quality and Operational Truth

Gallatin likely deals with fragmented systems of record, field reports, sensor
feeds, spreadsheets, APIs, and user interactions. The data-science work is not
just modeling; it is constructing a reliable operational picture.

Be ready to discuss:

- Entity resolution across assets, units, locations, and shipments.
- Missing and stale data.
- Delayed updates and out-of-order events.
- Confidence levels and provenance.
- Validation pipelines and data contracts.
- How to avoid silent failure when the data is incomplete.

### Uncertainty

The system should preserve uncertainty instead of collapsing everything into a
single point estimate.

Examples:

- "This unit will run out of fuel in 18 hours" is weaker than "70% chance of
  stockout within 18-24 hours under current tempo."
- "This route takes 4 hours" is weaker than "4 hours median, 8 hours p90 if the
  weather front hits."
- "This plan is optimal" is weaker than "this plan is feasible, robust across
  80% of simulated disruptions, and has a known tradeoff against lift usage."

### Evaluation

Use multiple levels of evaluation:

- Model metrics: MAE/RMSE for forecasts, calibration, log loss, recall of
  shortfall events.
- Solver metrics: optimality gap, runtime, scalability, robustness, constraint
  violation rate.
- System metrics: plan acceptance, human override rate, time saved, alert lead
  time, fewer emergency resupplies.
- Mission metrics: readiness, days of supply, stockout avoidance, mission
  continuity.

### Productionization

Gallatin's postings repeatedly point at production ownership: real-time and
batch pipelines, monitoring, validation, data operationalization, and feedback
from users.

Be ready to talk about:

- Batch versus streaming data flows.
- Feature stores or equivalent reproducibility mechanisms.
- Model monitoring, drift detection, and alerting.
- Backtesting and replay against historical operations.
- Canarying in a decision-support context.
- Rollback plans when model behavior changes.

## How to Position Yourself in Conversation

### A Strong 60-Second Framing

> The interesting part of Gallatin to me is that ML is not the product by
> itself. The product is better logistics decisions under uncertainty. I would
> think about the system as four layers: first, build a trustworthy operational
> state from messy data; second, forecast demand, travel time, readiness, and
> risk with uncertainty; third, feed those predictions into optimization for
> routing, allocation, and packing; fourth, enforce deterministic feasibility,
> authority, and physical constraints before a human acts. The models matter,
> but the real value is whether the whole loop produces plans that are faster,
> feasible, explainable, and trusted by operators.

### Topics to Sound Fluent On

- Forecasting under sparse, noisy, changing conditions.
- Optimization under constraints: min-cost flow, VRP, MIP, OR-Tools/Gurobi-style
  modeling.
- The difference between prediction quality and decision quality.
- Calibration and uncertainty propagation.
- Simulation as an evaluation and stress-testing tool.
- Human trust, explainability, and infeasibility diagnostics.
- Data contracts, provenance, observability, and drift.
- LLMs as interfaces or extraction tools, not unchecked execution engines.

### Questions Worth Asking the Gallatin Lead

- Where does Gallatin draw the boundary between ML prediction, optimization,
  and deterministic constraint enforcement?
- What is the hardest data-quality problem today: stale inventory, asset
  readiness, location truth, demand labels, or something else?
- How do you evaluate plan quality when live experimentation is difficult?
- Are forecasts optimized for standalone accuracy, or for downstream decisions
  like shortfall prevention and route selection?
- What kinds of uncertainty are most operationally important: demand, route
  risk, travel time, asset readiness, or adversary behavior?
- How do logisticians inspect and override the system's recommendations?
- What is the first model or optimization component a new ML/data-science hire
  would likely own?
- Given your Autodesk background, how do you think about constraint solving,
  simulation, and design-space exploration carrying over into logistics?

## Autodesk-to-Gallatin Bridge

If the interviewer was a lead ML engineer at Autodesk, a useful bridge is:

- Autodesk ML often lives near design, geometry, simulation, generative design,
  CAD/BIM workflows, and human-in-the-loop tooling.
- Gallatin's domain is different, but the shape is familiar: generate candidate
  plans, evaluate them under constraints, simulate outcomes, explain tradeoffs,
  and help experts make better decisions.
- Packing and loading has a geometry/physical-feasibility flavor.
- Routing and allocation has a design-space-search flavor.
- Decision support has a workflow/product trust flavor: experts need to
  understand, edit, and rely on model-assisted outputs.

This is a good way to steer the conversation toward the interviewer's likely
experience without pretending the domains are identical.

## Focused Prep Plan

### One-Day Prep

- Review min-cost flow, max flow/min cut, shortest path, VRP, and MIP basics.
- Review probabilistic forecasting and calibration.
- Prepare a concrete story about turning messy data into a reliable production
  model or decision system.
- Prepare one architecture sketch: demand forecast -> risk forecast -> optimizer
  -> feasibility checker -> explainable recommendation.
- Prepare one failure-mode story: bad data, model drift, hidden constraint,
  infeasible plan, or user mistrust.

### One-Week Prep

- Build a toy logistics notebook or small repo:
  - Simulate units, depots, roads, weather, inventory, and demand.
  - Forecast runout with uncertainty.
  - Use OR-Tools or a simple linear program for allocation/routing.
  - Emit explanations for infeasible plans.
  - Evaluate both forecast metrics and downstream stockout avoidance.
- Read up on military logistics terminology enough to be conversational:
  echelon, sustainment, S4, classes of supply, days of supply, convoy, lift
  capacity, readiness, in-transit visibility.
- Practice explaining why ML and OR should be integrated but independently
  validated.

## Likely Interview Themes

Expect the conversation to value:

- Practical engineering judgment over academic model novelty.
- Comfort with operations research and applied optimization.
- Willingness to own messy data and production behavior end to end.
- Clear thinking about safety, explainability, and failure modes.
- Ability to translate operational ambiguity into formal models.
- Respect for the human operator and the mission context.

The strongest stance is: "I can build models, but I care about the full decision
loop: trustworthy data, calibrated uncertainty, feasible optimization,
operational validation, monitoring, and user trust."
