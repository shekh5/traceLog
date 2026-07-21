#!/usr/bin/env python3
"""Drive one real incident and require the complete supervision stage sequence."""

from __future__ import annotations

import json
import os
import queue
import sys
import threading
import time
from dataclasses import dataclass, field
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

STAGE_SEQUENCE = (
    "watched",
    "diagnosed",
    "root_caused",
    "remediated",
    "synthesized",
    "evaluated",
    "patched",
    "replayed",
    "red_teamed",
)
STAGES = set(STAGE_SEQUENCE)
DEFAULT_MESSAGE = "Canary: what's the refund window for orders shipped to Germany?"


@dataclass
class CanaryTracker:
    message: str
    incident_id: str | None = None
    stages: set[str] = field(default_factory=set)
    verification_passed: bool = False
    verification_reason: str = ""

    def accept(self, event: dict) -> None:
        stage = str(event.get("stage", ""))
        if self.incident_id is None:
            detail = str(event.get("detail", ""))
            message_marker = self.message.removeprefix("Canary: ")[:48]
            if stage != "watched" or message_marker not in detail:
                return
            self.incident_id = str(event.get("incident_id", ""))
        if event.get("incident_id") != self.incident_id:
            return
        if stage in STAGES:
            self.stages.add(stage)
        if stage == "red_teamed":
            payload = event.get("payload") or {}
            self.verification_passed = payload.get("verification_passed") is True
            self.verification_reason = str(payload.get("verification_reason", ""))

    @property
    def complete(self) -> bool:
        return self.stages == STAGES and self.verification_passed


def _json_request(url: str, *, method: str = "GET", token: str = "", body: dict | None = None):
    headers = {"Accept": "application/json"}
    data = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
    request = Request(url, data=data, headers=headers, method=method)
    with urlopen(request, timeout=30) as response:  # noqa: S310 - operator-provided URL
        return json.load(response)


def _stream_events(
    events_url: str,
    tracker: CanaryTracker,
    connected: threading.Event,
    updates: queue.Queue[str],
) -> None:
    try:
        request = Request(events_url, headers={"Accept": "text/event-stream"})
        with urlopen(request, timeout=1200) as response:  # noqa: S310 - operator-provided URL
            connected.set()
            for raw_line in response:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line.startswith("data:"):
                    continue
                event = json.loads(line[5:].strip())
                previous = set(tracker.stages)
                tracker.accept(event)
                if tracker.stages != previous:
                    updates.put(
                        f"{tracker.incident_id}: {event.get('stage')} - {event.get('title', '')}"
                    )
                if "red_teamed" in tracker.stages:
                    return
    except Exception as exc:  # surfaced to the main thread
        connected.set()
        updates.put(f"ERROR:{type(exc).__name__}: {exc}")


def main() -> int:
    dashboard = os.getenv("DASHBOARD_BASE_URL", "").rstrip("/")
    token = os.getenv("TRACELOG_SERVICE_API_KEY", "")
    timeout_seconds = int(os.getenv("CANARY_TIMEOUT_SECONDS", "900"))
    message = os.getenv("CANARY_MESSAGE", DEFAULT_MESSAGE)
    if not dashboard or not token:
        print("DASHBOARD_BASE_URL and TRACELOG_SERVICE_API_KEY are required.", file=sys.stderr)
        return 2

    try:
        health = _json_request(f"{dashboard}/healthz")
        if health.get("mode") != "live":
            raise RuntimeError("end-to-end canary requires dashboard mode=live")

        tracker = CanaryTracker(message)
        connected = threading.Event()
        updates: queue.Queue[str] = queue.Queue()
        thread = threading.Thread(
            target=_stream_events,
            args=(f"{dashboard}/events", tracker, connected, updates),
            daemon=True,
        )
        thread.start()
        if not connected.wait(timeout=15):
            raise TimeoutError("SSE event stream did not connect")

        result = _json_request(
            f"{dashboard}/ask",
            method="POST",
            token=token,
            body={"message": message},
        )
        if not result.get("reply"):
            raise RuntimeError("Patient returned no reply")

        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline and "red_teamed" not in tracker.stages:
            try:
                update = updates.get(timeout=5)
            except queue.Empty:
                continue
            if update.startswith("ERROR:"):
                raise RuntimeError(update)
            print(update, flush=True)

        missing = sorted(STAGES - tracker.stages)
        if missing:
            raise TimeoutError(f"canary timed out; missing stages: {', '.join(missing)}")
        if not tracker.verification_passed:
            raise RuntimeError(
                "red-team verification failed: "
                + (tracker.verification_reason or "no verification reason returned")
            )
        print(f"End-to-end canary passed for {tracker.incident_id}: all nine stages verified.")
        return 0
    except (HTTPError, URLError, OSError, ValueError, RuntimeError, TimeoutError) as exc:
        print(f"End-to-end canary failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
