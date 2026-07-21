"""End-to-end canary event correlation stays scoped to its own incident."""

import importlib.util
from pathlib import Path
import sys

_PATH = Path(__file__).parents[1] / "scripts" / "e2e_canary.py"
_SPEC = importlib.util.spec_from_file_location("e2e_canary", _PATH)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)
CanaryTracker = _MODULE.CanaryTracker
STAGES = _MODULE.STAGES
STAGE_SEQUENCE = _MODULE.STAGE_SEQUENCE


def test_tracker_ignores_unrelated_incident():
    tracker = CanaryTracker("Canary: what's the refund window for orders shipped to Germany?")
    tracker.accept({"incident_id": "other", "stage": "watched", "detail": "different message"})
    assert tracker.incident_id is None


def test_tracker_requires_all_stages_and_verified_holdouts():
    message = "Canary: what's the refund window for orders shipped to Germany?"
    tracker = CanaryTracker(message)
    for stage in STAGE_SEQUENCE:
        tracker.accept(
            {
                "incident_id": "inc-1",
                "stage": stage,
                "detail": message.removeprefix("Canary: "),
                "payload": {"verification_passed": stage == "red_teamed"},
            }
        )
    assert tracker.complete
