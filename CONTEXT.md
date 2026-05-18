# Logistics Common Operating Picture

This context defines the domain language for the rebuilt Gallatin-inspired Logistics Common Operating Picture. The current product direction is a map-first sustainment workspace for a Logistics Watch Officer.

## Language

**Logistics Common Operating Picture**:
The map-first workspace where a Logistics Watch Officer inspects Unit location, sustainment posture, inventory projections, and related logistics state.
_Avoid_: Dashboard, map widget

**Logistics Watch Officer**:
The coordination user responsible for maintaining the Logistics Common Operating Picture and acting on sustainment risk.
_Avoid_: Dispatcher, generic user

**Logistics Picture**:
The current operational sustainment state represented by Units, inventory, locations, and projections.
_Avoid_: Reality, database, frontend state

**Unit**:
A military organization represented in the Logistics Common Operating Picture.
_Avoid_: Formation, map pin, group

**Selected Unit**:
The Unit currently in focus in the Logistics Common Operating Picture.
_Avoid_: Active card, selected pin

**Unit Summary Pane**:
The persistent side pane that describes the current Selected Unit.
_Avoid_: Main workspace, generic sidebar

**Detail Pane**:
The expanded working surface opened from a Unit Summary Pane section.
_Avoid_: Modal when it remains part of the LCOP workspace

**Parent Unit Context**:
The higher-level Unit context retained when a subordinate Reporting Unit becomes the Selected Unit.
_Avoid_: Breadcrumb when referring to the domain relationship

**Parent Unit Navigation**:
The UI affordance for returning from a subordinate Selected Unit to its Parent Unit Context.
_Avoid_: Browser history

**Unit Display Name**:
The human-readable full name of a Unit.
_Avoid_: Label when referring to the full name

**Unit Short Label**:
The abbreviated label used for a Unit on compact map and matrix surfaces.
_Avoid_: Nickname, code name

**Unit Tag**:
A freeform short descriptor attached to a Unit to communicate mission posture or application-specific identity.
_Avoid_: Label when referring to a unit name

**Reporting Unit**:
A Unit whose logistics status contributes to a higher-level sustainment posture.
_Avoid_: Row, child item, map marker

**Supported Unit**:
A Unit whose supply status, location, or mission creates sustainment demand.
_Avoid_: Customer, requester, receiver

**MGRS Grid Reference**:
A Military Grid Reference System location string used to identify a position in military-readable form.
_Avoid_: Address, latitude-longitude display

**Inventory**:
The quantity of Tracked Supplies held by a Unit.
_Avoid_: Stocks, warehouse, cargo

**Inventory Line**:
A Tracked Supply represented in a specific Unit's active Inventory.
_Avoid_: Global supply item, historical record

**On-Hand Inventory**:
Inventory currently available before future projection.
_Avoid_: OH as the canonical term

**Projected Inventory**:
The predicted quantity of a Tracked Supply at a Forecast Horizon.
_Avoid_: Manually entered future stock

**Displayed Inventory Quantity**:
The non-negative inventory quantity shown to the Logistics Watch Officer.
_Avoid_: Internal shortage calculation

**Requirement Baseline**:
The standing quantity a Unit is expected to maintain for a Tracked Supply.
_Avoid_: Mission-specific demand model for the initial LCOP

**Supply Percentage**:
The percentage of a Requirement Baseline represented by an inventory quantity.
_Avoid_: Raw quantity when comparing status across supplies

**Inventory Correction**:
A trusted Logistics Watch Officer correction to On-Hand Inventory.
_Avoid_: Temporary edit, future projection edit, local override

**Inventory Update**:
A submitted batch of changes to a Unit's active Inventory.
_Avoid_: Single-cell edit when multiple changes are submitted together

**Inventory Addition**:
A Logistics Watch Officer action that adds an Inventory Line to a Unit's active Inventory.
_Avoid_: Catalog creation unless the Tracked Supply itself is new

**Supply Catalog**:
The set of known Tracked Supplies that can be added to Unit Inventory.
_Avoid_: A Unit's current Inventory

**Inventory Removal**:
A Logistics Watch Officer action that removes an Inventory Line from a Unit's active Inventory.
_Avoid_: Deleting supply history, deleting the Tracked Supply

