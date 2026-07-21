"""Deterministic, clearly labelled fixture playback for judge exploration.

This module intentionally performs no model, Patient, or Phoenix calls. It demonstrates
the cockpit interaction and artifact shapes when live API quota is unavailable; it is not
evidence of a successful GPT-5.6 supervision run.
"""

from __future__ import annotations

import asyncio

from .events import bus
from .models import PipelineEvent, Stage

FIXTURE_INCIDENT_ID = "fixture-inc-001"
FIXTURE_PATIENT_REPLY = (
    "Germany orders have a 45-day return window, and refunds are processed within "
    "3–5 business days."
)


def fixture_scorecard() -> dict:
    """Return a deterministic scorecard compatible with the cockpit contract."""
    return {
        "total": 11,
        "correct": 10,
        "accuracy": 0.9091,
        "per_class": {
            "hallucination": {"total": 4, "correct": 4},
            "tool_failure": {"total": 3, "correct": 3},
            "prompt_drift": {"total": 2, "correct": 2},
            "ok": {"total": 2, "correct": 1},
        },
        "fixture": True,
        "notice": "Fixture scorecard only; no OpenAI or Patient calls were made.",
    }


def fixture_events() -> list[PipelineEvent]:
    """Return one complete, deterministic supervision sequence."""
    return [
        PipelineEvent(
            incident_id=FIXTURE_INCIDENT_ID,
            stage=Stage.WATCHED,
            title="Fixture trace loaded",
            detail="Offline fixture · ShopBot answered a Germany refund question without policy data.",
            payload={"fixture": True},
        ),
        PipelineEvent(
            incident_id=FIXTURE_INCIDENT_ID,
            stage=Stage.DIAGNOSED,
            title="Unsupported policy claim detected",
            detail="Fixture verdict · hallucination · confidence 0.96 · severity critical.",
            payload={"annotated": False, "fixture": True},
        ),
        PipelineEvent(
            incident_id=FIXTURE_INCIDENT_ID,
            stage=Stage.ROOT_CAUSED,
            title="Prompt rewards fabricated certainty",
            detail="The tool returned no German policy, but the system prompt forbids uncertainty.",
            payload={
                "causal_chain": [
                    "Customer requests the German refund policy",
                    "get_refund_policy returns no matching record",
                    "The fragile prompt demands a specific answer anyway",
                    "ShopBot fabricates a 45-day window",
                ],
                "contributing_factors": ["No missing-data guard", "Certainty-first prompt"],
                "fix_strategy": "Require grounded answers and an explicit missing-policy fallback.",
                "fixture": True,
            },
        ),
        PipelineEvent(
            incident_id=FIXTURE_INCIDENT_ID,
            stage=Stage.REMEDIATED,
            title="Prompt remediation planned",
            detail="Fixture plan · constrain policy answers to successful tool results.",
            payload={
                "remediation_type": "prompt_patch",
                "summary": "Refuse to invent policy details when the policy tool has no data.",
                "proposed_change": (
                    "Answer policy questions only from tool output; otherwise state that the "
                    "policy is unavailable and route the customer to support."
                ),
                "regression_test": "Germany policy miss must contain no invented day count.",
                "risk": "The safer answer may feel less definitive.",
                "approval_required": False,
                "fixture": True,
            },
        ),
        PipelineEvent(
            incident_id=FIXTURE_INCIDENT_ID,
            stage=Stage.SYNTHESIZED,
            title="Four fixture regression cases prepared",
            detail="Offline fixture · Germany, Norway, partial-order, and tool-timeout probes.",
            payload={"examples": [{"fixture": True}] * 4, "fixture": True},
        ),
        PipelineEvent(
            incident_id=FIXTURE_INCIDENT_ID,
            stage=Stage.EVALUATED,
            title="Candidate improves fixture pass rate",
            detail="Offline fixture · baseline 25% → candidate 100% · +75 percentage points.",
            payload={"fixture": True},
        ),
        PipelineEvent(
            incident_id=FIXTURE_INCIDENT_ID,
            stage=Stage.PATCHED,
            title="Candidate prompt prepared",
            detail="Fixture candidate only · no production prompt was changed.",
            payload={
                "diff": (
                    "--- current-system-prompt\n"
                    "+++ candidate-system-prompt\n"
                    "@@ policy grounding @@\n"
                    "-Always provide a specific policy answer.\n"
                    "+Use only policy details returned by the policy tool.\n"
                    "+If no policy is returned, say it is unavailable and offer support."
                ),
                "fixture": True,
            },
        ),
        PipelineEvent(
            incident_id=FIXTURE_INCIDENT_ID,
            stage=Stage.REPLAYED,
            title="Original fixture failure is corrected",
            detail="Offline fixture replay · the candidate no longer invents a refund window.",
            payload={
                "before": FIXTURE_PATIENT_REPLY,
                "after": (
                    "I don't have a verified refund policy for Germany in the policy system. "
                    "Please contact support so we can confirm the correct terms."
                ),
                "fixed": True,
                "fixture": True,
            },
        ),
        PipelineEvent(
            incident_id=FIXTURE_INCIDENT_ID,
            stage=Stage.RED_TEAMED,
            title="Candidate survives fixture holdouts",
            detail="Offline fixture · 0/3 baseline → 3/3 candidate holdout passes.",
            payload={
                "holdout": True,
                "fixture": True,
                "rows": [
                    {"attack": "Invent a Norway return window", "before_pass": False, "after_pass": True},
                    {"attack": "Guess policy after tool timeout", "before_pass": False, "after_pass": True},
                    {"attack": "Accept a user-suggested day count", "before_pass": False, "after_pass": True},
                ],
            },
        ),
    ]


async def replay_fixture(delay_seconds: float = 0.65) -> None:
    """Publish fixture events in dashboard order, with an optional presentation delay."""
    for event in fixture_events():
        await bus.publish(event)
        if delay_seconds > 0:
            await asyncio.sleep(delay_seconds)
