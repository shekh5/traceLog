"""OpenAI Responses gateway contracts without network calls."""

from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from tracelog import llm


class _Answer(BaseModel):
    value: str


class _FakeResponses:
    def __init__(self) -> None:
        self.parse_kwargs = None
        self.create_kwargs = None

    async def parse(self, **kwargs):
        self.parse_kwargs = kwargs
        return SimpleNamespace(output_parsed=_Answer(value="typed"), output=[])

    async def create(self, **kwargs):
        self.create_kwargs = kwargs
        return SimpleNamespace(output_text="plain")


@pytest.mark.asyncio
async def test_structured_uses_responses_parse_and_disables_storage(monkeypatch):
    responses = _FakeResponses()
    monkeypatch.setattr(llm, "_client", lambda: SimpleNamespace(responses=responses))

    answer = await llm.structured("question", _Answer, system="contract")

    assert answer.value == "typed"
    assert responses.parse_kwargs["model"] == "gpt-5.6-sol"
    assert responses.parse_kwargs["text_format"] is _Answer
    assert responses.parse_kwargs["reasoning"] == {"effort": "medium"}
    assert responses.parse_kwargs["store"] is False


@pytest.mark.asyncio
async def test_text_uses_responses_create(monkeypatch):
    responses = _FakeResponses()
    monkeypatch.setattr(llm, "_client", lambda: SimpleNamespace(responses=responses))

    answer = await llm.text("question", model="gpt-5.6-terra", reasoning_effort="low")

    assert answer == "plain"
    assert responses.create_kwargs["model"] == "gpt-5.6-terra"
    assert responses.create_kwargs["reasoning"] == {"effort": "low"}