**Tracked Supply**:
A specific supply item tracked for Unit inventory and sustainment projection.
_Avoid_: Resource, arbitrary item

**Unit of Issue**:
The packaging or measurement unit used to count a Tracked Supply.
_Avoid_: Unit when referring to a military organization

**Quantity per Unit Pack**:
The number of individual items contained in one packaged Unit of Issue.
_Avoid_: Pack size when the package count is meant

**Class of Supply**:
A military logistics category used to group supplies by type.
_Avoid_: Category, inventory type

**Class I**:
Subsistence supplies such as food, water, and rations.
_Avoid_: Food category

**Class II**:
Clothing, individual equipment, tools, and administrative supplies.
_Avoid_: Gear category

**Class III**:
Petroleum, oils, and lubricants, including fuel.
_Avoid_: Fuel category

**Class IV**:
Construction and fortification materials.
_Avoid_: Building supplies

**Class V**:
Ammunition and associated explosive items.
_Avoid_: Ammo category

**Class VI**:
Personal demand items.
_Avoid_: Comfort items

**Class VII**:
Major end items such as vehicles and weapon systems.
_Avoid_: Equipment category

**Class VIII**:
Medical materiel.
_Avoid_: Medical supplies

**Class IX**:
Repair parts.
_Avoid_: Spare parts

**Class X**:
Nonmilitary support materials.
_Avoid_: Civilian supplies

**BRAG Status**:
A Black, Red, Amber, or Green logistics condition used to summarize supply risk.
_Avoid_: Traffic light, arbitrary color

**Supply Status**:
The BRAG Status of a Tracked Supply for a Unit at a specific inventory point.
_Avoid_: Health, severity

**Status Cutoff**:
A threshold that maps Supply Percentage into a BRAG Status.
_Avoid_: Universal doctrine threshold

**Default BRAG Bands**:
The initial product-standard Supply Percentage ranges used to derive BRAG Status.
_Avoid_: Authoritative doctrine

**Green Status**:
BRAG Status for Supply Percentage greater than or equal to 80%.
_Avoid_: Fully mission capable as a guaranteed operational judgment

**Amber Status**:
BRAG Status for Supply Percentage greater than or equal to 50% and less than 80%.
_Avoid_: Safe, acceptable

**Red Status**:
BRAG Status for Supply Percentage greater than or equal to 30% and less than 50%.
_Avoid_: Immediate failure

**Black Status**:
BRAG Status for Supply Percentage less than 30%.
_Avoid_: Empty in every case

**Forecast Horizon**:
A product-standard time bucket used to evaluate projected sustainment status.
_Avoid_: Calendar slot, arbitrary column

**72-Hour Sustainment Window**:
The three-day planning window used as the central reference point for projected sustainment posture.
_Avoid_: Random forecast point, long-term plan

**Inventory Projection Matrix**:
A compact view of On-Hand Inventory and Projected Inventory for Tracked Supplies or Classes of Supply.
_Avoid_: Spreadsheet, generic table

**Inventory View Mode**:
A way to organize a Unit's Inventory for inspection.
_Avoid_: Separate inventory type

**Class of Supply Rollup**:
A Class of Supply-level BRAG Status that summarizes the Tracked Supplies beneath that class.
_Avoid_: Item inventory, category average

**Burn Rate**:
The expected integer quantity of a Tracked Supply consumed by a Unit per 24 hours.
_Avoid_: Usage, depletion speed

**Projected Black Time**:
The estimated time when a Tracked Supply will reach Black BRAG Status if conditions do not change.
_Avoid_: Deadline, depletion time

**Days of Supply**:
The amount of time a Unit can sustain itself with current and projected inventory.
_Avoid_: Stock duration, inventory runway

**LOGSTAT**:
A logistics status report from a Unit about supplies, equipment, or sustainment needs.
_Avoid_: Any supply signal

**LOGSYNC Matrix**:
A planning view that organizes sustainment movements by Unit and time.
_Avoid_: Calendar, schedule

**Movement**:
A logistics movement planned or executed for a Unit over a scheduled time interval.
_Avoid_: Generic calendar event, map animation

