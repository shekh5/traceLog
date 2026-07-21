"""Build Week wiring: GPT-5.6 configuration and provider-independent pipeline."""

from tracelog.config import Settings, reload_settings
from tracelog import state
from tracelog.loop_agent import SupervisionPipeline


def test_gpt56_model_roles_are_defaults():
    settings = Settings(openai_api_key="test")
    assert settings.openai_model == "gpt-5.6-sol"
    assert settings.evaluator_model == "gpt-5.6-terra"
    assert settings.patient_model == "gpt-5.6-terra"
    assert settings.model_provider == "OPENAI"
    assert settings.model_name == "gpt-5.6-sol"
    assert settings.openai_store_responses is False


def test_pipeline_includes_remediation_stage(monkeypatch, tmp_path):
    monkeypatch.setenv("STATE_BACKEND", "local")
    monkeypatch.chdir(tmp_path)
    reload_settings()
    state._STATE_STORE = None
    pipeline = SupervisionPipeline()
    assert pipeline.remediation.__class__.__name__ == "RemediationPlanner"
