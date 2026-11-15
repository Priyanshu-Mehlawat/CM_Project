import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, expect, test, vi } from "vitest";
import App from "./App";
import { loadEpisode } from "./api";
import fixtures from "./generated/test-fixtures.json";
const responses: Record<string, unknown> = fixtures;
function mockApi(overrides: Record<string, unknown> = {}) {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string) => {
      const payload = { ...responses, ...overrides }[url];
      return {
        ok: payload !== undefined,
        status: payload === undefined ? 404 : 200,
        json: async () => payload,
      };
    }),
  );
}
afterEach(() => vi.unstubAllGlobals());
test("connected contract selects a real backend fixture and replays future-only outcomes", async () => {
  mockApi();
  render(
    <MemoryRouter initialEntries={["/clinical"]}>
      <App />
    </MemoryRouter>,
  );
  fireEvent.click(await screen.findByRole("button", { name: /Example A/ }));
  expect(
    await screen.findByRole("heading", { name: "Current creatinine stage 1" }),
  ).toBeVisible();
  expect(
    screen.getByRole("heading", { name: "Outcome unknown" }),
  ).toBeVisible();
  expect(screen.queryByText("2.1 mg/dL")).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Hour 32" }));
  expect(
    await screen.findByRole("heading", { name: "Current creatinine stage 2" }),
  ).toBeVisible();
  expect(
    screen.getByRole("heading", { name: "Observed progression to Stage 2/3" }),
  ).toBeVisible();
  expect(screen.getByText("2.1 mg/dL")).toBeVisible();
  expect(screen.getAllByText("Model unavailable").length).toBeGreaterThan(0);
});
test("corrected labs replace earlier abnormal values through the API", async () => {
  mockApi();
  render(
    <MemoryRouter initialEntries={["/clinical"]}>
      <App />
    </MemoryRouter>,
  );
  fireEvent.click(await screen.findByRole("button", { name: /Example D/ }));
  expect(
    await screen.findByRole("heading", { name: "Current creatinine stage 1" }),
  ).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: "Hour 20" }));
  expect(
    await screen.findByRole("heading", { name: "Current creatinine stage 0" }),
  ).toBeVisible();
  expect(screen.getByText(/No confirmed Stage 1 index/)).toBeVisible();
  expect(screen.queryByText("1.2 mg/dL")).not.toBeInTheDocument();
});
test("missing follow-up stays unknown and search works", async () => {
  mockApi();
  render(
    <MemoryRouter initialEntries={["/clinical"]}>
      <App />
    </MemoryRouter>,
  );
  fireEvent.click(await screen.findByRole("button", { name: /Example C/ }));
  await screen.findByRole("heading", { name: "Current creatinine stage 1" });
  fireEvent.click(screen.getByRole("button", { name: "Hour 72" }));
  expect(await screen.findByText("insufficient followup")).toBeVisible();
  fireEvent.change(screen.getByRole("searchbox"), {
    target: { value: "no-match" },
  });
  expect(screen.getByText("No matching synthetic episodes.")).toBeVisible();
});
test("backend failure has an actionable retry without cached results", async () => {
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
  render(
    <MemoryRouter initialEntries={["/clinical"]}>
      <App />
    </MemoryRouter>,
  );
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "Backend unavailable",
  );
  mockApi();
  fireEvent.click(screen.getByRole("button", { name: "Retry connection" }));
  expect(
    await screen.findByRole("button", { name: /Example A/ }),
  ).toBeVisible();
});
test("research and protocol pages show the pending gate without invented metrics", async () => {
  mockApi();
  render(
    <MemoryRouter initialEntries={["/clinical"]}>
      <App />
    </MemoryRouter>,
  );
  await screen.findByRole("button", { name: /Example A/ });
  fireEvent.click(screen.getByRole("link", { name: "Research Console" }));
  expect(
    screen.getByRole("heading", { name: "Model training handoff" }),
  ).toBeVisible();
  fireEvent.click(screen.getByRole("link", { name: "Clinical Protocol" }));
  expect(
    screen.getByRole("heading", { name: "Clinical protocol" }),
  ).toBeVisible();
});
test("incompatible numeric scores fail closed against generated response schema", async () => {
  const path = "/api/v1/episodes/synthetic-progressor?cutoff_hour=14";
  const body = fixtures[path];
  mockApi({
    [path]: { ...body, prediction: { ...body.prediction, probability: 0.75 } },
  });
  await expect(
    loadEpisode("synthetic-progressor", 14, new AbortController().signal),
  ).rejects.toThrow("Incompatible API contract");
});
test("a failed episode request hides prior outcome and provides retry", async () => {
  mockApi();
  render(
    <MemoryRouter initialEntries={["/clinical"]}>
      <App />
    </MemoryRouter>,
  );
  fireEvent.click(await screen.findByRole("button", { name: /Example A/ }));
  await screen.findByRole("heading", { name: "Current creatinine stage 1" });
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
  fireEvent.click(screen.getByRole("button", { name: "Hour 32" }));
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "Episode unavailable",
  );
  expect(
    screen.queryByRole("heading", { name: "Current creatinine stage 1" }),
  ).not.toBeInTheDocument();
  mockApi();
  fireEvent.click(screen.getByRole("button", { name: "Retry episode" }));
  expect(
    await screen.findByRole("heading", { name: "Current creatinine stage 2" }),
  ).toBeVisible();
});