**Movement Status**:
The planning or execution state of a Movement.
_Avoid_: BRAG Status

**Proposed Movement**:
A Movement that has been planned but is not yet executing.
_Avoid_: Approved order unless approval is explicit

**In-Progress Movement**:
A Movement that is currently executing.
_Avoid_: Completed movement

**Movement Window**:
The scheduled time interval for a Movement.
_Avoid_: Forecast Horizon

**Daily Movement Capacity**:
The maximum number of Movements that may be scheduled for a parent Unit on a day.
_Avoid_: Visual column width

**Movement Destination Unit**:
The Supported Unit that a Movement is intended to resupply or serve.
_Avoid_: Movement executor, convoy owner

**Movement Payload**:
The Tracked Supplies and quantities carried by a Movement.
_Avoid_: Class of Supply label as the payload itself

**Movement Class Rollup**:
The Classes of Supply represented by a Movement Payload.
_Avoid_: Specific carried supplies

**Course of Action**:
A proposed sustainment response derived from the Logistics Picture.
_Avoid_: Generic task, guaranteed order

**COA Regeneration**:
Re-evaluation of Courses of Action after relevant logistics state changes.
_Avoid_: Manual planning note

**Taiwan Scenario**:
A real Taiwan geospatial setting with fictional Units, named places, inventory, and sustainment problems layered onto the map.
_Avoid_: Taiwan war plan, real-world disposition

**3rd Infantry Brigade Combat Team**:
The default Selected Unit for the initial LCOP.
_Avoid_: 3rd Infantry Bridge Combat Team

**HHC, 3IBCT**:
The headquarters company Reporting Unit for the initial 3rd Infantry Brigade Combat Team LCOP.
_Avoid_: Headquarters pin

**2-27 IN**:
An infantry battalion Reporting Unit in the initial 3rd Infantry Brigade Combat Team LCOP.
_Avoid_: Generic infantry unit

**2-35 IN**:
An infantry battalion Reporting Unit in the initial 3rd Infantry Brigade Combat Team LCOP.
_Avoid_: Generic infantry unit

**3-4 CAV**:
A cavalry squadron Reporting Unit in the initial 3rd Infantry Brigade Combat Team LCOP.
_Avoid_: Generic cavalry unit

**3-7 FA**:
A field artillery battalion Reporting Unit in the initial 3rd Infantry Brigade Combat Team LCOP.
_Avoid_: Generic artillery unit

**325 BSB**:
A brigade support battalion Reporting Unit in the initial 3rd Infantry Brigade Combat Team LCOP.
_Avoid_: Generic logistics unit

**65 BEB**:
A brigade engineer battalion Reporting Unit in the initial 3rd Infantry Brigade Combat Team LCOP.
_Avoid_: Generic engineer unit

## Relationships

