import { useEffect, useState } from "react";
import { NavLink, Navigate, Route, Routes } from "react-router-dom";
import { loadDemo, loadEpisode, type DemoState, type EpisodeView } from "./api";
import { Button } from "./components/ui/button";

function Timeline({ episode }: { episode: EpisodeView }) {
  const points = episode.timeline;
  return (
    <section className="card timeline">
      <div className="card-title">
        <h2>Kidney function · observed values</h2>
        <span className="pill">mg/dL · synthetic</span>
      </div>
      <svg
        viewBox="0 0 700 230"
        role="img"
        aria-label="Synthetic creatinine observations available at the selected cutoff"
      >
        {[1, 2, 3, 4].map((value) => (
          <g key={value}>
            <line
              x1="45"
              x2="670"
              y1={200 - value * 42}
              y2={200 - value * 42}
              stroke="#e0e8ed"
            />
            <text x="12" y={205 - value * 42} fontSize="12" fill="#536b79">
              {value}
            </text>
          </g>
        ))}
        <line x1="45" x2="670" y1="200" y2="200" stroke="#a7bbc5" />
        {[0, 24, 48, 72].map((h) => (
          <text
            key={h}
            x={45 + (h / 72) * 625}
            y="224"
            textAnchor="middle"
            fontSize="12"
            fill="#536b79"
          >
            {h}h
          </text>
        ))}
        {points.map((p) => (
          <g key={p.sample_id}>
            <circle
              cx={45 + (p.measured_hour / 72) * 625}
              cy={200 - p.creatinine_mg_dl * 42}
              r="5"
              fill="#12675f"
            >
              <title>
                {p.creatinine_mg_dl} mg/dL collected h{p.measured_hour},
                available h{p.available_hour}
              </title>
            </circle>
          </g>
        ))}
        {episode.index_hour != null && (
          <line
            x1={45 + (episode.index_hour / 72) * 625}
            x2={45 + (episode.index_hour / 72) * 625}
            y1="18"
            y2="200"
            stroke="#488d9d"
            strokeDasharray="5 5"
          />
        )}
      </svg>
      <p className="small">
        Dots are measurements, not continuous physiology. Dashed line: first
        confirmed Stage 1 index. Future or unavailable observations are hidden.
      </p>
      <div className="table-scroll">
        <table>
          <caption className="sr-only">
            Available synthetic observations
          </caption>
          <thead>
            <tr>
              <th>Sample</th>
              <th>Collected</th>
              <th>Available</th>
              <th>Creatinine</th>
            </tr>
          </thead>
          <tbody>
            {points.map((p) => (
              <tr key={p.sample_id}>
                <td>{p.sample_id}</td>
                <td>Hour {p.measured_hour}</td>
                <td>Hour {p.available_hour}</td>
                <td>{p.creatinine_mg_dl} mg/dL</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
function Workspace({ id }: { id: string }) {
  const [hour, setHour] = useState(14);
  const [episode, setEpisode] = useState<EpisodeView | null>(null);
  const [error, setError] = useState(false);
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    loadEpisode(id, hour, controller.signal)
      .then((result) => {
        if (!controller.signal.aborted) {
          setEpisode(result);
          setError(false);
        }
      })
      .catch(() => {
        if (!controller.signal.aborted) setError(true);
      });
    return () => controller.abort();
  }, [id, hour, retry]);
  const current =
    episode?.id === id && episode.cutoff_hour === hour ? episode : null;
  return (
    <>
      <section className="card replay">
        <div>
          <p className="eyebrow">HISTORICAL REPLAY</p>
          <h2>Information available at ICU hour {hour}</h2>
          <p>
            Move forward to reveal observations. The prediction index is fixed
            by the confirmed fixture history.
          </p>
        </div>
        <label htmlFor="replay-hour">Replay cutoff: {hour} hours</label>
        <input
          id="replay-hour"
          type="range"
          min="0"
          max="72"
          step="1"
          value={hour}
          onChange={(e) => {
            setHour(Number(e.target.value));
            setError(false);
          }}
        />
        <div className="preset-row">
          {[6, 14, 20, 32, 60, 72].map((h) => (
            <Button
              key={h}
              onClick={() => {
                setHour(h);
                setError(false);
              }}
              aria-pressed={hour === h}
            >
              Hour {h}
            </Button>
          ))}
        </div>
      </section>
      {error ? (
        <section className="card" role="alert">
          <h2>Episode unavailable</h2>
          <p>
            The API could not return a valid episode. Earlier results are
            hidden.
          </p>
          <Button onClick={() => setRetry((v) => v + 1)}>Retry episode</Button>
        </section>
      ) : !current ? (
        <p role="status">Loading episode at the selected cutoff…</p>
      ) : (
        <>
          <div className="summary-grid">
            <article className="card">
              <span className="label">Backend clinical assessment</span>
              <h2>
                {current.assessment.stage == null
                  ? "Reference comparison unavailable"
                  : `Current creatinine stage ${current.assessment.stage}`}
              </h2>
              <p>
                Index:{" "}
                {current.index_hour == null
                  ? "No confirmed Stage 1 index"
                  : `hour ${current.index_hour}`}{" "}
                · horizon: {current.horizon_hours} hours
              </p>
              <span className="small">
                Explicit synthetic reference · creatinine-only arithmetic
              </span>
            </article>
            <article className="card">
              <span className="label">Prediction inspector</span>
              <h2>Model unavailable</h2>
              <p>No validated progression model is loaded.</p>
              <span className="small">
                No risk tier, probability or explanation is invented.
              </span>
            </article>
          </div>
          <Timeline episode={current} />
          <section className="card outcome" aria-live="polite">
            <p className="eyebrow">RETROSPECTIVE OUTCOME · NOT A PREDICTION</p>
            <h2>
              {current.outcome.state === "progressed"
                ? "Observed progression to Stage 2/3"
                : current.outcome.state === "non_progressed"
                  ? "No progression under fixture ascertainment"
                  : "Outcome unknown"}
            </h2>
            <p>{current.outcome.reason.replaceAll("_", " ")}</p>
            {current.outcome.event_hour != null && (
              <p>
                Qualifying sample collected at hour {current.outcome.event_hour}
                .
              </p>
            )}
            <p className="small">{current.outcome.followup_note}</p>
          </section>
        </>
      )}
    </>
  );
}
function Explorer({ data }: { data: DemoState }) {
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<string | null>(null);
  const filtered = data.cases.filter((e) =>
    `${e.name} ${e.description}`.toLowerCase().includes(search.toLowerCase()),
  );
  const active = data.cases.find((e) => e.id === selected);
  return (
    <>
      <p className="eyebrow">RETROSPECTIVE RESEARCH WORKSPACE</p>
      <h1>Clinical Explorer</h1>
      <p className="intro">
        First confirmed Stage 1 → Stage 2/3 within 48 hours. Explore five
        independently authored synthetic histories.
      </p>
      <div className="workspace">
        <section className="card">
          <div className="card-title">
            <h2>Review episodes</h2>
            <span className="pill">{data.cases.length} synthetic</span>
          </div>
          <label className="search-label" htmlFor="case-search">
            Search episodes
          </label>
          <input
            id="case-search"
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Progression, correction, unknown…"
          />
          {!filtered.length ? (
            <p className="small">No matching synthetic episodes.</p>
          ) : (
            <ul className="case-list">
              {filtered.map((e) => (
                <li key={e.id}>
                  <button
                    className={`case-button ${selected === e.id ? "selected" : ""}`}
                    aria-pressed={selected === e.id}
                    onClick={() => setSelected(e.id)}
                  >
                    <span className="case-icon" aria-hidden="true">
                      ◇
                    </span>
                    <span>
                      <strong>{e.name}</strong>
                      <span className="small">{e.description}</span>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
        <section className="card inspector">
          <p className="eyebrow">STUDY CONTRACT</p>
          <h2>One index. One 48-hour question.</h2>
          <p>
            The backend computes staging and outcome states. Collection time and
            availability time remain separate.
          </p>
          <dl>
            <div>
              <dt>Research mode</dt>
              <dd>Disabled · G1 decisions pending</dd>
            </div>
            <div>
              <dt>Probability / calibration</dt>
              <dd>Unavailable · no approved progression model</dd>
            </div>
            <div>
              <dt>Source</dt>
              <dd>Independently authored synthetic fixtures</dd>
            </div>
          </dl>
          <p className="footnote">
            Fixture ascertainment and reference rules illustrate behavior. They
            are not approved clinical cohort policies.
          </p>
        </section>
      </div>
      {active ? (
        <div className="episode-heading">
          <h2>{active.name}</h2>
          <Workspace key={active.id} id={active.id} />
        </div>
      ) : (
        <section className="card empty-workspace">
          <h2>Select a synthetic episode</h2>
          <p>
            Inspect availability, corrected lab results, progression, or
            insufficient follow-up.
          </p>
        </section>
      )}
    </>
  );
}
function Research({ data }: { data: DemoState }) {
  return (
    <>
      <p className="eyebrow">EVIDENCE & REPRODUCIBILITY</p>
      <h1>Research Console</h1>
      <p className="intro">
        Protocol, validation and evidence status are reported by the API.
      </p>
      <section className="card research-notice">
        <div>
          <h2>Not yet evaluated</h2>
          <p>{data.research.reason}</p>
        </div>
      </section>
      <div className="summary-grid">
        {[
          "Discrimination · AUROC / AUPRC",
          "Calibration · Brier / plots",
          "External generalization",
          "Reliability & coverage",
        ].map((title) => (
          <article className="card" key={title}>
            <h2>{title}</h2>
            <p>Not yet evaluated</p>
            <span className="small">
              No approved progression evaluation artifact
            </span>
          </article>
        ))}
      </div>
      <section className="card protocol">
        <p className="eyebrow">CURRENT RESEARCH GATE</p>
        <h2>G1 · Dataset feasibility pending</h2>
        <p>
          Baseline/reference creatinine, result availability, eligibility,
          adequate follow-up and shared mappings require documented review.
          Missing outcomes remain unknown.
        </p>
      </section>
    </>
  );
}
function Protocol() {
  return (
    <>
      <p className="eyebrow">METHODS & LIMITS</p>
      <h1>Clinical protocol</h1>
      <section className="card protocol">
        <h2>Stage 1 progression over 48 hours</h2>
        <p>
          Primary study: adults in ICU at first confirmed creatinine-defined
          Stage 1. Outcome: creatinine-defined Stage 2/3 after index through
          index + 48 hours. No onset model is used as a progression model.
        </p>
        <h2 className="space-top">Before real labeling or training</h2>
        <ol className="method-list">
          <li>
            Run the source-only audit in an authorized isolated environment.
          </li>
          <li>
            Approve reference creatinine, eligibility and result-availability
            policies.
          </li>
          <li>Approve negative ascertainment and competing-event handling.</li>
          <li>Freeze patient splits and common features before development.</li>
          <li>
            Evaluate a locked pipeline on genuinely separate, comparable data.
          </li>
        </ol>
        <p className="small">
          KDIGO 2012 creatinine arithmetic is tested on synthetic cases. Urine
          output and KRT require separate analyses. No clinical benefit is
          claimed.
        </p>
      </section>
    </>
  );
}
export default function App() {
  const [data, setData] = useState<DemoState | null>(null);
  const [failed, setFailed] = useState(false);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    loadDemo(controller.signal)
      .then((value) => {
        if (!controller.signal.aborted) setData(value);
      })
      .catch(() => {
        if (!controller.signal.aborted) setFailed(true);
      });
    return () => controller.abort();
  }, [attempt]);
  return (
    <>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <div className="app-shell">
        <aside className="sidebar">
          <NavLink className="brand" to="/clinical">
            <span className="brand-mark" aria-hidden="true">
              R
            </span>
            <span>
              RENAL<span className="brand-light">—GUARD</span>
              <small>Critical care research</small>
            </span>
          </NavLink>
          <p className="nav-label">WORKSPACE</p>
          <nav aria-label="Main navigation">
            <NavLink to="/clinical">Clinical Explorer</NavLink>
            <NavLink to="/research">Research Console</NavLink>
            <NavLink to="/protocol">Clinical Protocol</NavLink>
          </nav>
          <div className="sidebar-note">
            <span className="label">SOURCE BOUNDARY</span>
            <p>Synthetic fixtures only</p>
            <small>All stages and outcomes come from the canonical API.</small>
          </div>
          <div className="sidebar-footer">
            Group 31 <span>Research · v0.2</span>
          </div>
        </aside>
        <div className="main-shell">
          <header className="topbar">
            <span>
              RENAL-GUARD{" "}
              <span className="breadcrumb">/ Progression research</span>
            </span>
            <span className="pill">SYNTHETIC DEMO</span>
          </header>
          <div className="research-banner">
            <strong>Research Prototype</strong>
            <span>
              For retrospective research and education. Not for patient care.
            </span>
          </div>
          <main id="main" tabIndex={-1}>
            {failed ? (
              <section className="card" role="alert">
                <h1>Backend unavailable</h1>
                <p>
                  Start the local API with <code>make dev-backend</code>. No
                  cached or invented results are displayed.
                </p>
                <Button
                  onClick={() => {
                    setFailed(false);
                    setData(null);
                    setAttempt((v) => v + 1);
                  }}
                >
                  Retry connection
                </Button>
              </section>
            ) : !data ? (
              <p role="status">Connecting to the local synthetic API…</p>
            ) : (
              <>
                <div className="connection">
                  <span className="connection-dot" aria-hidden="true" /> API
                  connected <span>· Synthetic demo · Model unavailable</span>
                </div>
                <Routes>
                  <Route path="/clinical" element={<Explorer data={data} />} />
                  <Route path="/research" element={<Research data={data} />} />
                  <Route path="/protocol" element={<Protocol />} />
                  <Route
                    path="*"
                    element={<Navigate to="/clinical" replace />}
                  />
                </Routes>
              </>
            )}
          </main>
          <footer className="footer">
            RENAL-GUARD{" "}
            <span>48-hour progression · Clinical protocol pending review</span>
          </footer>
        </div>
      </div>
    </>
  );
}
