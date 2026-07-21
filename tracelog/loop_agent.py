"""The provider-independent TraceLog supervision pipeline (FR-L1..L3)."""

from __future__ import annotations

from .baseline import resolve_baseline_prompt
from .diagnostician import Diagnostician
from .evaluator import Evaluator
from .models import Incident
from .patcher import Patcher
from .redteam import RedTeam
from .remediation import RemediationPlanner
from .replay import TraceReplay
from .rootcause import RootCauseAnalyst
from .state import get_state
from .synthesizer import Synthesizer
from .watcher import Watcher


class SupervisionPipeline:
    """Watch -> diagnose -> root cause -> remediate -> evaluate -> patch -> verify.

    One incident is processed per cycle and deduplicated by span id.
    """

    def __init__(self) -> None:
        self.watcher = Watcher()
        self.diagnostician = Diagnostician()
        self.rootcause = RootCauseAnalyst()
        self.remediation = RemediationPlanner()
        self.synthesizer = Synthesizer()
        self.evaluator = Evaluator()
        self.patcher = Patcher()
        self.replay = TraceReplay()
        self.redteam = RedTeam()
        self.state = get_state()

    async def run_once(self) -> Incident | None:
        """Process exactly one fresh failing incident, or return None (FR-L1)."""
        incidents = await self.watcher.poll()
        for inc in incidents:
            inc = await self.diagnostician.diagnose(inc)
            self.state.mark_seen(inc.span.span_id)  # FR-L3 dedupe regardless of verdict
            if inc.verdict is None or not inc.verdict.is_failure:
                continue

            inc = await self.rootcause.analyze(inc)          # why it broke
            inc = await self.remediation.plan(inc)          # engineering action
            inc = await self.synthesizer.synthesize(inc)      # eval generation
            # Resolve the supervised agent's CURRENT prompt once (file/trace/demo —
            # tracelog/baseline.py); Evaluator and Patcher both work from it.
            inc.baseline_prompt = resolve_baseline_prompt(inc.span)
            inc = await self.evaluator.run_baseline(inc, inc.baseline_prompt)
            inc = await self.patcher.propose(inc)             # prompt fixing
            inc = await self.evaluator.run_candidate(inc)
            inc = await self.replay.replay(inc)               # live trace replay
            inc = await self.redteam.attack(inc)              # adversarial testing
            self._write_postmortem(inc)                       # ready-to-paste report
            return inc  # yield after one full cycle (demo-deterministic)
        return None

    @staticmethod
    def _write_postmortem(inc: Incident) -> None:
        """Persist the auto-postmortem to reports/<incident_id>.md (best-effort)."""
        from pathlib import Path

        from .report import render_postmortem

        try:
            out = Path("reports")
            out.mkdir(exist_ok=True)
            (out / f"{inc.incident_id}.md").write_text(
                render_postmortem(inc), encoding="utf-8"
            )
        except OSError as exc:  # never let report I/O kill the supervision loop
            print(f"postmortem write failed: {exc}")
