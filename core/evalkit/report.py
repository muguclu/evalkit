from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from evalkit.types import RunResult


def save_run(run: RunResult, output_dir: str | Path) -> Path:
    """Write a RunResult to disk as runs/<run_id>/results.json and a
    sibling summary.md. Returns the run directory."""
    output_dir = Path(output_dir)
    run_dir = output_dir / run.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / "results.json").write_text(
        run.model_dump_json(indent=2), encoding="utf-8"
    )
    (run_dir / "summary.md").write_text(render_markdown(run), encoding="utf-8")
    return run_dir


def load_run(run_dir: str | Path) -> RunResult:
    run_dir = Path(run_dir)
    data = (run_dir / "results.json").read_text(encoding="utf-8")
    return RunResult.model_validate_json(data)


def render_markdown(run: RunResult) -> str:
    duration = (run.finished_at - run.started_at).total_seconds()
    lines: list[str] = [
        f"# Eval run `{run.run_id}`",
        "",
        f"- **Candidate:** `{run.candidate_label}`",
        f"- **Dataset:** `{run.dataset_path}`",
        f"- **Started:** {run.started_at.isoformat()}",
        f"- **Duration:** {duration:.1f}s",
        f"- **Cases:** {len(run.cases)}",
        f"- **Pass rate:** {run.pass_rate * 100:.1f}%",
        f"- **Mean score:** {run.mean_score:.3f}",
        f"- **Cost:** ${run.total_cost_usd:.4f}",
        "",
        "## Per-case results",
        "",
        "| Case | Score | Passed | Failed criteria |",
        "|---|---:|:---:|---|",
    ]
    for case in run.cases:
        failures = "; ".join(f for v in case.verdicts for f in v.failed_criteria)[:120]
        if case.error:
            failures = f"ERROR: {case.error}"
        mark = "✅" if case.passed else "❌"
        lines.append(
            f"| `{case.case_id}` | {case.aggregate_score:.2f} | {mark} | {failures or '—'} |"
        )

    tag_counts = Counter(t for c in run.cases for t in c.tags)
    if tag_counts:
        lines += ["", "## Tag breakdown", ""]
        for tag, count in tag_counts.most_common():
            tagged = [c for c in run.cases if tag in c.tags]
            tag_pass = sum(1 for c in tagged if c.passed) / len(tagged)
            lines.append(f"- `{tag}` ({count} cases): {tag_pass * 100:.1f}% pass")

    return "\n".join(lines) + "\n"


def diff_runs(baseline: RunResult, candidate: RunResult) -> dict:
    """Compute a regression diff between two runs.

    Returns a dict with overall deltas and per-case status transitions
    (regressed / fixed / unchanged / new / removed).
    """
    base_by_id = {c.case_id: c for c in baseline.cases}
    cand_by_id = {c.case_id: c for c in candidate.cases}

    regressed: list[dict] = []
    fixed: list[dict] = []
    unchanged: list[str] = []
    score_deltas: list[tuple[str, float]] = []

    for case_id, cand_case in cand_by_id.items():
        base_case = base_by_id.get(case_id)
        if base_case is None:
            continue
        delta = cand_case.aggregate_score - base_case.aggregate_score
        score_deltas.append((case_id, delta))
        if base_case.passed and not cand_case.passed:
            regressed.append(
                {
                    "case_id": case_id,
                    "baseline_score": base_case.aggregate_score,
                    "candidate_score": cand_case.aggregate_score,
                    "failed_criteria": [
                        f for v in cand_case.verdicts for f in v.failed_criteria
                    ],
                }
            )
        elif not base_case.passed and cand_case.passed:
            fixed.append({"case_id": case_id, "delta": delta})
        else:
            unchanged.append(case_id)

    new_cases = [cid for cid in cand_by_id if cid not in base_by_id]
    removed_cases = [cid for cid in base_by_id if cid not in cand_by_id]

    return {
        "baseline_run_id": baseline.run_id,
        "candidate_run_id": candidate.run_id,
        "baseline_label": baseline.candidate_label,
        "candidate_label": candidate.candidate_label,
        "pass_rate_delta": candidate.pass_rate - baseline.pass_rate,
        "mean_score_delta": candidate.mean_score - baseline.mean_score,
        "regressed": regressed,
        "fixed": fixed,
        "unchanged_count": len(unchanged),
        "new_cases": new_cases,
        "removed_cases": removed_cases,
        "score_deltas": dict(score_deltas),
    }


def render_diff_markdown(diff: dict) -> str:
    lines = [
        f"# Diff: `{diff['baseline_label']}` → `{diff['candidate_label']}`",
        "",
        f"- Pass rate delta: **{diff['pass_rate_delta'] * 100:+.1f}%**",
        f"- Mean score delta: **{diff['mean_score_delta']:+.3f}**",
        f"- Regressed: **{len(diff['regressed'])}**",
        f"- Fixed: **{len(diff['fixed'])}**",
        f"- Unchanged: {diff['unchanged_count']}",
        "",
    ]
    if diff["regressed"]:
        lines += ["## ❌ Regressions", ""]
        for r in diff["regressed"]:
            lines.append(
                f"- `{r['case_id']}` — {r['baseline_score']:.2f} → {r['candidate_score']:.2f}"
            )
            for fc in r["failed_criteria"][:3]:
                lines.append(f"  - {fc}")
    if diff["fixed"]:
        lines += ["", "## ✅ Fixed", ""]
        for f in diff["fixed"]:
            lines.append(f"- `{f['case_id']}` (+{f['delta']:.2f})")
    return "\n".join(lines) + "\n"
