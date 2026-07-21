"""Unit tests for the schema-coupled Phoenix gateway (NFR-10 contract)."""

import json

import httpx
import pytest

from tracelog.config import Settings
from tracelog.phoenix_mcp import PhoenixMCP
from tracelog.phoenix_mcp import _as_list, _id_of, normalize_span


def test_id_of_extracts_known_keys():
    assert _id_of({"dataset_id": "ds-1"}, "fb") == "ds-1"
    assert _id_of({"id": 42}, "fb") == "42"
    assert _id_of("exp-9", "fb") == "exp-9"
    assert _id_of({"unrelated": 1}, "fallback") == "fallback"


def test_as_list_unwraps_envelopes():
    assert _as_list({"spans": [1, 2]}) == [1, 2]
    assert _as_list([3]) == [3]
    assert _as_list(None) == []


def test_normalize_span_maps_core_fields():
    # The Patient emits FLAT dotted OpenInference attributes (patient/agent.py:
    # span.set_attribute("input.value", ...)), which normalize_span reads directly.
    raw = {
        "context": {"span_id": "s1", "trace_id": "t1"},
        "start_time": "2026-05-17T00:00:00Z",
        "attributes": {"input.value": "hi", "output.value": "there"},
    }
    s = normalize_span(raw, "patient-prod")
    assert s.span_id == "s1"
    assert s.trace_id == "t1"
    assert s.input_text == "hi"
    assert s.output_text == "there"
    assert s.project == "patient-prod"


def test_normalize_span_handles_nested_attributes():
    # Some Phoenix MCP builds return attributes NESTED rather than flat-dotted.
    # normalize_span must still extract input/output, else the Watcher silently
    # drops the span (no input/output text => not a candidate tree).
    raw = {
        "context": {"span_id": "s2", "trace_id": "t2"},
        "start_time": "2026-05-17T00:00:00Z",
        "attributes": {"input": {"value": "hi"}, "output": {"value": "there"}},
    }
    s = normalize_span(raw, "patient-prod")
    assert s.input_text == "hi"
    assert s.output_text == "there"


@pytest.mark.asyncio
async def test_annotation_rest_fallback_uses_supported_payload():
    observed: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        observed["authorization"] = request.headers.get("Authorization")
        observed["url"] = str(request.url)
        observed["body"] = json.loads(request.content)
        return httpx.Response(200, json={"data": [{"id": "ann-rest-1"}]})

    settings = Settings(
        phoenix_base_url="https://phoenix.example",
        phoenix_api_key="test-phoenix-key",
    )
    gateway = PhoenixMCP(settings, http_transport=httpx.MockTransport(handler))
    annotation_id = await gateway._annotate_via_rest(
        "span-1", "hallucination", 0.97, "Unsupported claim"
    )

    assert annotation_id == "ann-rest-1"
    assert observed["authorization"] == "Bearer test-phoenix-key"
    assert observed["url"].endswith("/v1/span_annotations?sync=true")
    assert observed["body"]["data"][0]["result"]["label"] == "hallucination"
