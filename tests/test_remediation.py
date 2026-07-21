"""Remediation planner: structured GPT-5.6 engineering plan and event wiring."""

from datetime import datetime, timezone

import pytest

from tracelog.models import (
    FailureClass,
    Incident,
    RemediationPlan,
    RemediationType,
    RootCause,
    SpanRecord,
    Stage,
    Verdict,
)
from tracelog.remediation import RemediationPlanner


def _incident() -> Incident:
    inc = Incident.from_span(
        SpanRecord(
            span_id="s1",
            trace_id="t1",
            project="patient-prod",
            started_at=datetime.now(timezone.utc),
            input_text="Where is order A1002?",
            output_text="It arrives Friday by DHL.",
            tool_calls=[{"name": "lookup_order", "result": {"carrier": None}}],
        )
    )
    inc.verdict = Verdict(
        failure_class=FailureClass.TOOL_FAILURE,
        confidence=0.95,
        rationale="Carrier was invented.",
    )
    inc.root_cause = RootCause(
        summary="Missing carrier was treated as success.",
        culprit="tool result validation",
        causal_chain=["tool returned null", "agent fabricated carrier"],
        fix_strategy="Validate required tool fields.",
    )
    return inc


@pytest.mark.asyncio
async def test_remediation_planner_enriches_incident(monkeypatch):
    async def fake_structured(*args, **kwargs):
        return RemediationPlan(
            remediation_type=RemediationType.TOOL_FIX,
            summary="Reject incomplete order records.",
            evidence=["carrier is null"],
            proposed_change="Validate carrier before answering.",
            regression_test="Incomplete orders must produce an escalation.",
            risk="low",
        )

    monkeypatch.setattr("tracelog.remediation.llm.structured", fake_structured)
    result = await RemediationPlanner().plan(_incident())
    assert result.stage == Stage.REMEDIATED
    assert result.remediation is not None
    assert result.remediation.remediation_type == RemediationType.TOOL_FIX
    assert result.remediation.approval_required is True


def test_non_prompt_remediation_cannot_disable_approval():
    plan = RemediationPlan(
        remediation_type=RemediationType.CODE_FIX,
        summary="Validate tool output.",
        proposed_change="Add a schema check.",
        regression_test="Reject incomplete records.",
        risk="low",
        approval_required=False,
    )
    assert plan.approval_required is True
