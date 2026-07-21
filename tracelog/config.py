"""Central typed configuration. All env access goes through here (NFR-4)."""

from __future__ import annotations

from functools import lru_cache
from hmac import compare_digest

from dotenv import load_dotenv
from openai.types.shared.reasoning_effort import ReasoningEffort
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(override=True)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # OpenAI GPT-5.6 model roles. Sol handles quality-critical reasoning; Terra
    # handles repeated live-agent/evaluation calls where cost and latency matter.
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.6-sol"
    evaluator_model: str = "gpt-5.6-terra"
    patient_model: str = "gpt-5.6-terra"
    openai_reasoning_effort: ReasoningEffort = "medium"
    evaluator_reasoning_effort: ReasoningEffort = "low"
    patient_reasoning_effort: ReasoningEffort = "low"
    openai_store_responses: bool = False
    openai_timeout_seconds: float = 300.0
    openai_max_retries: int = 5

    # Arize Phoenix (partner MCP)
    phoenix_base_url: str = "https://app.phoenix.arize.com"
    phoenix_api_key: str = "replace-me"
    phoenix_mcp_command: str = "npx"
    phoenix_mcp_args: str = "-y,@arizeai/phoenix-mcp@latest"
    patient_project: str = "patient-prod"
    meta_project: str = "tracelog-meta"

    # TraceLog tuning
    poll_interval_seconds: int = 60
    diagnosis_confidence_threshold: float = 0.7
    synth_dataset_size: int = 12
    demo_eval_cases: int = 4
    redteam_holdout_cases: int = 6
    redteam_min_valid_holdouts: int = 3

    # Judge-safe fixture playback. This never calls OpenAI or Phoenix and must remain
    # visibly labelled in the cockpit so recorded evidence cannot be confused with a
    # live GPT-5.6 supervision run.
    offline_demo_mode: bool = False
    offline_demo_delay_seconds: float = 0.65

    # Introspection / on-product depth
    self_trace_enabled: bool = True       # trace TraceLog's own reasoning into META_PROJECT
    phoenix_experiments_enabled: bool = False  # also register A/B as a real Phoenix experiment

    # State backend
    state_backend: str = "firestore"  # firestore | gcs | local
    firestore_collection: str = "tracelog_state"

    # Dashboard (defaults match the documented local ports; .env overrides)
    dashboard_port: int = 8085
    patient_endpoint: str = "http://localhost:8082/chat"

    # Supervised-agent ("Patient") integration — generic, NOT ShopBot-specific.
    # baseline_prompt_file: file holding the supervised agent's CURRENT system prompt
    # (tracelog/baseline.py resolver; unset = extract from the trace, else demo ShopBot).
    # patient_prompt_name: the Phoenix prompt name candidate patches are versioned under.
    baseline_prompt_file: str | None = None
    patient_prompt_name: str = "patient-shopbot-system"

    # Shared secret for the Patient's system_override path (SECURITY). When set, the
    # Patient honors system_override only if the caller also sends it in the
    # X-TraceLog-Token header. Unset = local-dev mode (session_id gate only).
    replay_shared_secret: str | None = None

    # Optional bearer key for cost-incurring service operations. When configured,
    # Patient /chat and dashboard /ask + /selfeval require Authorization: Bearer.
    # Leave unset only for local development or when an upstream identity proxy
    # already enforces access.
    service_api_key: str | None = None

    @field_validator("phoenix_base_url")
    @classmethod
    def normalize_phoenix_base_url(cls, value: str) -> str:
        """Keep appended Phoenix API and UI paths from producing double slashes."""
        return value.rstrip("/")

    @property
    def phoenix_mcp_arg_list(self) -> list[str]:
        return [a for a in self.phoenix_mcp_args.split(",") if a]

    @property
    def is_openai(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def model_provider(self) -> str:
        """Phoenix `upsert-prompt` provider for the GPT-5.6 reasoning core."""
        return "OPENAI"

    @property
    def model_name(self) -> str:
        """The quality-critical model used by TraceLog's reasoning stages."""
        return self.openai_model


@lru_cache
def get_settings() -> Settings:
    return Settings()


def replay_auth_headers() -> dict[str, str]:
    """Headers TraceLog attaches when calling the Patient with a system_override.

    Empty when no REPLAY_SHARED_SECRET is configured (local dev), so existing
    deployments keep working until the secret is set on both services.
    """
    s = get_settings()
    headers = {"X-TraceLog-Token": s.replay_shared_secret} if s.replay_shared_secret else {}
    if s.service_api_key:
        headers["Authorization"] = f"Bearer {s.service_api_key}"
    return headers


def service_key_is_valid(authorization: str | None) -> bool:
    """Validate the optional service bearer key without timing-sensitive equality."""
    expected = get_settings().service_api_key
    if not expected:
        return True
    scheme, separator, supplied = (authorization or "").partition(" ")
    return separator == " " and scheme.lower() == "bearer" and compare_digest(supplied, expected)


def reload_settings() -> Settings:
    """Re-read .env and rebuild the cached Settings.

    `get_settings()` is cached for the process lifetime, and `load_dotenv` only runs at
    import — so editing `.env` does not take effect until restart (this bit us when adding
    the OpenAI key). Long-running servers should still be restarted, but this gives scripts
    and tests a way to pick up a changed `.env` without a fresh process.
    """
    get_settings.cache_clear()
    load_dotenv(override=True)
    return get_settings()