- The **Logistics Watch Officer** is the primary user of the **Logistics Common Operating Picture**.
- The **Logistics Common Operating Picture** is the primary application workspace.
- The **Logistics Common Operating Picture** presents the **Logistics Picture**.
- The initial **Logistics Common Operating Picture** opens with **3rd Infantry Brigade Combat Team** as the default **Selected Unit**.
- A **Selected Unit** drives the **Unit Summary Pane** and map focus.
- A **Detail Pane** may open from a **Unit Summary Pane** section.
- Map selection and Reporting Unit list selection may identify the same **Selected Unit**.
- A **Selected Unit** may retain **Parent Unit Context** when selected from a higher-level Unit.
- **Parent Unit Navigation** returns from a subordinate **Selected Unit** to its immediate **Parent Unit Context**.
- A **Unit** has one **Unit Display Name** and may have one **Unit Short Label**.
- A **Unit** may have one or more **Unit Tags**.
- A **Unit** may have an **MGRS Grid Reference** for operator-facing location.
- A **Unit** may have one or more **Reporting Units**.
- A **Reporting Unit** contributes **BRAG Status** values to a higher-level sustainment summary.
- A **Reporting Unit** may become the **Selected Unit**.
- A **Supported Unit** is a kind of **Reporting Unit** in the initial sustainment vocabulary.
- A selected parent **Unit** may show **Reporting Units** by **Class of Supply Rollup**.
- A selected **Reporting Unit** may show an **Inventory Projection Matrix** by **Tracked Supply**.
- A selected **Reporting Unit** may present **Tracked Supplies** as a flat list while preserving each item's **Class of Supply**.
- A parent **Unit** **Class of Supply Rollup** reflects its **Reporting Units** inventory state.
- **HHC, 3IBCT**, **2-27 IN**, **2-35 IN**, **3-4 CAV**, **3-7 FA**, **325 BSB**, and **65 BEB** are initial **Reporting Units** for **3rd Infantry Brigade Combat Team**.
- The initial Unit names are reused as fictional scenario entities within the **Taiwan Scenario**.
- The initial LCOP tracks **Tracked Supplies** only in **Class I**, **Class III**, and **Class V**.
- A **Tracked Supply** belongs to one **Class of Supply**.
- A **Tracked Supply** has one **Unit of Issue**.
- A **Unit of Issue** may have an optional **Quantity per Unit Pack**.
- A **Unit** may have a **Requirement Baseline** for a **Tracked Supply**.
- The initial LCOP stores **Requirement Baseline** per **Unit** and **Tracked Supply**.
- A **Requirement Baseline** is not mission-specific in the initial LCOP.
- Active **Inventory Lines** require a positive **Requirement Baseline** in the initial LCOP.
- A **Unit** may have a **Burn Rate** for a **Tracked Supply**.
- The initial LCOP stores **Burn Rate** per **Unit** and **Tracked Supply**.
- The initial LCOP expresses **Burn Rate** in the **Tracked Supply** item's **Unit of Issue** per 24 hours.
- Inventory quantities are expressed in the **Tracked Supply** item's **Unit of Issue**.
- The initial **Forecast Horizons** are 24, 48, 72, and 96 hours.
- **On-Hand Inventory** reflects current status.
- **Forecast Horizons** reflect projected future status.
- A **Forecast Horizon** contains **Projected Inventory** for a **Tracked Supply**.
- **Projected Inventory** is computed from **On-Hand Inventory**, **Burn Rate**, and **Forecast Horizon** in the initial LCOP.
- **Displayed Inventory Quantity** does not go below zero.
- Projected **BRAG Status** is calculated from logistics inputs, not manually entered as standalone color cells.
- A **Supply Percentage** compares displayed inventory quantity to a **Requirement Baseline**.
- The initial LCOP uses **Default BRAG Bands** for deriving **BRAG Status**.
- **Default BRAG Bands** are product defaults, not authoritative doctrine.
- **Default BRAG Bands** map **Supply Percentage** to **Green Status** at 80% or higher, **Amber Status** from 50% to less than 80%, **Red Status** from 30% to less than 50%, and **Black Status** below 30%.
- Inventory cell **BRAG Status** is derived from **Supply Percentage** and applicable **Status Cutoffs**.
- An **Inventory Projection Matrix** shows **On-Hand Inventory** and the standard **Forecast Horizons**.
- An **Inventory Projection Matrix** may summarize status by **Tracked Supply** or **Class of Supply**.
- The default **Inventory View Mode** groups **Tracked Supplies** by **Class of Supply**.
- The initial LCOP only needs the Class-based **Inventory View Mode**.
- A **Class of Supply Rollup** summarizes one or more **Tracked Supplies** for one **Class of Supply**.
- A **Class of Supply Rollup** takes the most constrained **BRAG Status** among its underlying **Tracked Supplies** for the same **Forecast Horizon**.
- The **72-Hour Sustainment Window** is the central planning reference within the standard **Forecast Horizons**.
- A selected **Reporting Unit** inventory view supports **Inventory Corrections**, **Inventory Additions**, and **Inventory Removals**.
- An **Inventory Line** represents one **Tracked Supply** in one **Unit**'s active **Inventory**.
- An **Inventory Update** may contain multiple **Inventory Corrections** and **Inventory Removals**.
- An **Inventory Correction** directly adjusts **On-Hand Inventory**.
- An **Inventory Correction** is trusted over model-predicted current inventory values.
- An **Inventory Correction** does not change **Burn Rate**.
- An **Inventory Addition** adds an **Inventory Line** to a **Unit**'s active **Inventory**.
- An **Inventory Addition** selects a **Tracked Supply** from the **Supply Catalog**.
- An **Inventory Addition** includes initial **On-Hand Inventory** for the new **Inventory Line**.
- An **Inventory Addition** includes a **Requirement Baseline** for the new **Inventory Line**.
- An **Inventory Addition** includes a **Burn Rate** for the new **Inventory Line**.
- An **Inventory Removal** removes an **Inventory Line** from a **Unit**'s active **Inventory**.
- Removed **Inventory Lines** do not contribute to active **Inventory Projection Matrix** displays.
- Removed **Inventory Lines** do not contribute to active **Class of Supply Rollups**.
- The inventory Edit action is for **Inventory Corrections** and **Inventory Removals**.
- The Add Items action is for **Inventory Additions**.
- **Projected Inventory** may be recalculated after an **Inventory Correction**, **Inventory Addition**, or **Inventory Removal**.
- An **Inventory Correction** may trigger **COA Regeneration**.
- **COA Regeneration** updates **Courses of Action** from the current **Logistics Picture**.
- A selected parent **Unit** may open the **LOGSYNC Matrix** in a **Detail Pane**.
- The **LOGSYNC Matrix** organizes **Movements** by **Unit** and day.
- A **Movement** is associated with a **Movement Destination Unit**.
- **LOGSYNC Matrix** rows represent **Movement Destination Units**.
- A **Movement** has one **Movement Status**.
- The initial **Movement Status** values include **Proposed Movement** and **In-Progress Movement**.
- A **Movement** has one **Movement Window**.
- A **Movement** has one **Movement Payload**.
- A **Movement Payload** contains **Tracked Supplies** and quantities.
- A **Movement Class Rollup** is derived from the **Movement Payload**.
- A **Movement** may display vehicle count and personnel count.
- The **LOGSYNC Matrix** may show **Daily Movement Capacity** for each day.
- **Daily Movement Capacity** constrains the number of **Movements** scheduled across the selected parent **Unit** on that day.

