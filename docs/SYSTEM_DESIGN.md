# TraceLog system design

## Design goals

TraceLog converts observable production failures into evidence-backed, reviewable changes.
It is agent-agnostic, avoids training/evaluation leakage, keeps external side effects behind
gateways, and leaves production promotion under operator control.

## Components

| Component | Responsibility |
|---|---|
| `patient/agent.py` | Reference supervised agent, Responses tool loop, trace export |
| `tracelog/llm.py` | Shared GPT-5.6 Responses and structured-output gateway |
| `tracelog/phoenix_mcp.py` | Only Phoenix MCP boundary |
| `tracelog/loop_agent.py` | Provider-independent async orchestration |
| `tracelog/remediation.py` | Typed engineering plan and approval boundary |
| `tracelog/evaluator.py` | Bounded live development-set evaluation |
| `tracelog/redteam.py` | Fresh holdout generation, filtering, execution, judging |
| `tracelog/report.py` | Reviewable incident postmortem |
| `dashboard/main.py` | API proxy, SSE stream, self-evaluation endpoint, UI hosting |

## Data model

`Incident` is the aggregate root. It begins with a `SpanRecord` and accumulates `Verdict`,
`Severity`, `RootCause`, `RemediationPlan`, generated `DatasetExample` values,
`ExperimentResult`, `EfficiencyReport`, prompt candidate/diff, `ReplayResult`, and
`RedTeamResult`.

`RemediationPlan` distinguishes prompt, code, tool, data, and configuration fixes. It
contains evidence, a proposed change, regression test, risk, and approval flag. This keeps
“we know what to change” distinct from “we changed production.”

`RedTeamResult` records requested attacks, completed executions, execution errors, pass
counts, individual rows, and `holdout=true`. Errors do not masquerade as failed judgments.

## Evaluation integrity

The synthesizer's examples form the development set used for baseline/candidate comparison.
After the patch exists, RedTeam asks GPT-5.6 Terra for twice the requested number of new
candidate probes, rejects token-Jaccard-near-duplicates of all development and already
accepted cases, and keeps only the configured holdout count. Both current and candidate
prompts are then tested against those unseen inputs.

This is a pragmatic leakage defense, not a mathematical guarantee. A production version
should add semantic-embedding similarity, persistent benchmark lineage, and a minimum
holdout-generation success threshold.

## Failure and retry behavior

The OpenAI SDK owns bounded transport retries and timeout configuration. Evaluator cases are
concurrency-limited and gathered with exception isolation so one slow probe cannot cancel the
entire batch. Red-team exceptions are retained as explicit error rows. Phoenix experiment
registration is optional because the live evaluator is the source of truth.

## Security and privacy

- Configuration is typed and centralized in `tracelog/config.py`.
- `.env` is untracked; production credentials belong in Secret Manager.
- `OPENAI_STORE_RESPONSES=false` is the default.
- System-prompt override is restricted to test sessions and an optional shared secret.
- Test spans are excluded from supervision.
- Inputs are length-bounded at the public FastAPI surfaces.

## Verification strategy

Offline tests mock OpenAI and MCP calls and cover classification, root-cause analysis,
remediation, holdout novelty, security gates, reporting, and pipeline wiring. Ruff enforces
Python consistency. TypeScript checking plus a Vite production build verifies the primary UI.
A live acceptance run is separate because it requires real OpenAI, Phoenix, and Patient
credentials.
