import { type ReactNode, useEffect, useMemo, useState } from "react";

import {
  Bounds,
  Coordinate,
  InventoryItem,
  LogisticsPictureScenario,
  NamedLocation,
  PrerecordedRadioClip,
  RadioTransmission,
  ReadinessResponse,
  SupplyStatus,
  fetchLogisticsPicture,
  fetchPrerecordedRadioClips,
  fetchReadiness,
  transmitPrerecordedRadioClip
} from "./api";
import "./App.css";

type ReadinessLoadState =
  | { kind: "loading" }
  | { kind: "ready"; readiness: ReadinessResponse }
  | { kind: "unavailable"; readiness: ReadinessResponse }
  | { kind: "error"; message: string };

type PictureLoadState =
  | { kind: "loading" }
  | { kind: "ready"; picture: LogisticsPictureScenario }
  | { kind: "error"; message: string };

type PrerecordedClipsLoadState =
  | { kind: "loading" }
  | { kind: "ready"; clips: PrerecordedRadioClip[] }
  | { kind: "error"; message: string };

type TransmissionLoadState =
  | { kind: "idle" }
  | { kind: "transcribing" }
  | { kind: "ready"; transmission: RadioTransmission }
  | { kind: "error"; message: string };

type MapEntity = {
  id: string;
  label: string;
  detail: string;
  coordinate: Coordinate;
  tone: "lsa" | "lrp" | "convoy" | SupplyStatus;
};

const statusRank: Record<SupplyStatus, number> = {
  green: 1,
  amber: 2,
  red: 3,
  black: 4
};

function App() {
  const [readinessState, setReadinessState] = useState<ReadinessLoadState>({
    kind: "loading"
  });
  const [pictureState, setPictureState] = useState<PictureLoadState>({
    kind: "loading"
  });
  const [clipsState, setClipsState] = useState<PrerecordedClipsLoadState>({
    kind: "loading"
  });
  const [transmissionState, setTransmissionState] = useState<TransmissionLoadState>({
    kind: "idle"
  });

  useEffect(() => {
    let active = true;

    fetchReadiness()
      .then((readiness) => {
        if (!active) return;
        setReadinessState({
          kind: readiness.status === "ready" ? "ready" : "unavailable",
          readiness
        });
      })
      .catch((error: unknown) => {
        if (!active) return;
        setReadinessState({
          kind: "error",
          message: error instanceof Error ? error.message : "Unknown readiness error"
        });
      });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;

    fetchPrerecordedRadioClips()
      .then((clips) => {
        if (!active) return;
        setClipsState({ kind: "ready", clips });
      })
      .catch((error: unknown) => {
        if (!active) return;
        setClipsState({
          kind: "error",
          message: error instanceof Error ? error.message : "Unknown Prerecorded Radio Clip error"
        });
      });

    return () => {
      active = false;
    };
  }, []);

  function transmitClip(clipId: string) {
    setTransmissionState({ kind: "transcribing" });

    transmitPrerecordedRadioClip(clipId)
      .then((transmission) => {
        setTransmissionState({ kind: "ready", transmission });
        return fetchLogisticsPicture()
          .then((picture) => {
            setPictureState({ kind: "ready", picture });
          })
          .catch((error: unknown) => {
            setPictureState({
              kind: "error",
              message: error instanceof Error ? error.message : "Unknown Logistics Picture error"
            });
          });
      })
      .catch((error: unknown) => {
        setTransmissionState({
          kind: "error",
          message: error instanceof Error ? error.message : "Unknown transcription error"
        });
      });
  }

  useEffect(() => {
    let active = true;

    fetchLogisticsPicture()
      .then((picture) => {
        if (!active) return;
        setPictureState({ kind: "ready", picture });
      })
      .catch((error: unknown) => {
        if (!active) return;
        setPictureState({
          kind: "error",
          message: error instanceof Error ? error.message : "Unknown Logistics Picture error"
        });
      });

    return () => {
      active = false;
    };
  }, []);

  const title =
    pictureState.kind === "ready"
      ? pictureState.picture.name
      : "Kaohsiung-Tainan Logistics Picture";

  return (
    <main className="workspace-shell">
      <header className="workspace-header">
        <div>
          <p className="eyebrow">Quarterback Workspace</p>
          <h1>{title}</h1>
        </div>
        <ReadinessBadge loadState={readinessState} />
      </header>

      <section className="workspace-grid" aria-label="Quarterback demo workspace">
        <SupplyOfficerView pictureState={pictureState} />
        <LogisticsStatusPanel pictureState={pictureState} readinessState={readinessState} />
      </section>

      <WorkspacePanels
        pictureState={pictureState}
        clipsState={clipsState}
        transmissionState={transmissionState}
        onTransmitClip={transmitClip}
      />
    </main>
  );
}

