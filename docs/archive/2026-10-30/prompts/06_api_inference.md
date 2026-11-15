# CODEX PROMPT 06 — FastAPI inference and provenance

Precondition: G4 completed, a trusted compatible model is available for authorized runtime; source-only Codex environment can test against synthetic/dummy **test models** labeled non-clinical. Do not access real model weights if disclosure/status unclear.

## Objective
Deliver stable, typed API contracts and actual pipeline-backed inference when a vetted local model is present, with clearly unavailable prediction states otherwise.

## Implement
- `GET /api/v1/health`, `/api/v1/system/info`, `/api/v1/patients`, `/api/v1/patients/{id}`, `/api/v1/patients/{id}/timeline`, `POST /api/v1/predictions`, `GET /api/v1/predictions/{id}/explanation`, and read-only `/api/v1/research/{models,experiments,metrics,calibration,hospitals,reliability}`.
- `PredictionService` (separate from route): eligibility, trusted feature schema, as-of index feature lookup, preprocessing, predictor, optional validated calibration, reliability, metadata, structured result. Never train inside request path.
- Responses: `available`, `review_required`, `withheld`, `unavailable`; probability null whenever not generated; machine-readable reason codes, horizon, model/protocol versions, warnings. Versioned Pydantic schemas + OpenAPI docs.
- Research JSON reads only verified artifacts; absent => `not_evaluated`, not fake values. Explain SHAP space accurately and render `unavailable` when unsupported.
- Synthetic-only demo SQLite/repositories; protected research access disabled by default, bind localhost; never expose original IDs, secrets, or protected paths in logs/errors. CORS local origins only.
- API tests with synthetic data + deterministic test model fixture. Ensure direct pipeline and API probabilities match exactly for test model; invalid and no-model paths exercised.

## Gate G6
Endpoint integration tests pass and distinction between actual validated artifacts and synthetic test models is visible. Never fabricate output on missing models. No agent access to patient data.
