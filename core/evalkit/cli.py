from __future__ import annotations

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import click
from rich.console import Console
from rich.table import Table

from evalkit.report import diff_runs, load_run, render_diff_markdown, render_markdown

console = Console()


@click.group()
def main() -> None:
    """EvalKit — LLM evaluation framework."""


@main.command("report")
@click.argument("run_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
def report_cmd(run_dir: Path) -> None:
    """Print a Markdown summary of a run."""
    run = load_run(run_dir)
    click.echo(render_markdown(run))


@main.command("diff")
@click.argument("baseline_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument("candidate_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option(
    "--fail-on-regression",
    is_flag=True,
    help="Exit with code 1 if the candidate has any regressed cases.",
)
def diff_cmd(baseline_dir: Path, candidate_dir: Path, fail_on_regression: bool) -> None:
    """Compare two runs and highlight regressions."""
    baseline = load_run(baseline_dir)
    candidate = load_run(candidate_dir)
    diff = diff_runs(baseline, candidate)
    click.echo(render_diff_markdown(diff))
    if fail_on_regression and diff["regressed"]:
        console.print(
            f"[red]REGRESSION: {len(diff['regressed'])} case(s) regressed[/red]"
        )
        sys.exit(1)


@main.command("list")
@click.argument("runs_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
def list_cmd(runs_dir: Path) -> None:
    """List runs in a directory."""
    table = Table(title=f"Runs in {runs_dir}")
    table.add_column("Run ID")
    table.add_column("Candidate")
    table.add_column("Started")
    table.add_column("Cases", justify="right")
    table.add_column("Pass rate", justify="right")
    table.add_column("Mean score", justify="right")
    table.add_column("Cost (USD)", justify="right")

    for run_path in sorted(runs_dir.iterdir()):
        if not (run_path / "results.json").exists():
            continue
        run = load_run(run_path)
        table.add_row(
            run.run_id,
            run.candidate_label,
            run.started_at.strftime("%Y-%m-%d %H:%M"),
            str(len(run.cases)),
            f"{run.pass_rate * 100:.1f}%",
            f"{run.mean_score:.3f}",
            f"${run.total_cost_usd:.4f}",
        )
    console.print(table)


if __name__ == "__main__":
    main()
