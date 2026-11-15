import { useEffect, useRef, useState } from "react";
import { Button } from "./components/ui/button";
import { importPatient, type ModelStatus, type PatientAssessment } from "./api";

export const examplePatient = {
  source: "synthetic", age: 62, cutoff_hour: 8,
  reference_creatinine_mg_dl: 1, reference_measured_hour: -12,
  reference_available_hour: -11, reference_confirmed: true,
  eligibility_confirmed: true, protocol_version: "example-only-v1",
  observations: [
    { concept: "creatinine", value: 1.3, unit: "mg/dL", measured_hour: 2, available_hour: 3 },
    { concept: "creatinine", value: 1.6, unit: "mg/dL", measured_hour: 7, available_hour: 8 },
    { concept: "heart_rate", value: 94, unit: "bpm", measured_hour: 2, available_hour: 2 },
    { concept: "map", value: 74, unit: "mmHg", measured_hour: 2, available_hour: 2 },
    { concept: "respiratory_rate", value: 21, unit: "/min", measured_hour: 2, available_hour: 2 },
    { concept: "spo2", value: 96, unit: "%", measured_hour: 2, available_hour: 2 },
    { concept: "temperature", value: 37.2, unit: "C", measured_hour: 2, available_hour: 2 },
    { concept: "bun", value: 31, unit: "mg/dL", measured_hour: 2, available_hour: 3 },
    { concept: "potassium", value: 4.6, unit: "mmol/L", measured_hour: 2, available_hour: 3 },
  ],
};
function downloadTemplate(format: "json" | "csv") {
  const { observations, ...meta } = examplePatient;
  const content = format === "json" ? JSON.stringify(examplePatient, null, 2) : [
    [...Object.keys(meta), ...Object.keys(observations[0])].join(","),
    ...observations.map(o => [...Object.values(meta), ...Object.values(o)].join(",")),
  ].join("\n");
  const url = URL.createObjectURL(new Blob([content], { type: "text/plain" }));
  const link = document.createElement("a");
  link.href = url; link.download = `renal-guard-template.${format}`; link.click();
  URL.revokeObjectURL(url);
}
export default function PatientUpload({ model }: { model: ModelStatus }) {
  const [content, setContent] = useState("");
  const [format, setFormat] = useState<"json" | "csv">("json");
  const [result, setResult] = useState<PatientAssessment | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const request = useRef<AbortController | null>(null);
  const generation = useRef(0);
  useEffect(() => () => { request.current?.abort(); }, []);
  function invalidate() {
    generation.current += 1;
    request.current?.abort();
    setResult(null); setError(""); setBusy(false);
  }
  async function evaluate() {
    invalidate();
    const controller = new AbortController();
    request.current = controller;
    setBusy(true);
    try {
      const assessment = await importPatient(format, content, controller.signal);
      if (!controller.signal.aborted) setResult(assessment);
    } catch (e) {
      if (!controller.signal.aborted) setError(e instanceof Error ? e.message : "Assessment failed");
    } finally {
      if (!controller.signal.aborted) setBusy(false);
    }
  }
  return <>
    <p className="eyebrow">UPLOAD · ASSESS · INSPECT</p>
    <h1>Patient assessment</h1>
    <p className="intro">Import timestamped creatinine, labs and vitals. Inspect current kidney status and an index-time 48-hour forecast when a trained progression model is installed.</p>
    <section className="card protocol">
      <div className="card-title"><h2>Local inference engine</h2><span className="pill">{model.state === "ready" ? "MODEL CONNECTED" : "ASSESSMENT READY"}</span></div>
      <p>{model.state === "ready" ? `Model ${model.model_version} · Protocol ${model.protocol_version} · ${model.calibration}` : "Creatinine staging and trend assessment work now. Forecasting requires a privately trained progression bundle; follow the local training runbook."}</p>
      <p className="small">{model.patient_import_enabled ? "Authorized research imports enabled on this device." : "Synthetic uploads enabled. Enable patient import in your authorized isolated research environment."} Uploads are processed in memory, without app storage or external AI calls. This is a research prototype, not a clinical decision tool.</p>
    </section>
    <div className="workspace upload-layout">
      <section className="card">
        <h2>Measurements and reference</h2>
        <p>Use the template for one adult ICU encounter. Supply a verified reference creatinine, result-availability times and protocol eligibility. No names, dates of birth or record numbers.</p>
        <div className="preset-row">
          <Button onClick={() => downloadTemplate("json")}>JSON template</Button>
          <Button onClick={() => downloadTemplate("csv")}>CSV template</Button>
          <Button onClick={() => { invalidate(); setFormat("json"); setContent(JSON.stringify(examplePatient, null, 2)); }}>Load synthetic example</Button>
        </div>
        <label className="search-label" htmlFor="patient-file">Upload CSV or JSON · maximum 100 KB</label>
        <input id="patient-file" type="file" accept=".csv,.json" disabled={busy} onChange={async e => {
          invalidate();
          const file = e.target.files?.[0];
          if (!file) return;
          if (file.size > 100000) { setError("File exceeds 100 KB."); return; }
          const current = generation.current;
          const text = await file.text();
          if (generation.current !== current) return;
          setFormat(file.name.toLowerCase().endsWith(".csv") ? "csv" : "json"); setContent(text);
        }} />
        <label className="search-label" htmlFor="input-format">Input format</label>
        <select id="input-format" value={format} onChange={e => { invalidate(); setFormat(e.target.value as "json" | "csv"); }}><option value="json">JSON</option><option value="csv">CSV</option></select>
        <label className="search-label" htmlFor="patient-content">Input contents</label>
        <textarea id="patient-content" value={content} spellCheck={false} onChange={e => { invalidate(); setContent(e.target.value); }} placeholder="Upload a file or load the example" />
        <div className="preset-row"><Button disabled={!content.trim() || busy} onClick={evaluate}>{busy ? "Assessing…" : "Evaluate measurements"}</Button><Button onClick={() => { invalidate(); setContent(""); }}>Clear session</Button></div>
        {error && <p role="alert" className="space-top">{error}</p>}
      </section>
      <section className="card" aria-live="polite">
        {!result ? <><h2>Assessment results</h2><p>Submit measurements to see the observed stage, trend, data checks and prediction provenance.</p></> : <>
          <p className="eyebrow">{result.source === "synthetic" ? "SYNTHETIC EXAMPLE" : "AUTHORIZED RESEARCH INPUT"}</p>
          <h2>{result.stage == null ? "Reference timing insufficient for staging" : `Current creatinine stage ${result.stage}`}</h2>
          <dl>
            <div><dt>Latest creatinine</dt><dd>{result.latest_creatinine_mg_dl.toFixed(2)} mg/dL</dd></div>
            <div><dt>Observed direction</dt><dd>{result.trend.replaceAll("_", " ")} {result.change_mg_dl != null && `(${result.change_mg_dl >= 0 ? "+" : ""}${result.change_mg_dl.toFixed(2)} mg/dL since previous measurement)`}</dd></div>
            <div><dt>First eligible Stage 1 index</dt><dd>{result.index_hour == null ? "Outside progression-model scope" : `Hour ${result.index_hour}`}</dd></div>
          </dl>
          <h2 className="space-top">48-hour progression forecast</h2>
          {result.prediction.probability != null ? <><p className="forecast-value">{(100 * result.prediction.probability).toFixed(1)}%</p><p>Model-estimated probability of Stage 2/3 by index + 48 hours. Uncalibrated research estimate.</p></> : <p>{result.prediction.reason}</p>}
          <p className="small">Observed rise describes the uploaded history. It does not establish future worsening. A forecast is fixed at the Stage 1 index, not recalculated using later results.</p>
          {result.prediction.model_version && <p className="small">{result.prediction.model_version} · {result.feature_version}</p>}
          <h2 className="space-top">Data checks</h2>
          <ul className="assessment-notes">{result.warnings.map(w => <li key={w}>{w}</li>)}{result.missing_features.length > 0 && <li>Missing at index: {result.missing_features.join(", ")}</li>}</ul>
          <div className="table-scroll"><table><caption>Available creatinine history</caption><thead><tr><th>Measured hour</th><th>mg/dL</th></tr></thead><tbody>{result.timeline.map((point, i) => <tr key={i}><td>{point.measured_hour}</td><td>{point.creatinine_mg_dl.toFixed(2)}</td></tr>)}</tbody></table></div>
          {result.features && <div className="table-scroll"><table><caption>Model inputs at index</caption><thead><tr><th>Feature</th><th>Value</th></tr></thead><tbody>{Object.entries(result.features).map(([k,v]) => <tr key={k}><td>{k}</td><td>{v == null ? "Missing" : v.toFixed(2)}</td></tr>)}</tbody></table></div>}
          {result.prediction.contributions.length > 0 && <><h2 className="space-top">Model influence · log odds</h2><p>Exact linear contributions relative to the saved intercept. These are model influences, not causes.</p><div className="table-scroll"><table><thead><tr><th>Feature</th><th>Contribution</th></tr></thead><tbody>{result.prediction.contributions.map(c => <tr key={c.feature}><td>{c.feature}</td><td>{c.log_odds_contribution.toFixed(3)}</td></tr>)}</tbody></table></div></>}
        </>}
      </section>
    </div>
  </>;
}
