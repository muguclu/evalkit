"""Dogfood: evaluate Claude variants on the Turkish legal Q&A dataset.

Each invocation runs one candidate model against the 8-case dataset and
saves the result under runs/. The LLM judge (in dataset.yaml) always uses
claude-sonnet-4-6 to keep the judge consistent across runs.

Usage:
    python run_eval.py --model claude-haiku-4-5
    python run_eval.py --model claude-sonnet-4-6
    python run_eval.py --model claude-opus-4-7

After two or more runs, compare from the dashboard or CLI:
    evalkit diff runs/<a> runs/<b> --fail-on-regression
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from rich.console import Console

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env", override=True)

from evalkit import Runner, TestCase, load_dataset
from evalkit.report import render_markdown, save_run

console = Console()

DATASET_PATH = Path(__file__).parent / "dataset.yaml"
RUNS_DIR = ROOT / "runs"

SYSTEM_PROMPT = (
    "Sen Türk hukuku konusunda uzman bir asistansın. "
    "Sorulara açık, doğru ve özlü Türkçe ile cevap ver. "
    "Bilmediğin konularda 'bu konuda kesin bilgim yok' de."
)


def make_candidate(model: str):
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    async def candidate_fn(case: TestCase) -> str:
        response = await client.messages.create(
            model=model,
            max_tokens=600,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": case.input["question"]}],
        )
        return "".join(
            b.text for b in response.content if getattr(b, "type", None) == "text"
        )

    return candidate_fn


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        default="claude-haiku-4-5",
        help="Candidate Anthropic model id (e.g. claude-opus-4-7, claude-sonnet-4-6, claude-haiku-4-5).",
    )
    parser.add_argument("--limit", type=int, default=0, help="Only run first N cases (0 = all).")
    parser.add_argument("--concurrency", type=int, default=4)
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        console.print("[red]ANTHROPIC_API_KEY not set — put it in .env or export it.[/red]")
        sys.exit(2)

    cases = load_dataset(DATASET_PATH)
    if args.limit:
        cases = cases[: args.limit]

    label = f"{args.model}-noRAG"
    console.print(
        f"[bold]Model:[/bold] {args.model}  "
        f"[bold]Cases:[/bold] {len(cases)}  "
        f"[bold]Concurrency:[/bold] {args.concurrency}"
    )

    runner = Runner(
        candidate_fn=make_candidate(args.model),
        candidate_label=label,
        concurrency=args.concurrency,
        on_case_complete=lambda r: console.print(
            f"  {'[green]PASS[/green]' if r.passed else '[red]FAIL[/red]'} "
            f"{r.case_id} -> {r.aggregate_score:.2f}"
            + (f" — {r.error}" if r.error else "")
        ),
    )
    run = await runner.run(cases, dataset_path=str(DATASET_PATH))

    run_dir = save_run(run, RUNS_DIR)
    console.print(f"\n[green]Saved run to {run_dir}[/green]")
    console.print(render_markdown(run))


if __name__ == "__main__":
    asyncio.run(main())
