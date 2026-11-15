import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./tests/e2e",
  workers: 1,
  fullyParallel: false,
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:5173",
    headless: true,
    reducedMotion: "reduce",
  },
  webServer: [
    {
      command:
        "../.venv/bin/python -m uvicorn backend.app.main:app --app-dir .. --host 127.0.0.1 --port 8000 --no-access-log",
      url: "http://127.0.0.1:8000/api/v1/health",
      reuseExistingServer: false,
    },
    {
      command: "npm run dev -- --host 127.0.0.1",
      url: "http://127.0.0.1:5173",
      reuseExistingServer: false,
    },
  ],
});
