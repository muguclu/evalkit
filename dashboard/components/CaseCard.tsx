"use client";

import { useState } from "react";
import clsx from "clsx";

import { ScoreBar } from "./ScoreBar";
import { StatusBadge } from "./StatusBadge";
import type { CaseResult, Verdict } from "@/lib/types";
import { fmtCost, fmtLatency, fmtScore } from "@/lib/format";

export function CaseCard({ result }: { result: CaseResult }) {
  const [open, setOpen] = useState(false);

  return (
    <div
      className={clsx(
        "card transition",
        result.passed
          ? "border-bg-border"
          : "border-accent-red/30 bg-accent-red/[0.03]",
      )}
    >
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between text-left"
      >
        <div className="flex flex-1 items-center gap-4">
          <StatusBadge passed={result.passed} />
          <div className="font-mono text-sm text-ink-base">{result.case_id}</div>
          {result.tags.length > 0 && (
            <div className="flex gap-1.5">
              {result.tags.map((t) => (
                <span key={t} className="pill">
                  {t}
                </span>
              ))}
            </div>
          )}
        </div>
        <div className="flex items-center gap-4">
          <ScoreBar score={result.aggregate_score} passed={result.passed} />
          <span className="text-ink-dim">{open ? "−" : "+"}</span>
        </div>
      </button>

      {open && (
        <div className="mt-5 space-y-5 border-t border-bg-border pt-5">
          {result.error && (
            <div className="rounded-lg border border-accent-red/30 bg-accent-red/10 p-3 text-sm text-accent-red">
              {result.error}
            </div>
          )}

          <Section title="Candidate output">
            <pre className="whitespace-pre-wrap rounded-lg bg-bg-panel p-4 text-sm text-ink-base">
              {result.candidate_output || "(empty)"}
            </pre>
          </Section>

          {result.verdicts.map((v, i) => (
            <VerdictPanel key={i} verdict={v} />
          ))}
        </div>
      )}
    </div>
  );
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <div className="mb-2 text-xs uppercase tracking-wide text-ink-dim">
        {title}
      </div>
      {children}
    </div>
  );
}

function VerdictPanel({ verdict }: { verdict: Verdict }) {
  const rubric = verdict.raw?.scores;
  return (
    <div className="rounded-lg border border-bg-border bg-bg-panel/40 p-4">
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <StatusBadge passed={verdict.passed} size="sm" />
          <span className="font-mono text-sm text-ink-base">
            {verdict.judge_name}
          </span>
          <span className="pill">{verdict.judge_kind}</span>
        </div>
        <div className="flex items-center gap-4 text-xs text-ink-muted">
          {verdict.cost_usd > 0 && <span>{fmtCost(verdict.cost_usd)}</span>}
          {verdict.latency_ms > 0 && <span>{fmtLatency(verdict.latency_ms)}</span>}
          <span className="font-mono text-ink-base">
            {fmtScore(verdict.score)}
          </span>
        </div>
      </div>

      {verdict.reasoning && (
        <p className="mb-3 text-sm text-ink-muted">{verdict.reasoning}</p>
      )}

      {rubric && (
        <div className="space-y-2">
          {Object.entries(rubric).map(([name, entry]) => (
            <div
              key={name}
              className="flex flex-col gap-1 rounded-md bg-bg-card/60 p-2.5"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <StatusBadge passed={entry.passed} size="sm" />
                  <span className="font-mono text-xs text-ink-base">{name}</span>
                </div>
                <ScoreBar
                  score={entry.score}
                  passed={entry.passed}
                  width="w-20"
                />
              </div>
              {entry.evidence && (
                <p className="text-xs italic text-ink-muted">
                  &ldquo;{entry.evidence}&rdquo;
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {verdict.failed_criteria.length > 0 && !rubric && (
        <ul className="mt-2 space-y-1 text-xs text-accent-red">
          {verdict.failed_criteria.map((f, i) => (
            <li key={i}>· {f}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
