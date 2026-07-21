# OpenAI Build Week submission draft

Source of truth: [OpenAI Build Week on Devpost](https://openai.devpost.com/).
Deadline: **July 21, 2026 at 5:00 PM PDT**. Category: **Developer Tools**.

## Project name

TraceLog — continuous reliability for AI agents

## One-line pitch

TraceLog is a GPT-5.6 meta-agent that catches production-agent failures, turns them into
evaluation assets, and proves a safer prompt on the real agent before a human approves it.

## Project description

Production agents can return fluent, confident failures that ordinary uptime monitoring
cannot see. TraceLog watches an agent's OpenInference traces in Arize Phoenix and runs a
complete reliability loop whenever it finds a high-confidence hallucination, prompt drift,
or tool failure.

One incident becomes a structured diagnosis, causal chain, typed remediation plan,
Phoenix regression dataset, live baseline/candidate evaluation, versioned prompt patch,
exact-input replay, and a final set of unseen red-team holdouts. Holdouts are filtered with
OpenAI embeddings and retain incident, dataset, model, prompt-version, and similarity
lineage. Verification cannot pass unless enough valid holdouts complete and every patched
answer passes.

The product includes an authenticated React cockpit, a generic Patient adapter contract,
a published `tracelog-mcp` server, a CI prompt gate, self-tracing, and diagnostic
self-evaluation. A clearly labelled offline fixture lets judges test the full product UI
without spending API quota; it never presents fixture artifacts as live evidence.

## How GPT-5.6 is used

- GPT-5.6 Sol performs diagnosis, root-cause analysis, remediation planning, synthesis,
  and prompt patching through the Responses API with Pydantic structured outputs.
- GPT-5.6 Terra handles the repeated Patient and evaluator/judge calls.
- `text-embedding-3-small` performs semantic novelty filtering for unseen holdouts.
- OpenAI response storage is disabled by default.

## How Codex was used

Codex was the primary implementation partner for the OpenAI migration and hardening work:
repository analysis, Responses API conversion, strict Patient function calling, security
boundaries, offline fixture design, semantic holdout filtering, lineage, integration and
Playwright tests, CI/Dependabot review, deployment automation, and documentation. Key
decisions were verified through tests and protected pull requests instead of copied into
the repository without review.

## Links to provide

- Repository: https://github.com/shekh5/traceLog
- Public YouTube demo (1:54): https://youtu.be/CcQz8jVtWhI
- Runnable no-credential demo: https://shekh5.github.io/traceLog/
- Judge testing instructions: `docs/JUDGE_TESTING.md`
- Build Week implementation evidence: `docs/BUILD_WEEK_CHANGES.md` and the dated Git history
- Core Codex `/feedback` session ID: `019f8366-9fb4-72a1-98ce-14e1b95b11f1`

## Supported platforms

- Hosted fixture: current desktop and mobile browsers.
- Local runtime: validated on macOS and designed for Linux/container deployment.
- Windows: WSL2 is the recommended path; native Windows is not CI-validated.
- Prerequisites for local execution: Python 3.11+ and Node.js; Docker is optional.

## Final submission checklist

- [x] Developer Tools category selected.
- [x] Public repository and Apache-2.0 license.
- [x] README setup instructions and no-credential judge path.
- [x] GPT-5.6, Codex, and key implementation decisions explained.
- [x] Build Week additions and dated implementation evidence documented.
- [x] Supported platforms and no-rebuild judge path documented.
- [x] Public YouTube demo is under three minutes and includes audio explaining both Codex
      and GPT-5.6 usage.
- [x] `/feedback` session ID obtained and ready to enter.
- [x] All submission materials are in English.
- [ ] Entrant confirms age, location, ownership, and conflict-of-interest eligibility.
- [ ] Devpost form submitted before the deadline.

## Disclosed limitation — not a missing submission artifact

The hosted judge path is a deterministic, visibly labelled fixture. Live GPT-5.6 and Phoenix
execution remains credential- and quota-dependent and was not recorded as validation evidence.
The video and submission description must preserve this distinction. The implementation and
tests for the live path remain available in the repository.
