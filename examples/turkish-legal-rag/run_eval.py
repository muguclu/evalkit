"""Dogfood: evaluate Claude variants (and an external RAG) on Turkish legal Q&A.

Each invocation runs one candidate against the 8-case dataset and saves the
result under runs/. The LLM judge (in dataset.yaml) always uses
claude-sonnet-4-6 to keep judgement consistent across runs.

Usage:
    # Raw Claude variants — calls the API
    python run_eval.py --model claude-haiku-4-5
    python run_eval.py --model claude-sonnet-4-6
    python run_eval.py --model claude-opus-4-7

    # External RAG outputs collected elsewhere — no candidate API calls,
    # the judge still runs against the answers in the JSON
    python run_eval.py \\
        --model json:examples/turkish-legal-rag/rag_outputs.json \\
        --label turkish-legal-rag-v1

After two or more runs, compare from the dashboard or CLI:
    evalkit diff runs/<a> runs/<b> --fail-on-regression
"""
from __future__ import annotations

import argparse
import asyncio
import json
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


def make_anthropic_candidate(model: str):
    """Live candidate: call Anthropic Messages API with no retrieval."""
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


def make_json_candidate(json_path: Path):
    """Replay candidate: read pre-collected outputs from a JSON file.

    Expected schema (matches tools/collect_rag_outputs.py):
        {
          "<case_id>": {
              "answer": "...",
              "context": "...",          # optional, surfaced to the judge
              "source_documents": [...]  # optional
          }
        }
    """
    if not json_path.exists():
        raise FileNotFoundError(f"RAG outputs file not found: {json_path}")
    data = json.loads(json_path.read_text(encoding="utf-8"))

    async def candidate_fn(case: TestCase) -> str:
        entry = data.get(case.id)
        if entry is None:
            raise KeyError(
                f"case '{case.id}' missing from {json_path.name} — "
                f"the JSON must include every case_id from dataset.yaml"
            )
        if entry.get("error"):
            raise RuntimeError(f"upstream RAG error: {entry['error']}")
        # Surface retrieved context to the LLM judge for faithfulness scoring.
        if entry.get("context"):
            case.context = entry["context"]
        return entry["answer"]

    return candidate_fn


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        default="claude-haiku-4-5",
        help="claude-* model id, or 'json:<path>' to replay pre-collected outputs.",
    )
    parser.add_argument(
        "--label",
        default=None,
        help="Candidate label saved with the run. Defaults to '<model>-noRAG'.",
    )
    parser.add_argument("--limit", type=int, default=0, help="Only run first N cases (0 = all).")
    parser.add_argument("--concurrency", type=int, default=4)
    args = parser.parse_args()

    cases = load_dataset(DATASET_PATH)
    if args.limit:
        cases = cases[: args.limit]

    if args.model.startswith("json:"):
        json_path = Path(args.model.removeprefix("json:"))
        candidate_fn = make_json_candidate(json_path)
        label = args.label or f"replay:{json_path.stem}"
        source_desc = f"json:{json_path.name}"
    else:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            console.print("[red]ANTHROPIC_API_KEY not set — put it in .env or export it.[/red]")
            sys.exit(2)
        candidate_fn = make_anthropic_candidate(args.model)
        label = args.label or f"{args.model}-noRAG"
        source_desc = args.model

    console.print(
        f"[bold]Candidate:[/bold] {source_desc}  "
        f"[bold]Label:[/bold] {label}  "
        f"[bold]Cases:[/bold] {len(cases)}  "
        f"[bold]Concurrency:[/bold] {args.concurrency}"
    )

    runner = Runner(
        candidate_fn=candidate_fn,
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
