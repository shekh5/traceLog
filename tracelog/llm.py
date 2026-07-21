"""OpenAI GPT-5.6 Responses API gateway shared by TraceLog's reasoning stages.

Every model call stays behind ``structured`` or ``text`` so pipeline modules remain
provider-agnostic and easy to mock. Responses are not stored by default because
production traces can contain customer data.
"""

from __future__ import annotations

from typing import TypeVar

from openai import AsyncOpenAI
from openai.types.shared.reasoning_effort import ReasoningEffort
from openai.types.shared_params.reasoning import Reasoning
from pydantic import BaseModel

from .config import get_settings

T = TypeVar("T", bound=BaseModel)


def _client() -> AsyncOpenAI:
    s = get_settings()
    if not s.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required for TraceLog's GPT-5.6 runtime")
    return AsyncOpenAI(
        api_key=s.openai_api_key,
        max_retries=s.openai_max_retries,
        timeout=s.openai_timeout_seconds,
    )


def _reasoning(effort: ReasoningEffort | None) -> Reasoning:
    value = effort or get_settings().openai_reasoning_effort
    return {"effort": value}


async def structured(
    prompt: str,
    schema: type[T],
    *,
    system: str = "",
    temperature: float | None = None,
    model: str | None = None,
    reasoning_effort: ReasoningEffort | None = None,
) -> T:
    """Return a Pydantic-validated GPT-5.6 response.

    ``temperature`` remains in the signature for source compatibility with the
    previous gateway, but is intentionally not sent to GPT-5.6 reasoning requests.
    Determinism is enforced by the schema, prompt contract, and evaluation suite.
    """

    del temperature
    s = get_settings()
    response = await _client().responses.parse(
        model=model or s.openai_model,
        instructions=system or None,
        input=prompt,
        text_format=schema,
        reasoning=_reasoning(reasoning_effort),
        store=s.openai_store_responses,
    )
    parsed = getattr(response, "output_parsed", None)
    if parsed is not None:
        return parsed

    # Defensive compatibility with SDK releases that expose parsed content only
    # on the message content item.
    for output in response.output:
        if getattr(output, "type", None) != "message":
            continue
        for item in getattr(output, "content", []):
            refusal = getattr(item, "refusal", None)
            if refusal:
                raise ValueError(f"GPT-5.6 refused the structured request: {refusal}")
            item_parsed = getattr(item, "parsed", None)
            if item_parsed is not None:
                return item_parsed
    raise ValueError("GPT-5.6 returned no parseable structured output")


async def text(
    prompt: str,
    *,
    system: str = "",
    temperature: float | None = None,
    model: str | None = None,
    reasoning_effort: ReasoningEffort | None = None,
) -> str:
    """Return plain text from GPT-5.6 through the Responses API."""

    del temperature
    s = get_settings()
    response = await _client().responses.create(
        model=model or s.openai_model,
        instructions=system or None,
        input=prompt,
        reasoning=_reasoning(reasoning_effort),
        store=s.openai_store_responses,
    )
    return response.output_text or ""


async def embeddings(texts: list[str], *, model: str | None = None) -> list[list[float]]:
    """Return embeddings in input order for semantic novelty checks."""
    if not texts:
        return []
    s = get_settings()
    response = await _client().embeddings.create(
        model=model or s.embedding_model,
        input=texts,
        encoding_format="float",
    )
    ordered = sorted(response.data, key=lambda item: item.index)
    if len(ordered) != len(texts):
        raise ValueError("OpenAI returned an incomplete embedding batch")
    return [item.embedding for item in ordered]
