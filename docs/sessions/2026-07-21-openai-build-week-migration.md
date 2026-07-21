# Session: OpenAI Build Week migration

## Scope

Converted TraceLog from the earlier Gemini/ADK hackathon runtime to an OpenAI GPT-5.6
reliability supervisor, then implemented the missing remediation and evaluation-integrity
work identified during project review.

## Decisions

- Use the Responses API everywhere. GPT-5.6 Sol owns quality-critical reasoning; Terra owns
  repeated Patient and evaluator calls.
- Keep Responses storage off by default because traces may contain customer data.
- Keep orchestration in ordinary async Python instead of retaining a vendor runtime wrapper.
- Treat non-prompt remediation as an approval-required plan, never an implied code deploy.
- Generate red-team probes after the candidate exists and keep them distinct from the
  development evaluation set.

## Changes

- Replaced provider configuration and shared LLM gateway.
- Migrated the Patient to strict Responses function calling.
- Added `RemediationPlan`, `RemediationPlanner`, and `Stage.REMEDIATED`.
- Rebuilt holdout red-team generation, filtering, execution-error accounting, and results.
- Updated the pipeline, postmortem, MCP result, React cockpit, and fallback cockpit.
- Removed Google ADK/Agent Engine code and dependencies.
- Updated deployment configuration and the current README/architecture/system-design docs.
- Added OpenAI wiring, remediation, approval-boundary, and holdout novelty tests.

## Verification

- `.venv/bin/pytest -q`: 46 passed.
- `.venv/bin/ruff check tracelog patient dashboard tests`: passed.
- `.venv/bin/mypy tracelog patient dashboard --ignore-missing-imports`: passed.
- `web/npm run build`: passed.
- `npm audit --omit=dev`: zero production vulnerabilities.
- `python3 -m compileall` and `git diff --check`: passed.

## Open items

- Run a credentialed end-to-end acceptance cycle against OpenAI and the target Phoenix
  project.
- Review three development-only frontend audit findings; the production dependency audit
  currently reports zero vulnerabilities.
- Build the Cloud Run image when a Docker daemon is available; the daemon was not running
  in this workspace session.
- Add semantic similarity and persistent lineage if holdout isolation needs a stronger
  production guarantee than the current lexical filter.

Configuration is cached; restart Patient and dashboard processes after changing `.env`.
