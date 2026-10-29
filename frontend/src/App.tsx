import { useEffect, useState } from 'react';
import { NavLink, Navigate, Route, Routes } from 'react-router-dom';
import { loadDemo, type DemoState } from './api';
import { Button } from './components/ui/button';

function Explorer({ data }: { data: DemoState }) {
  const [selected, setSelected] = useState<string | null>(null);
  const active = data.cases.find(item => item.id === selected);
  return <>
    <div className="section-heading"><div><p className="eyebrow">RETROSPECTIVE WORKSPACE</p>
      <h1>Clinical Explorer</h1><p className="intro">A clear view of the research workflow. Every example here is synthetic.</p></div>
      <span className="pill">{data.cases.length} synthetic examples</span></div>
    <div className="summary-grid"><article className="card"><span className="label">Prediction target</span><h2>AKI progression</h2><p>Stage 1 → Stage 2/3 · 48-hour horizon</p><span className="small">Study objective · clinical definitions pending G1</span></article>
      <article className="card"><span className="label">Inference status</span><h2>Model unavailable</h2><p>No validated model has been loaded.</p><span className="small">Probabilities and explanations unavailable</span></article></div>
    <div className="workspace"><section className="card"><div className="card-title"><h2>Synthetic review queue</h2><span className="dot-label">Demo fixtures</span></div><p className="small">Independently authored examples for interface development.</p>
      {data.cases.length === 0 ? <p>No synthetic examples are available.</p> : <ul className="case-list">{data.cases.map(item => <li key={item.id}><button className={`case-button ${selected === item.id ? 'selected' : ''}`} aria-pressed={selected === item.id} onClick={() => setSelected(item.id)}><span className="case-icon" aria-hidden="true">◇</span><span><strong>{item.name}</strong><span className="small">Synthetic · Model unavailable</span></span><span aria-hidden="true">↗</span></button></li>)}</ul>}
    </section><section className="card inspector" aria-live="polite"><p className="eyebrow">PREDICTION INSPECTOR</p>{active ? <><h2>{active.name}</h2><p>{active.description}</p><dl><div><dt>Source</dt><dd>Independently authored synthetic fixture</dd></div><div><dt>Clinical stage</dt><dd>Unavailable · clinical engine pending</dd></div><div><dt>Prediction</dt><dd>Model unavailable</dd></div></dl></> : <><div className="empty-symbol" aria-hidden="true">⌁</div><h2>Select an example</h2><p>Open a synthetic case to inspect its provenance and availability state.</p></>}
      <p className="footnote">No clinical interpretation or treatment guidance is provided.</p></section></div>
  </>;
}
function Research() {
  return <><p className="eyebrow">EVIDENCE & REPRODUCIBILITY</p><h1>Research Console</h1><p className="intro">Validation results will appear here when reviewed, versioned artifacts are available.</p>
    <section className="card research-notice"><span className="empty-symbol" aria-hidden="true">◎</span><div><h2>Not yet evaluated</h2><p>No training or internal/external evaluation has been performed. No performance claim is available.</p></div></section>
    <div className="summary-grid">{['Model comparison', 'Internal & external validation', 'Calibration', 'Reliability & coverage'].map(title => <article className="card" key={title}><h2>{title}</h2><p>Not yet evaluated</p><span className="small">Awaiting genuine evaluation artifacts</span></article>)}</div>
    <section className="card protocol"><p className="eyebrow">CURRENT RESEARCH GATE</p><h2>G1 · Dataset feasibility pending</h2><p>Reference creatinine, adequate outcome follow-up, result availability, eligibility, and shared feature mappings require a reviewed dataset audit.</p></section></>;
}
export default function App() {
  const [data, setData] = useState<DemoState | null>(null);
  const [failed, setFailed] = useState(false);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    loadDemo(controller.signal).then(value => { if (!controller.signal.aborted) setData(value); })
      .catch(() => { if (!controller.signal.aborted) setFailed(true); });
    return () => controller.abort();
  }, [attempt]);
  return <><a className="skip-link" href="#main">Skip to content</a><div className="app-shell"><aside className="sidebar"><a className="brand" href="/clinical"><span className="brand-mark" aria-hidden="true">R</span><span>RENAL<span className="brand-light">—GUARD</span><small>Critical care research</small></span></a><p className="nav-label">WORKSPACE</p><nav aria-label="Main navigation"><NavLink to="/clinical"><span aria-hidden="true">▦</span> Clinical Explorer</NavLink><NavLink to="/research"><span aria-hidden="true">◫</span> Research Console</NavLink></nav><div className="sidebar-note"><span className="label">SOURCE BOUNDARY</span><p>Synthetic fixtures only</p><small>Restricted datasets are never connected to this demo.</small></div><div className="sidebar-footer">Group 31 <span>Foundation · v0.1</span></div></aside>
    <div className="main-shell"><header className="topbar"><span>RENAL-GUARD <span className="breadcrumb">/ Research workspace</span></span><span className="pill">SYNTHETIC DEMO</span></header><div className="research-banner"><strong>Research Prototype</strong><span>For retrospective research and education. Not for patient care.</span></div>
    <main id="main" tabIndex={-1}>{failed ? <section className="card" role="alert"><h1>Backend unavailable</h1><p>The local API could not be reached or returned an incompatible response. Start the backend with <code>make dev-backend</code>.</p><p>Model unavailable. No cached or invented results are displayed.</p><Button onClick={() => {setFailed(false); setData(null); setAttempt(value => value + 1);}}>Retry connection</Button></section> : !data ? <p role="status">Connecting to the local synthetic API…</p> : <><div className="connection"><span className="connection-dot" aria-hidden="true"/> API connected <span>· Synthetic demo · Model unavailable</span></div><Routes><Route path="/clinical" element={<Explorer data={data}/>}/><Route path="/research" element={<Research/>}/><Route path="*" element={<Navigate to="/clinical" replace/>}/></Routes></>}</main><footer className="footer">RENAL-GUARD <span>Synthetic source · Clinical protocol pending review</span></footer></div></div></>;
}
