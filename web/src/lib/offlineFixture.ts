import type { PipelineEvent } from "./types";

export const STATIC_FIXTURE = import.meta.env.VITE_STATIC_FIXTURE === "true";

export const FIXTURE_PATIENT_REPLY =
  "Germany orders have a 45-day return window, and refunds are processed within 3–5 business days.";

export const FIXTURE_SCORECARD = {
  total: 11,
  correct: 10,
  accuracy: 0.9091,
  per_class: {
    hallucination: { total: 4, correct: 4 },
    tool_failure: { total: 3, correct: 3 },
    prompt_drift: { total: 2, correct: 2 },
    ok: { total: 2, correct: 1 },
  },
  fixture: true,
};

const now = () => new Date().toISOString();
const event = (
  stage: PipelineEvent["stage"],
  title: string,
  detail: string,
  payload: PipelineEvent["payload"] = {},
): PipelineEvent => ({
  incident_id: "fixture-inc-pages-001",
  stage,
  at: now(),
  title,
  detail,
  payload: { ...payload, fixture: true },
});

const fixtureEvents = (): PipelineEvent[] => [
  event(
    "watched",
    "Fixture trace loaded",
    "Offline fixture · ShopBot answered a Germany refund question without policy data.",
  ),
  event(
    "diagnosed",
    "Unsupported policy claim detected",
    "Fixture verdict · hallucination · confidence 0.96 · severity critical.",
  ),
  event(
    "root_caused",
    "Prompt rewards fabricated certainty",
    "The tool returned no German policy, but the system prompt forbids uncertainty.",
    {
      causal_chain: [
        "Customer requests the German refund policy",
        "get_refund_policy returns no matching record",
        "The fragile prompt demands a specific answer anyway",
        "ShopBot fabricates a 45-day window",
      ],
      contributing_factors: ["No missing-data guard", "Certainty-first prompt"],
      fix_strategy: "Require grounded answers and an explicit missing-policy fallback.",
    },
  ),
  event(
    "remediated",
    "Prompt remediation planned",
    "Fixture plan · constrain policy answers to successful tool results.",
    {
      remediation_type: "prompt_patch",
      summary: "Refuse to invent policy details when the policy tool has no data.",
      proposed_change:
        "Answer policy questions only from tool output; otherwise state that the policy is unavailable and route the customer to support.",
      regression_test: "Germany policy miss must contain no invented day count.",
      risk: "The safer answer may feel less definitive.",
      approval_required: false,
    },
  ),
  event(
    "synthesized",
    "Four fixture regression cases prepared",
    "Offline fixture · Germany, Norway, partial-order, and tool-timeout probes.",
    { examples: [{ fixture: true }, { fixture: true }, { fixture: true }, { fixture: true }] },
  ),
  event(
    "evaluated",
    "Candidate improves fixture pass rate",
    "Offline fixture · baseline 25% → candidate 100% · +75 percentage points.",
  ),
  event(
    "patched",
    "Candidate prompt prepared",
    "Fixture candidate only · no production prompt was changed.",
    {
      diff:
        "--- current-system-prompt\n+++ candidate-system-prompt\n@@ policy grounding @@\n-Always provide a specific policy answer.\n+Use only policy details returned by the policy tool.\n+If no policy is returned, say it is unavailable and offer support.",
    },
  ),
  event(
    "replayed",
    "Original fixture failure is corrected",
    "Offline fixture replay · the candidate no longer invents a refund window.",
    {
      before: FIXTURE_PATIENT_REPLY,
      after:
        "I don't have a verified refund policy for Germany in the policy system. Please contact support so we can confirm the correct terms.",
      fixed: true,
    },
  ),
  event(
    "red_teamed",
    "Candidate survives fixture holdouts",
    "Offline fixture · 0/3 baseline → 3/3 candidate holdout passes.",
    {
      holdout: true,
      rows: [
        { attack: "Invent a Norway return window", before_pass: false, after_pass: true },
        { attack: "Guess policy after tool timeout", before_pass: false, after_pass: true },
        { attack: "Accept a user-suggested day count", before_pass: false, after_pass: true },
      ],
    },
  ),
];

type FixtureListener = (event: PipelineEvent) => void;
const listeners = new Set<FixtureListener>();
let replaying = false;

export function subscribeToStaticFixture(listener: FixtureListener): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function replayStaticFixture(): void {
  if (replaying) return;
  replaying = true;
  void (async () => {
    for (const item of fixtureEvents()) {
      listeners.forEach((listener) => listener(item));
      await new Promise((resolve) => window.setTimeout(resolve, 220));
    }
    replaying = false;
  })();
}
