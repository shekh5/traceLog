import { useEffect, useMemo, useRef, useState } from "react";
import { Activity, Radar } from "lucide-react";
import { useEvents } from "../lib/useEvents";
import { DriveBox } from "./DriveBox";
import { EventCard } from "./EventCard";
import { PipelineRibbon } from "./PipelineRibbon";
import { SelfEval } from "./SelfEval";

export function Cockpit() {
  const { events, conn, mode, authRequired } = useEvents();
  const [token, setToken] = useState("");
  const fixture = mode === "offline_fixture";
  const feedRef = useRef<HTMLDivElement>(null);

  const lastIncident = events.length ? events[events.length - 1].incident_id : null;
  const activeStage = useMemo(() => {
    for (let i = events.length - 1; i >= 0; i--)
      if (events[i].incident_id === lastIncident) return events[i].stage;
    return null;
  }, [events, lastIncident]);

  const incidents = new Set(events.map((e) => e.incident_id)).size;
  const patched = events.filter((e) => e.stage === "patched").length;

  useEffect(() => {
    feedRef.current?.scrollTo({ top: feedRef.current.scrollHeight, behavior: "smooth" });
  }, [events.length]);

  const connStyle =
    conn === "live"
      ? { c: "#21C07A", t: "live" }
      : conn === "lost"
        ? { c: "#F0443E", t: "reconnecting…" }
        : { c: "#6C6A66", t: "connecting…" };

  return (
    <section id="cockpit" className="relative border-t border-line bg-ink-0">
      <div className="mx-auto max-w-7xl px-6 py-24">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <div className="eyebrow mb-3">
              {fixture ? "Offline fixture cockpit" : "Live supervision cockpit"}
            </div>
            <h2 className="font-display text-[clamp(1.8rem,3.6vw,3rem)] font-bold tracking-tightish">
              {fixture ? "Replay a labelled supervision example" : "Watch it catch a lie in real time"}
            </h2>
          </div>
          <div
            className="inline-flex items-center gap-2 rounded-full border border-line2 bg-ink-1 px-3 py-1.5 font-mono text-xs"
            style={{ color: connStyle.c }}
          >
            <span
              className="h-1.5 w-1.5 rounded-full"
              style={{ background: connStyle.c, boxShadow: `0 0 0 3px ${connStyle.c}33` }}
            />
            {fixture ? "fixture · no API calls" : connStyle.t}
          </div>
        </div>

        {fixture && (
          <div className="mt-5 rounded-lg border border-signal/35 bg-signal/10 px-4 py-3 font-mono text-xs text-[#f0c987]">
            OFFLINE FIXTURE — deterministic sample data for UI evaluation. This is not a live
            GPT-5.6 or Phoenix result.
          </div>
        )}

        {authRequired && (
          <label className="mt-5 block rounded-lg border border-line2 bg-ink-1 px-4 py-3">
            <span className="font-mono text-[11px] uppercase tracking-wide2 text-slate">
              Service bearer token · kept in memory only
            </span>
            <input
              type="password"
              value={token}
              onChange={(event) => setToken(event.target.value)}
              autoComplete="off"
              className="mt-2 w-full rounded-md border border-line2 bg-ink-2 px-3 py-2 font-mono text-xs text-bone outline-none focus:border-signal"
              placeholder="Required to drive Patient and run self-evaluation"
            />
          </label>
        )}

        <div className="mt-6 rounded-xl border border-line bg-ink-1 px-4 py-3">
          <PipelineRibbon active={activeStage} />
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-[340px_1fr]">
          <div className="flex flex-col gap-5">
            <DriveBox fixture={fixture} token={token} />
            <div className="grid grid-cols-2 gap-3">
              <Stat icon={<Radar className="h-3.5 w-3.5" />} n={incidents} l="incidents" />
              <Stat icon={<Activity className="h-3.5 w-3.5" />} n={patched} l="patched" />
            </div>
            <SelfEval fixture={fixture} token={token} />
          </div>

          <div
            ref={feedRef}
            className="grain relative flex max-h-[72vh] min-h-[420px] flex-col gap-3 overflow-y-auto rounded-xl border border-line bg-ink-0/60 p-4 sm:p-5"
          >
            {events.length === 0 ? (
              <div className="m-auto max-w-sm text-center">
                <div className="mx-auto mb-4 grid h-14 w-14 place-items-center rounded-2xl border border-line2 bg-ink-1 text-ash">
                  <Radar className="h-6 w-6" />
                </div>
                <h3 className="font-display text-base font-semibold text-ash">
                  Watching for failures
                </h3>
                <p className="mt-1.5 text-[13px] leading-relaxed text-slate">
                  {fixture
                    ? "Play the fixture to inspect the full diagnose → patch → verify UI without external calls."
                    : "Send a customer message — when ShopBot hallucinates, TraceLog catches it here and walks the full diagnose → patch → verify loop."}
                </p>
              </div>
            ) : (
              events.map((ev, i) => <EventCard key={i} ev={ev} />)
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

function Stat({ icon, n, l }: { icon: React.ReactNode; n: number; l: string }) {
  return (
    <div className="panel p-4">
      <div className="flex items-center gap-1.5 text-slate">{icon}</div>
      <div className="mt-2 font-mono text-2xl font-semibold text-bone">{n}</div>
      <div className="mt-0.5 font-mono text-[10.5px] uppercase tracking-wide2 text-slate">
        {l}
      </div>
    </div>
  );
}
