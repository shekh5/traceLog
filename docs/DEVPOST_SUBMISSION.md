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
- Public YouTube demo (<3:00): **TODO**
- Runnable demo or testing path: use the offline fixture instructions in `README.md`, or
  provide the deployed dashboard URL when Cloud Run is ready.
- Core Codex `/feedback` session ID: **TODO — obtain from this Codex task before submitting**

## Final submission checklist

- [x] Developer Tools category selected.
- [x] Public repository and Apache-2.0 license.
- [x] README setup instructions and no-credential judge path.
- [x] GPT-5.6, Codex, and key implementation decisions explained.
- [ ] Usable OpenAI project quota confirmed.
- [ ] Live Phoenix evidence and deployed URL captured.
- [ ] Public YouTube demo is under three minutes and includes audio explaining both Codex
      and GPT-5.6 usage.
- [ ] `/feedback` session ID entered.
- [ ] Devpost form submitted before the deadline.
