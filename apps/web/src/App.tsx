import { useEffect, useState } from "react";

import { ReadinessResponse, fetchReadiness } from "./api";
import "./App.css";

type LoadState =
  | { kind: "loading" }
  | { kind: "ready"; readiness: ReadinessResponse }
  | { kind: "unavailable"; readiness: ReadinessResponse }
  | { kind: "error"; message: string };

const workspacePanels = [
  "Supply Officer View",
  "Field Radio Console",
  "Evidence Pane",
  "Event Ledger",
  "Logistics Picture",
  "COA Review"
];

function App() {
  const [loadState, setLoadState] = useState<LoadState>({ kind: "loading" });

  useEffect(() => {
    let active = true;

    fetchReadiness()
      .then((readiness) => {
        if (!active) return;
        setLoadState({
          kind: readiness.status === "ready" ? "ready" : "unavailable",
          readiness
        });
      })
      .catch((error: unknown) => {
        if (!active) return;
        setLoadState({
          kind: "error",
          message: error instanceof Error ? error.message : "Unknown readiness error"
        });
      });

    return () => {
      active = false;
    };
  }, []);

  return (
    <main className="workspace-shell">
      <header className="workspace-header">
        <div>
          <p className="eyebrow">Quarterback Workspace</p>
          <h1>Gallatin Radio Agent</h1>
        </div>
        <ReadinessBadge loadState={loadState} />
      </header>

      <section className="workspace-grid" aria-label="Quarterback demo workspace">
        <div className="map-surface">
          <div className="map-region">
            <span className="map-pin lsa">LSA</span>
            <span className="map-pin lrp">LRP</span>
            <span className="map-pin mule">Mule 2</span>
            <span className="map-pin viper">Viper</span>
          </div>
        </div>

        <aside className="status-panel" aria-labelledby="readiness-heading">
          <h2 id="readiness-heading">Local Readiness</h2>
          <ReadinessDetails loadState={loadState} />
        </aside>
      </section>

      <section className="panel-strip" aria-label="Workspace lanes">
        {workspacePanels.map((panel) => (
          <article className="workspace-panel" key={panel}>
            <h2>{panel}</h2>
            <p>Awaiting scenario data.</p>
          </article>
        ))}
      </section>
    </main>
  );
}

function ReadinessBadge({ loadState }: { loadState: LoadState }) {
  const label =
    loadState.kind === "ready"
      ? "API Ready"
      : loadState.kind === "loading"
        ? "Checking API"
        : "API Unavailable";

  return <div className={`readiness-badge ${loadState.kind}`}>{label}</div>;
}

function ReadinessDetails({ loadState }: { loadState: LoadState }) {
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

export default App;
