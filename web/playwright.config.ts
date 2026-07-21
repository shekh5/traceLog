import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  expect: { timeout: 10_000 },
  use: {
    baseURL: "http://127.0.0.1:8085",
    trace: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command:
      "cd .. && OFFLINE_DEMO_MODE=true SERVICE_API_KEY=test-key STATE_BACKEND=local ${PYTHON_BIN:-.venv/bin/python} -m uvicorn dashboard.main:app --host 127.0.0.1 --port 8085",
    url: "http://127.0.0.1:8085/healthz",
    reuseExistingServer: true,
    timeout: 30_000,
  },
});
