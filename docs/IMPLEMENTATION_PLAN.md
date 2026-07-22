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

- [x] Replace lexical-only holdout filtering with OpenAI embedding similarity and dataset lineage.
- [x] Require a minimum number of valid holdouts before calling verification successful.
- [x] Add authenticated service-to-service access around the Patient and dashboard.
- [x] Remediate frontend dependency audit findings with a targeted Vite upgrade.
- [x] Add a deployment smoke test and a manual authenticated end-to-end canary.
- [x] Add HTTP authentication integration tests and a Playwright cockpit flow.

## Deployment and submission evidence

- [ ] Resolve usable OpenAI API quota and complete the credentialed acceptance checklist.
- [ ] Create fresh `replay-shared-secret` and `service-api-key` secrets in Secret Manager.
- [ ] Deploy Patient and dashboard and run `scripts/smoke_test.sh` against their URLs.
- [ ] Configure the GitHub canary URL variables and `TRACELOG_SERVICE_API_KEY` secret.
- [ ] Capture Phoenix trace, annotation, dataset, prompt-version, replay, and holdout evidence.
- [ ] Record the final demo and complete the Devpost submission.

The implemented change log is in [BUILD_WEEK_CHANGES.md](BUILD_WEEK_CHANGES.md).