function SupplyOfficerView({ pictureState }: { pictureState: PictureLoadState }) {
  if (pictureState.kind === "loading") {
    return (
      <section className="map-surface" aria-labelledby="picture-heading">
        <p className="eyebrow">Supply Officer View</p>
        <h2 id="picture-heading">Loading Logistics Picture</h2>
        <p className="muted">Requesting Kaohsiung-Tainan scenario state from the API...</p>
      </section>
    );
  }

  if (pictureState.kind === "error") {
    return (
      <section className="map-surface" aria-labelledby="picture-heading">
        <p className="eyebrow">Supply Officer View</p>
        <h2 id="picture-heading">Logistics Picture Unavailable</h2>
        <p className="failure">{pictureState.message}</p>
      </section>
    );
  }

  const { picture } = pictureState;
  const entities = buildMapEntities(picture);
  const routePoints = getRouteLocations(picture).map((location) =>
    toSvgPoint(location.coordinate, picture.area_of_operations.bounds)
  );
  const polygonPoints = picture.area_of_operations.polygon
    .map((coordinate) => toSvgPoint(coordinate, picture.area_of_operations.bounds))
    .join(" ");

  return (
    <section className="map-surface" aria-labelledby="picture-heading">
      <div className="map-heading">
        <div>
          <p className="eyebrow">Supply Officer View</p>
          <h2 id="picture-heading">{picture.area_of_operations.name}</h2>
        </div>
        <p>{picture.area_of_operations.corridor}</p>
      </div>

      <div className="map-region" aria-label={`${picture.area_of_operations.name} spatial view`}>
        <svg className="map-overlay" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
          <polygon className="ao-polygon" points={polygonPoints} />
          {routePoints.length > 1 ? (
            <polyline className="route-line" points={routePoints.join(" ")} />
          ) : null}
        </svg>

        {entities.map((entity) => {
          const position = toPercent(entity.coordinate, picture.area_of_operations.bounds);
          return (
            <div
              className={`map-marker ${entity.tone}`}
              key={entity.id}
              style={{ left: `${position.x}%`, top: `${position.y}%` }}
            >
              <strong>{entity.label}</strong>
              <span>{entity.detail}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function LogisticsStatusPanel({
  pictureState,
  readinessState
}: {
  pictureState: PictureLoadState;
  readinessState: ReadinessLoadState;
}) {
  return (
    <aside className="status-panel" aria-labelledby="status-heading">
      <section>
        <h2 id="status-heading">Baseline Logistics Status</h2>
        <ScenarioStatusDetails pictureState={pictureState} />
      </section>

      <section className="status-section" aria-labelledby="readiness-heading">
        <h2 id="readiness-heading">System Readiness</h2>
        <ReadinessDetails loadState={readinessState} />
      </section>
    </aside>
  );
}

function ScenarioStatusDetails({ pictureState }: { pictureState: PictureLoadState }) {
  if (pictureState.kind === "loading") {
    return <p className="muted">Loading seeded scenario state...</p>;
  }

  if (pictureState.kind === "error") {
    return <p className="failure">{pictureState.message}</p>;
  }

  const { picture } = pictureState;
  const convoy = picture.supply_convoy;

  return (
    <div className="scenario-status">
      <dl className="status-facts">
        <div>
          <dt>Watch</dt>
          <dd>{picture.logistics_watch_officer}</dd>
        </div>
        <div>
          <dt>Radio Channel</dt>
          <dd>{picture.radio_channel}</dd>
        </div>
        <div>
          <dt>Agent Callsign</dt>
          <dd>{picture.agent_callsign}</dd>
        </div>
      </dl>

      <div className="status-section">
        <h3>Friendly Callsigns</h3>
        <ul className="callsign-list">
          {picture.friendly_callsigns.map((callsign) => (
            <li key={callsign.callsign}>
              <strong>{callsign.callsign}</strong>
              <span>{callsign.role}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="status-section">
        <h3>Supported Unit Inventory</h3>
        <div className="inventory-list">
          {picture.supported_units.map((unit) => (
            <section className="inventory-group" key={unit.id} aria-labelledby={`${unit.id}-inventory`}>
              <div>
                <h4 id={`${unit.id}-inventory`}>{unit.callsign}</h4>
                <p>{unit.display_name}</p>
              </div>
              <ul>
                {unit.inventory.map((item) => (
                  <li key={`${unit.id}-${item.class_of_supply}-${item.tracked_supply}`}>
                    <span>
                      {item.class_of_supply} / {item.tracked_supply}
                    </span>
                    <strong>
                      {formatQuantity(item.quantity)} {item.unit}
                    </strong>
                    <StatusPill status={item.status} />
                    {item.days_of_supply !== null ? <small>{item.days_of_supply} DOS</small> : null}
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>
      </div>

      <div className="status-section">
        <h3>{convoy.callsign} Supply Load</h3>
        <p className="route-summary">
          {convoy.movement_status}: {convoy.route_summary}
        </p>
        <ul className="load-list">
          {convoy.supply_load.map((item) => (
            <li key={`${item.destination_unit_id}-${item.tracked_supply}`}>
              <span>
                {item.class_of_supply} / {item.tracked_supply}
              </span>
              <strong>
                {formatQuantity(item.quantity)} {item.unit}
              </strong>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

type WorkspacePanel = {
  title: string;
  body: ReactNode;
};

function WorkspacePanels({
  pictureState,
  clipsState,
  transmissionState,
  onTransmitClip
}: {
  pictureState: PictureLoadState;
  clipsState: PrerecordedClipsLoadState;
  transmissionState: TransmissionLoadState;
  onTransmitClip: (clipId: string) => void;
}) {
  const panels = useMemo(() => {
    if (pictureState.kind !== "ready") {
      return [
        { title: "Field Radio Console", body: "Scenario callsigns load from the API." },
        { title: "Evidence Pane", body: "Radio evidence is out of scope for this slice." },
        { title: "Event Ledger", body: "Persistence arrives in the next vertical slice." },
        { title: "COA Review", body: "Executable COAs are not generated yet." }
      ];
    }

    const { picture } = pictureState;
    const unitCallsigns = picture.supported_units.map((unit) => unit.callsign).join(", ");
    return [
      {
        title: "Field Radio Console",
        body: (
          <FieldRadioConsole
            clipsState={clipsState}
            monitorText={`${picture.logistics_watch_officer} monitors ${picture.radio_channel}.`}
            onTransmitClip={onTransmitClip}
            transmissionState={transmissionState}
          />
        )
      },
      {
        title: "Evidence Pane",
        body: <EvidencePane agentCallsign={picture.agent_callsign} transmissionState={transmissionState} />
      },
      {
        title: "Event Ledger",
        body: eventLedgerPanelBody(picture)
      },
      {
        title: "Logistics Picture",
        body: `${unitCallsigns} and ${picture.supply_convoy.callsign} are visible in the AO.`
      },
      {
        title: "COA Review",
        body: `${picture.supply_convoy.callsign} remains in ${picture.supply_convoy.movement_status}.`
      }
    ] satisfies WorkspacePanel[];
  }, [clipsState, onTransmitClip, pictureState, transmissionState]);

  return (
    <section className="panel-strip" aria-label="Workspace lanes">
      {panels.map((panel) => (
        <article className="workspace-panel" key={panel.title}>
          <h2>{panel.title}</h2>
          {typeof panel.body === "string" ? <p>{panel.body}</p> : panel.body}
        </article>
      ))}
    </section>
  );
}

function FieldRadioConsole({
  clipsState,
  monitorText,
  transmissionState,
  onTransmitClip
}: {
  clipsState: PrerecordedClipsLoadState;
  monitorText: string;
  transmissionState: TransmissionLoadState;
  onTransmitClip: (clipId: string) => void;
}) {
  if (clipsState.kind === "loading") {
    return <p className="muted">Loading Prerecorded Radio Clips...</p>;
  }

  if (clipsState.kind === "error") {
    return <p className="failure">{clipsState.message}</p>;
  }

  if (clipsState.clips.length === 0) {
    return <p>No Prerecorded Radio Clips are available.</p>;
  }

  return (
    <div className="panel-details radio-console">
      <p>{monitorText}</p>
      {clipsState.clips.map((clip) => (
        <div className="radio-clip" key={clip.clip_id}>
          <strong>{clip.title}</strong>
          <span>
            {clip.source_callsign} on {clip.radio_channel}
          </span>
          <small>Audio file: {clip.audio.filename}</small>
          <button
            disabled={transmissionState.kind === "transcribing"}
            onClick={() => onTransmitClip(clip.clip_id)}
            type="button"
          >
            Transmit to {clip.radio_channel}
          </button>
        </div>
      ))}
    </div>
  );
}

function EvidencePane({
  agentCallsign,
  transmissionState
}: {
  agentCallsign: string;
  transmissionState: TransmissionLoadState;
}) {
  if (transmissionState.kind === "idle") {
    return <p>{agentCallsign} has no Tactical Radio Audio evidence attached to this seed.</p>;
  }

  if (transmissionState.kind === "transcribing") {
    return <p className="muted">Transcribing Tactical Radio Audio...</p>;
  }

  if (transmissionState.kind === "error") {
    return <p className="failure">{transmissionState.message}</p>;
  }

  const { transmission } = transmissionState;

  return (
    <div className="panel-details evidence-transcript">
      <p>
        {transmission.source_callsign} / {transmission.radio_channel}
      </p>
      <p className="transcript-text">{transmission.transcript}</p>
      <p className="panel-evidence">{transmission.audio.filename}</p>
      <p>{transmission.transcription.pipeline}</p>
      {transmission.interpretations.length > 0 ? (
        <ul className="interpretation-list">
          {transmission.interpretations.map((interpretation) => (
            <li key={interpretation.interpretation_id}>
              <strong>Auto-accepted Position Update</strong>
              <span>{interpretation.summary}</span>
              <small>{interpretation.extracted_callsigns.join(", ")}</small>
              <small>{interpretation.domain_event_id}</small>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}

function eventLedgerPanelBody(picture: LogisticsPictureScenario) {
  const latestEvent = picture.event_ledger.at(-1);

  if (!latestEvent) {
    return <p>{picture.name} is loaded as deterministic seed state.</p>;
  }

  const evidence = latestEvent.evidence[0];

  return (
    <div className="panel-details">
      <p>
        Event Ledger projection: {formatAcceptedEventCount(picture.projection.accepted_event_count)}.
      </p>
      <p>{latestEvent.summary}</p>
      {evidence ? <p className="panel-evidence">{evidence.reference}</p> : null}
    </div>
  );
}

function formatAcceptedEventCount(count: number) {
  return `${count} accepted ${count === 1 ? "event" : "events"}`;
}

function ReadinessBadge({ loadState }: { loadState: ReadinessLoadState }) {
  const label =
    loadState.kind === "ready"
      ? "API Ready"
      : loadState.kind === "loading"
        ? "Checking API"
        : "API Unavailable";

  return <div className={`readiness-badge ${loadState.kind}`}>{label}</div>;
}

function ReadinessDetails({ loadState }: { loadState: ReadinessLoadState }) {
  if (loadState.kind === "loading") {
    return <p className="muted">Checking API and PostGIS readiness...</p>;
  }

  if (loadState.kind === "error") {
    return <p className="failure">{loadState.message}</p>;
  }

  const { readiness } = loadState;

  return (
    <div className="readiness-details">
      <p>
        <span>Service</span>
        <strong>{readiness.service}</strong>
      </p>
      <p>
        <span>Status</span>
        <strong>{readiness.status}</strong>
      </p>
      <ul>
        {readiness.dependencies.map((dependency) => (
          <li key={dependency.name}>
            <span>{dependency.name}</span>
            <strong>{dependency.status}</strong>
            <small>{dependency.details}</small>
          </li>
        ))}
      </ul>
    </div>
  );
}

function StatusPill({ status }: { status: SupplyStatus }) {
  return <span className={`status-pill ${status}`}>{status}</span>;
}

function buildMapEntities(picture: LogisticsPictureScenario): MapEntity[] {
  const locations = new Map(picture.locations.map((location) => [location.id, location]));
  const fixedLocations = picture.locations
    .filter((location) => ["Logistics Support Area", "Logistics Release Point"].includes(location.role))
    .map<MapEntity>((location) => ({
      id: location.id,
      label: location.name,
      detail: location.role,
      coordinate: location.coordinate,
      tone: location.role === "Logistics Support Area" ? "lsa" : "lrp"
    }));

  const supportedUnits = picture.supported_units.flatMap((unit) => {
    const location = locations.get(unit.location_id);
    if (!location) return [];

    return [
      {
        id: unit.id,
        label: unit.callsign,
        detail: `${unit.echelon} / ${worstSupplyStatus(unit.inventory)} supply`,
        coordinate: location.coordinate,
        tone: worstSupplyStatus(unit.inventory)
      }
    ];
  });

  const convoyLocation = locations.get(picture.supply_convoy.location_id);
  const convoy = convoyLocation
    ? [
        {
          id: picture.supply_convoy.id,
          label: picture.supply_convoy.callsign,
          detail: picture.supply_convoy.movement_status,
          coordinate: convoyLocation.coordinate,
          tone: "convoy" as const
        }
      ]
    : [];

  return [...fixedLocations, ...supportedUnits, ...convoy];
}

function getRouteLocations(picture: LogisticsPictureScenario): NamedLocation[] {
  const locations = new Map(picture.locations.map((location) => [location.id, location]));
  return picture.supply_convoy.route_location_ids.flatMap((locationId) => {
    const location = locations.get(locationId);
    return location ? [location] : [];
  });
}

function worstSupplyStatus(inventory: InventoryItem[]): SupplyStatus {
  return inventory.reduce<SupplyStatus>((worst, item) => {
    return statusRank[item.status] > statusRank[worst] ? item.status : worst;
  }, "green");
}

function toPercent(coordinate: Coordinate, bounds: Bounds) {
  const x = ((coordinate.longitude - bounds.west) / (bounds.east - bounds.west)) * 100;
  const y = (1 - (coordinate.latitude - bounds.south) / (bounds.north - bounds.south)) * 100;

  return {
    x: clamp(x, 3, 97),
    y: clamp(y, 5, 95)
  };
}

function toSvgPoint(coordinate: Coordinate, bounds: Bounds) {
  const point = toPercent(coordinate, bounds);
  return `${point.x},${point.y}`;
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}

function formatQuantity(quantity: number) {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 1
  }).format(quantity);
}

export default App;
