"""Judge-safe offline fixture playback remains complete and explicitly labelled."""

import pytest

from tracelog import offline_demo
from tracelog.models import Stage


def test_fixture_covers_the_complete_pipeline_without_live_links():
    events = offline_demo.fixture_events()

    assert [event.stage for event in events] == list(Stage)
    assert len({event.incident_id for event in events}) == 1
    assert all(event.payload.get("fixture") is True for event in events)
    assert all(event.phoenix_url is None for event in events)


def test_fixture_scorecard_is_explicit_and_consistent():
    scorecard = offline_demo.fixture_scorecard()

    assert scorecard["fixture"] is True
    assert scorecard["correct"] == sum(v["correct"] for v in scorecard["per_class"].values())
    assert scorecard["total"] == sum(v["total"] for v in scorecard["per_class"].values())


@pytest.mark.asyncio
async def test_fixture_replay_publishes_every_event(monkeypatch):
    published = []

    async def capture(event):
        published.append(event)

    monkeypatch.setattr(offline_demo.bus, "publish", capture)
    await offline_demo.replay_fixture(delay_seconds=0)

    assert [event.stage for event in published] == list(Stage)
