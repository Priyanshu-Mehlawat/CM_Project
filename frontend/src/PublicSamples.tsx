import { useEffect, useState } from "react";
const cases = ["stable-no-aki", "stage1-rising", "stage1-falling", "stage2-observed", "stage3-observed", "missing-vitals", "delayed-result", "micromol-units", "expired-reference"];
export default function PublicSamples() {
  const [selected, setSelected] = useState(cases[0]);
  const [result, setResult] = useState<{stage: number | null; trend: string; latest_creatinine_mg_dl: number; index_hour: number | null; missing_features: string[]; warnings: string[]} | null>(null);
  const [error, setError] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    fetch(`/api/v1/samples/${selected}/assessment`, {signal: controller.signal})
      .then(async r => { if (!r.ok) throw new Error("Assessment failed"); return r.json(); })
      .then(data => { if (!controller.signal.aborted) {setResult(data); setError(false);} })
      .catch(() => { if (!controller.signal.aborted) setError(true); });
    return () => controller.abort();
  }, [selected]);
  return <><h1>RENAL-GUARD · Public research demo</h1><p className="intro">Explore independently authored measurements and download matching CSV/JSON files. No real patient uploads or private models are accepted by this public deployment.</p>
    <div className="workspace"><section className="card"><h2>Sample library</h2><label className="search-label" htmlFor="sample">Choose a scenario</label><select id="sample" value={selected} onChange={e => {setResult(null); setSelected(e.target.value);}}>{cases.map(c => <option key={c} value={c}>{c.replaceAll("-", " ")}</option>)}</select><div className="preset-row"><a className="button" href={`/api/v1/samples/${selected}/download?format=csv`}>Download CSV</a><a className="button" href={`/api/v1/samples/${selected}/download?format=json`}>Download JSON</a></div><p className="small">Every file is synthetic. Stage and direction describe observed measurements; they do not establish future worsening.</p></section>
    <section className="card" aria-live="polite"><h2>Computed assessment</h2>{error ? <p role="alert">Could not load this sample. Refresh to retry.</p> : !result ? <p>Assessing sample…</p> : <><h2>{result.stage == null ? "Insufficient reference timing" : `Current creatinine stage ${result.stage}`}</h2><p>Latest creatinine: {result.latest_creatinine_mg_dl.toFixed(2)} mg/dL</p><p>Observed direction: {result.trend.replaceAll("_", " ")}</p><p>Stage 1 index: {result.index_hour == null ? "Outside model scope" : `Hour ${result.index_hour}`}</p><ul className="assessment-notes">{result.warnings.map(w => <li key={w}>{w}</li>)}</ul>{result.missing_features.length > 0 && <p>Missing: {result.missing_features.join(", ")}</p>}<p className="small">A real 48-hour forecast requires private model training and evaluation. No clinical performance is claimed.</p></>}</section></div></>;
}
