import { useEffect, useState } from "react";
import { loadSample, type PatientAssessment } from "./api";
import { Button } from "./components/ui/button";
const scenarios = [
  ["stable-no-aki", "Stable creatinine", "Values do not meet creatinine-based AKI criteria."],
  ["stage1-rising", "Stage 1 · rising", "An observed increase from the first to the latest sample."],
  ["stage1-falling", "Stage 1 · falling", "An observed decrease, with Stage 1 still present."],
  ["stage2-observed", "Stage 2 observed", "Progression is already present in the measurements."],
  ["stage3-observed", "Stage 3 observed", "The latest sample meets the Stage 3 creatinine branch."],
  ["missing-vitals", "Missing vitals", "Kidney staging works while optional model inputs are absent."],
  ["delayed-result", "Delayed lab result", "The latest collected result is not yet available at cutoff."],
  ["micromol-units", "Creatinine in µmol/L", "The backend converts values into the common mg/dL unit."],
  ["expired-reference", "Reference outside timing window", "The reference is too old for the supported comparison."],
];
export default function PublicSamples() {
  const [selected, setSelected] = useState(scenarios[0][0]);
  const [loaded, setLoaded] = useState<{id: string; data: PatientAssessment} | null>(null);
  const [error, setError] = useState(false);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    loadSample(selected, controller.signal)
      .then(data => { if (!controller.signal.aborted) {setLoaded({id: selected, data}); setError(false);} })
      .catch(() => { if (!controller.signal.aborted) setError(true); });
    return () => controller.abort();
  }, [selected, attempt]);
  const result = loaded?.id === selected ? loaded.data : null;
  const scenario = scenarios.find(s => s[0] === selected)!;
  return <>
    <p className="eyebrow">COMPUTED FROM OBSERVED MEASUREMENTS</p>
    <h1>Sample assessment</h1>
    <p className="intro">Inspect a synthetic case, trace its creatinine measurements and download the exact input. All calculations come from the assessment API.</p>
    <div className="workspace upload-layout">
      <section className="card">
        <h2>Nine sample scenarios</h2>
        <label className="search-label" htmlFor="sample">Choose a scenario</label>
        <select id="sample" value={selected} onChange={e => {setError(false); setSelected(e.target.value);}}>
          {scenarios.map(([id, title]) => <option key={id} value={id}>{title}</option>)}
        </select>
        <p className="space-top">{scenario[2]}</p>
        <dl><div><dt>Source</dt><dd>Independently authored synthetic measurements</dd></div><div><dt>Cutoff</dt><dd>ICU hour 8 · results available by this time</dd></div><div><dt>Formats</dt><dd>One encounter · identical CSV and JSON contents</dd></div></dl>
        <div className="preset-row">
          <a className="button" href={`/api/v1/samples/${selected}/download?format=csv`}>Download CSV</a>
          <a className="button" href={`/api/v1/samples/${selected}/download?format=json`}>Download JSON</a>
        </div>
        <p className="small">Public samples only. For time-dependent outcomes and corrected results, open Example Replay.</p>
      </section>
      <section className="card" aria-live="polite" aria-busy={!error && !result}>
        {error ? <div role="alert"><h2>Sample could not be assessed</h2><p>No earlier result is displayed. Retry to request the current case again.</p><Button onClick={() => {setError(false); setAttempt(v => v + 1);}}>Retry sample</Button></div> : !result ? <p role="status">Assessing sample…</p> : <>
          <div className="card-title"><h2>{result.stage == null ? "Reference timing insufficient" : `Current creatinine stage ${result.stage}`}</h2><span className="pill">OBSERVED</span></div>
          <dl><div><dt>Latest available creatinine</dt><dd>{result.latest_creatinine_mg_dl.toFixed(2)} mg/dL</dd></div><div><dt>Direction since previous measurement</dt><dd>{result.trend.replaceAll("_", " ")}{result.change_mg_dl != null && ` (${result.change_mg_dl >= 0 ? "+" : ""}${result.change_mg_dl.toFixed(2)} mg/dL)`}</dd></div><div><dt>First eligible Stage 1 index in supplied history</dt><dd>{result.index_hour == null ? "No eligible index" : `Hour ${result.index_hour}`}</dd></div></dl>
          <h2 className="space-top">Available measurement history</h2>
          <div className="table-scroll"><table><caption className="sr-only">Creatinine observations known at cutoff</caption><thead><tr><th>Measured hour</th><th>Creatinine · mg/dL</th></tr></thead><tbody>{result.timeline.map((point, i) => <tr key={i}><td>{point.measured_hour}</td><td>{point.creatinine_mg_dl.toFixed(2)}</td></tr>)}</tbody></table></div>
          <h2 className="space-top">Assessment checks</h2>
          <ul className="assessment-notes">{result.warnings.map(w => <li key={w}>{w}</li>)}{result.stage == null && <li>The reference cannot support staging at the latest measurement time.</li>}{result.missing_features.length > 0 && <li>Absent at Stage 1 index: {result.missing_features.join(", ")}. Values have not been invented.</li>}</ul>
          <p className="small">Observed stage and direction are not a prediction of future worsening. No trained clinical model is connected to this public demo.</p>
        </>}
      </section>
    </div>
  </>;
}
