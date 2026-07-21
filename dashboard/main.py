"""Dashboard service (FR-DB1..DB5).

Serves the self-contained cockpit (dashboard/ui/index.html — no build step),
streams pipeline events over SSE, and proxies the "send customer message" box to
the Patient so the whole loop is driveable live on camera.
"""

from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager, suppress
from pathlib import Path

import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from tracelog.config import get_settings, service_key_is_valid
from tracelog.events import bus
from tracelog.loop_agent import SupervisionPipeline

_UI = Path(__file__).resolve().parent / "ui"
# The React/Vite frontend (web/dist, built by the Docker webbuild stage or a local
# `npm run build`). When present it is the primary UI at "/"; the self-contained
# cockpit remains available at /cockpit (and is the fallback when dist is absent).
_WEB_DIST = Path(__file__).resolve().parent.parent / "web" / "dist"


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    if settings.offline_demo_mode:
        print("Offline fixture demo enabled; live Patient, OpenAI, and Phoenix calls are disabled.")
        yield
        return

    from tracelog.instrumentation import init_self_tracing

    init_self_tracing()  # trace TraceLog's own reasoning into the tracelog-meta project

    async def watcher_loop():
        print("Starting background SupervisionPipeline watcher loop...")
        pipeline = SupervisionPipeline()
        while True:
            try:
                result = await pipeline.run_once()
                if result:
                    # After a full cycle (diagnose → red-team), wait longer to let
                    # replay/red-team spans flush and get marked as seen before the
                    # next poll picks them up as fresh incidents.
                    await asyncio.sleep(30)
                else:
                    await asyncio.sleep(10)  # nothing found, poll again soon
            except Exception as e:
                print(f"Background SupervisionPipeline error: {e}")
                await asyncio.sleep(15)

    task = asyncio.create_task(watcher_loop())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


app = FastAPI(title="TraceLog Dashboard", lifespan=lifespan)


class Ask(BaseModel):
    # max_length bounds LLM cost/abuse via the public demo proxy.
    message: str = Field(min_length=1, max_length=2000)


@app.get("/events")
async def events():
    async def gen():
        async for ev in bus.subscribe():
            yield {"event": "pipeline", "data": json.dumps(ev.model_dump(mode="json"))}

    return EventSourceResponse(gen(), ping=15)


@app.post("/ask")
async def ask(req: Ask, authorization: str | None = Header(default=None)) -> dict:
    """Drive the demo: send a customer message to the Patient (FR-DB3)."""
    s = get_settings()
    if not service_key_is_valid(authorization):
        raise HTTPException(status_code=401, detail="A valid bearer token is required.")
    if s.offline_demo_mode:
        from tracelog.offline_demo import FIXTURE_PATIENT_REPLY, replay_fixture

        asyncio.create_task(replay_fixture(s.offline_demo_delay_seconds))
        return {
            "reply": FIXTURE_PATIENT_REPLY,
            "demo_mode": "offline_fixture",
            "notice": "Fixture playback only; no OpenAI or Phoenix calls were made.",
        }
    async with httpx.AsyncClient(timeout=300) as c:
        headers = {"Authorization": authorization} if authorization else {}
        r = await c.post(s.patient_endpoint, json={"message": req.message}, headers=headers)
        r.raise_for_status()
        return r.json()


@app.post("/selfeval", response_model=None)
async def selfeval(authorization: str | None = Header(default=None)) -> dict | JSONResponse:
    """TraceLog grades its OWN diagnostic accuracy against labeled ground truth.

    The introspection / self-improvement signal the Arize track rewards.
    """
    s = get_settings()
    if not service_key_is_valid(authorization):
        raise HTTPException(status_code=401, detail="A valid bearer token is required.")
    if s.offline_demo_mode:
        from tracelog.offline_demo import fixture_scorecard

        return fixture_scorecard()

    from tracelog.selfeval import SelfEvaluator

    try:
        # concurrency=1 avoids a burst while the shared LLM layer handles retries.
        card = await SelfEvaluator().evaluate(concurrency=1)
    except Exception as exc:  # surface as JSON so the cockpit can render it, not raw HTML 500
        detail = str(exc)
        hint = " (check OpenAI project limits and billing)" if "429" in detail else ""
        return JSONResponse(
            status_code=200,
            content={"error": f"self-eval failed: {type(exc).__name__}: {detail}{hint}"},
        )
    return {**card.model_dump(mode="json"), "accuracy": card.accuracy}


@app.get("/how", response_class=HTMLResponse)
@app.get("/how-it-works", response_class=HTMLResponse)
async def how_it_works() -> str:
    """Self-contained animated explainer of every TraceLog workflow (FR-DB5).

    A clean alias for dashboard/ui/how-it-works.html (also reachable directly via the
    StaticFiles mount). No build step — inline SVG/CSS/JS, same theme as the cockpit.
    """
    page = _UI / "how-it-works.html"
    if page.is_file():
        return page.read_text(encoding="utf-8")
    return "<h1>how-it-works.html missing</h1>"


@app.get("/healthz")
async def healthz() -> dict:
    s = get_settings()
    return {
        "ok": True,
        "service": "dashboard",
        "ui": (_WEB_DIST / "index.html").is_file() or (_UI / "index.html").is_file(),
        "mode": "offline_fixture" if s.offline_demo_mode else "live",
        "auth_required": bool(s.service_api_key),
    }


# Static mounts go last so /events, /ask, /selfeval, /healthz keep priority.
# React frontend (web/dist) at "/" when built; single-file cockpit at /cockpit
# always (and at "/" as the fallback when no dist exists).
_HAS_WEB = (_WEB_DIST / "index.html").is_file()
if (_UI / "index.html").is_file():
    app.mount(
        "/cockpit" if _HAS_WEB else "/",
        StaticFiles(directory=str(_UI), html=True),
        name="cockpit",
    )
if _HAS_WEB:
    app.mount("/", StaticFiles(directory=str(_WEB_DIST), html=True), name="ui")
elif not (_UI / "index.html").is_file():

    @app.get("/", response_class=HTMLResponse)
    async def _missing() -> str:
        return (
            "<body style='background:#070707;color:#F4F1EA;font-family:monospace;"
            "padding:48px;line-height:1.6'>"
            "<h1>TraceLog cockpit missing</h1>"
            "<p>Expected <code>web/dist/index.html</code> or "
            "<code>dashboard/ui/index.html</code>.</p></body>"
        )
