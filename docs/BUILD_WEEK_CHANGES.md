# OpenAI Build Week implementation

Implemented on branch `codex/openai-build-week` on 2026-07-21.

## Runtime migration

- Replaced Gemini, Vertex, OpenRouter, Google ADK, and Agent Engine dependencies with the
  OpenAI Python SDK and the Responses API.
- Added separate GPT-5.6 model roles: Sol for high-value reasoning and Terra for repeated
  evaluation/Patient traffic.
- Added explicit reasoning effort, retry, timeout, and response-storage configuration.
- Migrated Patient function calling to strict Responses function tools and stateless
  multi-turn replay with encrypted reasoning content.

## Reliability workflow

- Added a typed remediation stage covering prompt, code, tool, data, and configuration
  actions. Non-prompt work always requires approval.
- Rebuilt red-team as post-patch holdout generation instead of reusing development cases.
- Added lexical similarity filtering, requested/completed/error accounting, and error rows.
- Added remediation and holdout evidence to reports, MCP output, React UI, and fallback UI.

## Operations

- Updated local environment, VS Code MCP, Cloud Build, and VM startup configuration.
- Removed the obsolete Vertex Agent Engine entry point and ADK wiring test.
- Rewrote current architecture and system-design documentation for the implemented stack.

## Verification

- Offline Python tests: 46 passed.
- Ruff: clean.
- Mypy: clean with third-party missing imports ignored.
- React/TypeScript production build: successful.
- Production frontend dependency audit: zero vulnerabilities.
- Live OpenAI/Phoenix acceptance remains credential-dependent and was not run here.
