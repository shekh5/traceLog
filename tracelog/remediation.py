"""GPT-5.6 remediation planner for prompt, code, tool, data, and config failures."""

from __future__ import annotations

from . import llm
from .events import bus
from .models import Incident, PipelineEvent, RemediationPlan, Stage

_SYSTEM = """You are a reliability engineer reviewing one failed AI-agent trace.
Choose the narrowest remediation type supported by the evidence. Propose an auditable
change and a regression test. Never claim a code edit was applied. Code, tool, data, and
configuration changes require human approval. Return the requested structured output."""


class RemediationPlanner:
    async def plan(self, inc: Incident) -> Incident:
        if inc.verdict is None or inc.root_cause is None:
            return inc
        prompt = (
            f"FAILURE CLASS: {inc.verdict.failure_class.value}\n"
            f"USER INPUT: {inc.span.input_text}\n"
            f"BAD OUTPUT: {inc.span.output_text}\n"
            f"TOOL CALLS: {inc.span.tool_calls}\n"
            f"ROOT CAUSE: {inc.root_cause.model_dump_json()}\n\n"
            "Create the smallest safe remediation plan."
        )
        inc.remediation = await llm.structured(prompt, RemediationPlan, system=_SYSTEM)
        inc.stage = Stage.REMEDIATED
        await bus.publish(
            PipelineEvent(
                incident_id=inc.incident_id,
                stage=Stage.REMEDIATED,
                title=f"Remediation: {inc.remediation.remediation_type.value}",
                detail=inc.remediation.summary,
                payload=inc.remediation.model_dump(mode="json"),
            )
        )
        return inc
