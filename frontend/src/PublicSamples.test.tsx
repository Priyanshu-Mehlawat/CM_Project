import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import PublicSamples from "./PublicSamples";
const result = {schema_version: "v1", source: "synthetic", stage: 0, trend: "rising",
  latest_creatinine_mg_dl: 1.1, change_mg_dl: .1, index_hour: null, horizon_hours: 48,
  feature_version: "progression-v1", features: null, missing_features: [], warnings: ["Creatinine-only assessment"],
  prediction: {state: "withheld", probability: null, model_version: null, reason: "No eligible index",
    contributions: [], calibration: "not_calibrated"},
  timeline: [{measured_hour: -12, creatinine_mg_dl: 1}, {measured_hour: 7, creatinine_mg_dl: 1.1}],
};
afterEach(() => vi.unstubAllGlobals());
test("sample assessment displays actual history and matching downloadable inputs", async () => {
  vi.stubGlobal("fetch", vi.fn(async () => ({ok: true, json: async () => result})));
  render(<PublicSamples />);
  expect(await screen.findByRole("heading", {name: "Current creatinine stage 0"})).toBeVisible();
  expect(screen.getByRole("cell", {name: "1.10"})).toBeVisible();
  expect(screen.getByRole("link", {name: "Download CSV"})).toHaveAttribute("href", "/api/v1/samples/stable-no-aki/download?format=csv");
});
test("failed selection hides previous result and retry recovers", async () => {
  const fetcher = vi.fn().mockResolvedValueOnce({ok: true, json: async () => result})
    .mockRejectedValueOnce(new Error("offline"))
    .mockResolvedValueOnce({ok: true, json: async () => ({...result, stage: 1})});
  vi.stubGlobal("fetch", fetcher);
  render(<PublicSamples />);
  await screen.findByRole("heading", {name: "Current creatinine stage 0"});
  fireEvent.change(screen.getByLabelText("Choose a scenario"), {target: {value: "stage1-rising"}});
  expect(await screen.findByRole("alert")).toHaveTextContent("Sample could not be assessed");
  expect(screen.queryByText("Current creatinine stage 0")).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", {name: "Retry sample"}));
  expect(await screen.findByRole("heading", {name: "Current creatinine stage 1"})).toBeVisible();
  expect(screen.getByRole("link", {name: "Download JSON"})).toHaveAttribute("href", "/api/v1/samples/stage1-rising/download?format=json");
});
test("incompatible assessment responses do not render clinical values", async () => {
  vi.stubGlobal("fetch", vi.fn(async () => ({ok: true, json: async () => ({...result, stage: "wrong-type"})})));
  render(<PublicSamples />);
  expect(await screen.findByRole("alert")).toBeVisible();
  expect(screen.queryByText(/Current creatinine stage/)).not.toBeInTheDocument();
});
