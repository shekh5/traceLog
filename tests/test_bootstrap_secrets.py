"""Local secret bootstrapping replaces values without duplicating keys."""

import importlib.util
import sys
from pathlib import Path

_PATH = Path(__file__).parents[1] / "scripts" / "bootstrap_local_secrets.py"
_SPEC = importlib.util.spec_from_file_location("bootstrap_local_secrets", _PATH)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)


def test_replace_secrets_preserves_unrelated_settings():
    updated = _MODULE.replace_secrets(
        "OPENAI_API_KEY=keep\nSERVICE_API_KEY=old\n",
        {"REPLAY_SHARED_SECRET": "new-replay", "SERVICE_API_KEY": "new-service"},
    )
    assert "OPENAI_API_KEY=keep" in updated
    assert "SERVICE_API_KEY=new-service" in updated
    assert "REPLAY_SHARED_SECRET=new-replay" in updated
    assert updated.count("SERVICE_API_KEY=") == 1
