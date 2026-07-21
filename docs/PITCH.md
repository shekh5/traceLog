# TraceLog: The Meta-Agent That Watches Other Agents

*Pitch for OpenAI Build Week, Developer Tools category. This is the narrative for the
website, Devpost page, and demo video.*

## The one-liner

Every production LLM agent fails silently. TraceLog is an agent whose only job is to catch those failures, prove a fix, and attack its own fix, all without a human in the loop.

## The problem

Teams running LLM agents in production share one unsolved problem: agents fail quietly and confidently. A support bot invents a refund policy that does not exist. A tool call returns nothing and the agent papers over the gap with a fabricated delivery date. A model upgrade drifts the prompt's behavior overnight.

Today this is caught by humans staring at trace dashboards, sampling conversations by hand, writing eval datasets manually, and editing prompts on intuition. It is slow, it does not scale, and most failures are never caught at all.

## The idea

TraceLog closes that loop autonomously. It is, recursively, an agent that supervises other agents. It connects to Arize Phoenix, the observability platform the supervised agent already exports traces to, and runs the exact workflow Phoenix was built for, but automated, continuous, and self-improving:

1. **Watch.** Poll fresh production traces from Phoenix.
2. **Diagnose.** An LLM-as-judge classifies each failure: hallucination, prompt drift, or tool failure, with a confidence and severity.
3. **Root-cause.** Pinpoint the culprit and a causal chain: which tool returned nothing, which prompt line told the model to fabricate.
4. **Remediate.** Produce an auditable, typed plan with human approval boundaries.
5. **Synthesize.** Turn that single failure into an adversarial eval dataset, written back into Phoenix.
6. **Evaluate.** Score the current prompt against the dataset, live, on the real agent.
7. **Patch.** Rewrite the system prompt to close the failure, registered as a Phoenix prompt version with a unified diff.
8. **Replay.** Re-run the exact original failing input on the patched prompt and judge whether this specific case is now fixed.
9. **Red-team.** Generate embedding-filtered unseen holdouts, run both prompts, and require every valid patched result to pass.

One incident in, one verified, evidence-backed prompt patch out. Every artifact (annotation, dataset, experiment scores, prompt version) lands in Phoenix where the team already works.

## The recursive twist

TraceLog also watches itself. Its own reasoning is traced into a second Phoenix project, and a built-in self-evaluation runs a hand-labeled trap library through its own Diagnostician and scores its diagnostic accuracy against ground truth. The supervisor is as observable and as measurable as the agents it supervises.

## What you see in the demo

A live cockpit. You type a customer message; the victim agent ("the Patient", a deliberately fragile ShopBot) confidently invents a refund policy. Seconds later TraceLog catches it in the trace feed and the full pipeline plays out on screen: the diagnosis, the causal chain, the synthesized attack set, baseline versus candidate pass rates, the prompt diff, the before-and-after replay, and the red-team table. Then you press "Grade my own diagnoses" and TraceLog scores itself.

## Why it fits OpenAI Build Week

- **Technological implementation.** GPT-5.6 performs multiple distinct structured reasoning
  roles, OpenAI embeddings protect holdout novelty, and the repository ships protected
  Python, web, and browser CI rather than a thin API wrapper.
- **Design.** The cockpit turns a complex reliability workflow into one coherent,
  inspectable cascade, with a no-credential judge path that is explicitly labelled.
- **Potential impact.** Every production LLM team has this exact pain and currently solves
  it with manual trace review and hand-authored evals.
- **Quality of the idea.** Almost every entry is an agent; TraceLog is the agent that
  measures and improves those agents, including itself.

## Built with

OpenAI GPT-5.6 through the Responses API, Arize Phoenix through the partner MCP server,
FastAPI on Cloud Run, Firestore for durable state, and Secret Manager for keys.

## The tagline

Agents fail silently. TraceLog hears them.
