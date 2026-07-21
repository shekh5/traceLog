# TraceLog implementation plan

Updated 2026-07-21 for the OpenAI GPT-5.6 build.

## Completed

- [x] Migrate all model calls to the OpenAI Responses API.
- [x] Assign GPT-5.6 Sol to complex analysis and Terra to high-volume evaluation.
- [x] Remove Gemini, OpenRouter, Google ADK, and Vertex Agent Engine runtime code.
- [x] Migrate the reference Patient to strict Responses function calling.
- [x] Keep model output structured with Pydantic and storage disabled by default.
- [x] Add typed remediation plans with enforced approval for non-prompt changes.
- [x] Add post-patch holdout generation, novelty filtering, and error accounting.
- [x] Surface remediation and holdout evidence in reports, MCP, and both UIs.
- [x] Update Cloud Run configuration, local environment templates, and architecture docs.
- [x] Pass offline tests, lint, type checking, and the React production build.
- [x] Add a visibly labelled, deterministic offline judge fixture through the real SSE UI.
- [x] Add GitHub Actions quality gates and weekly Dependabot configuration.
- [x] Add credential-free and live judge testing instructions.

## Credentialed acceptance

- [x] Configure `OPENAI_API_KEY`, Phoenix URL/key, and Patient endpoint.
- [x] Start Patient and dashboard; restart them after every `.env` change.
- [ ] Seed the canonical missing-policy and incomplete-order failures.
- [ ] Confirm Phoenix receives the Patient trace and TraceLog annotation.
- [ ] Run one complete supervision cycle and verify all nine dashboard stages.
- [ ] Confirm the prompt version and generated dataset appear in Phoenix.
- [ ] Confirm red-team reports fresh holdouts and no hidden execution errors.
- [ ] Review the generated postmortem and approve or reject the candidate prompt.

## Production hardening

- [ ] Replace lexical-only holdout filtering with semantic similarity and dataset lineage.
- [ ] Require a minimum number of valid holdouts before calling verification successful.
- [ ] Add authenticated service-to-service access around the Patient and dashboard.
- [ ] Review and remediate frontend dependency audit findings without forced upgrades.
- [ ] Add a deployment smoke test and a scheduled end-to-end canary.

The implemented change log is in [BUILD_WEEK_CHANGES.md](BUILD_WEEK_CHANGES.md).