## Example Dialogue

> **Dev:** "What should be selected by default?"
> **Domain expert:** "The initial LCOP opens with **3rd Infantry Brigade Combat Team** as the **Selected Unit**."
> **Dev:** "If I click **3-4 CAV** in the Reporting Units list, is that different from clicking the map pin?"
> **Domain expert:** "No. Both make **3-4 CAV** the **Selected Unit** and focus the map on it."
> **Dev:** "Does the parent Unit show every inventory item for every subordinate Unit?"
> **Domain expert:** "No. The parent view shows **Reporting Units** by **Class of Supply Rollup**."
> **Dev:** "What do I see after selecting a Reporting Unit?"
> **Domain expert:** "You see that Unit's **Tracked Supplies** with On-Hand Inventory and Projected Inventory at 24, 48, 72, and 96 hours."
> **Dev:** "How does a Class III rollup become Red?"
> **Domain expert:** "The **Class of Supply Rollup** takes the most constrained **BRAG Status** among the Class III Tracked Supplies for that Forecast Horizon."
> **Dev:** "Can the Logistics Watch Officer directly edit projected 24, 48, 72, or 96 hour inventory?"
> **Domain expert:** "No. The Logistics Watch Officer corrects **On-Hand Inventory**; **Projected Inventory** is recalculated from the trusted current state."

## Flagged Ambiguities

- "Supply Officer View" was used as the main workspace name; resolved term: **Logistics Common Operating Picture**.
- "Formation" was introduced too broadly; resolved term: **Unit**.
- "Logistics officer" was used loosely; resolved term: **Logistics Watch Officer**.
- "GARB" was used once for color coding; resolved term: **BRAG Status**.
- "OH" was used as a UI abbreviation; resolved term: **On-Hand Inventory**.
- "PAX" appears in reference logistics products as personnel posture; it is not a **Class of Supply** and is outside the initial sustainment vocabulary.
- The inventory star marker appears in reference products but has unresolved meaning and is outside initial scope.
- "Philippines / Calapan" reference imagery informs LCOP interaction patterns, but the initial scenario remains a **Taiwan Scenario**.
- Real-world Unit names in the initial LCOP are fictional scenario entities, not claims about real-world disposition.
