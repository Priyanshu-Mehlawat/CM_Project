import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import PatientUpload from "./PatientUpload";
const model = {state: "not_configured" as const, model_version: null, protocol_version: null, calibration: null, metrics: null, patient_import_enabled: false};
afterEach(() => vi.unstubAllGlobals());
test("submits structured measurements and clears stale assessment on edits", async () => {
  vi.stubGlobal("fetch", vi.fn(async () => ({ok: true, json: async () => ({
    schema_version: "v1", source: "synthetic", stage: 1, trend: "rising",
    latest_creatinine_mg_dl: 1.6, change_mg_dl: .3, index_hour: 3, horizon_hours: 48,
    feature_version: "progression-v1", features: null, missing_features: [], warnings: [], timeline: [],
    prediction: {state: "model_required", probability: null, model_version: null,
      reason: "Train a private progression model", calibration: "not_calibrated", contributions: []},
  })})));
  render(<PatientUpload model={model} />);
  fireEvent.click(screen.getByRole("button", {name: "Load synthetic example"}));
  fireEvent.click(screen.getByRole("button", {name: "Evaluate measurements"}));
  expect(await screen.findByRole("heading", {name: "Current creatinine stage 1"})).toBeVisible();
  expect(screen.getByText("Train a private progression model")).toBeVisible();
  fireEvent.change(screen.getByLabelText("Input contents"), {target: {value: "{}"}});
  expect(screen.queryByText("Current creatinine stage 1")).not.toBeInTheDocument();
});
test("failed imports display actionable errors without a previous score", async () => {
  vi.stubGlobal("fetch", vi.fn(async () => ({ok: false, status: 422})));
  render(<PatientUpload model={model} />);
  fireEvent.click(screen.getByRole("button", {name: "Load synthetic example"}));
  fireEvent.click(screen.getByRole("button", {name: "Evaluate measurements"}));
  expect(await screen.findByRole("alert")).toHaveTextContent("Input was rejected");
});
