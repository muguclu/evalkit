"""Smoke test: validate imports, dataset loading, and non-LLM judges
without making any API calls."""
import asyncio
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from rich.console import Console

from evalkit import Runner, TestCase, load_dataset
from evalkit.judges import build_judge
from evalkit.judges.contains import ContainsJudge
from evalkit.judges.exact_match import ExactMatchJudge
from evalkit.report import diff_runs, render_diff_markdown, render_markdown, save_run
from evalkit.types import JudgeConfig

console = Console()


async def main() -> None:
    dataset_path = Path("examples/turkish-legal-rag/dataset.yaml")
    cases = load_dataset(dataset_path)
    assert len(cases) == 8, f"expected 8 cases, got {len(cases)}"
    console.print(f"[green]PASS[/green]: loaded {len(cases)} cases")
    for c in cases:
        assert c.judges, f"case {c.id} has no judges"
    console.print("[green]PASS[/green]: all cases have judges via default_judges")

    em = ExactMatchJudge(name="em", case_sensitive=False)
    case = TestCase(id="t1", input={"q": "x"}, expected={"answer": "Paris"})
    v = await em.evaluate(case, "  paris  ")
    assert v.passed and v.score == 1.0
    console.print(f"[green]PASS[/green]: exact_match works ({v.reasoning})")

    contains = ContainsJudge(name="c")
    case = TestCase(
        id="t2",
        input={"q": "x"},
        expected={"must_mention": ["Paris", "France"], "must_not_mention": ["London"]},
    )
    v = await contains.evaluate(case, "Paris is the capital of France.")
    assert v.passed, v.failed_criteria
    console.print(f"[green]PASS[/green]: contains all required (score={v.score})")

    v = await contains.evaluate(case, "Paris is in London.")
    assert not v.passed
    console.print(f"[green]PASS[/green]: contains caught failures ({len(v.failed_criteria)} criteria)")

    composite_cfg = JudgeConfig(
        kind="composite",
        name="combo",
        config={
            "children": [
                {"kind": "contains", "name": "c", "weight": 0.5, "config": {}},
                {"kind": "exact_match", "name": "em", "weight": 0.5, "config": {}},
            ]
        },
    )
    combo = build_judge(composite_cfg)
    case = TestCase(
        id="t3",
        input={"q": "x"},
        expected={"answer": "yes", "must_mention": ["yes"]},
    )
    v = await combo.evaluate(case, "yes")
    assert v.passed and v.score == 1.0
    console.print(f"[green]PASS[/green]: composite works ({v.reasoning})")

    async def fake_candidate(case: TestCase) -> str:
        if case.id == "bosanma_sure":
            return "Anlaşmalı boşanma davası, hâkim huzurunda tek duruşmada bitirilebilir."
        return "TÜFE'ye göre yıllık kira artışı yapılır."

    cases_no_llm = [c for c in cases if c.id in ("bosanma_sure", "kira_artis_orani")]
    for c in cases_no_llm:
        c.judges = [j for j in c.judges if j.kind != "llm_judge"]

    runner = Runner(
        candidate_fn=fake_candidate,
        candidate_label="fake-baseline",
        concurrency=2,
    )
    run = await runner.run(cases_no_llm, dataset_path=str(dataset_path))
    assert len(run.cases) == 2
    console.print(
        f"[green]PASS[/green]: runner — {len(run.cases)} cases, pass_rate={run.pass_rate:.2f}"
    )

    run_dir = save_run(run, "runs/")
    assert (run_dir / "results.json").exists()
    assert (run_dir / "summary.md").exists()
    console.print(f"[green]PASS[/green]: report saved to {run_dir}")

    saved = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
    assert saved["run_id"] == run.run_id

    console.print("\n[bold]--- summary.md ---[/bold]")
    console.print(render_markdown(run))

    async def fake_candidate_v2(case: TestCase) -> str:
        if case.id == "bosanma_sure":
            return "Anlaşmalı boşanma TÜFE'ye göre değişir."
        return "Yıllık artış sınırsızdır."

    runner2 = Runner(candidate_fn=fake_candidate_v2, candidate_label="fake-v2", concurrency=2)
    cases_no_llm_2 = [c.model_copy(deep=True) for c in cases_no_llm]
    run2 = await runner2.run(cases_no_llm_2, dataset_path=str(dataset_path))
    save_run(run2, "runs/")
    diff = diff_runs(run, run2)
    console.print("[bold]--- diff ---[/bold]")
    console.print(render_diff_markdown(diff))
    console.print("\n[bold green]ALL SMOKE TESTS PASSED[/bold green]")


if __name__ == "__main__":
    asyncio.run(main())
