"""Dogfood: evaluate the turkish-legal-rag pipeline with EvalKit.

Supports two candidate modes:

    python run_eval.py --mode baseline     # raw Claude, no retrieval
    python run_eval.py --mode rag          # full RAG chain with ChromaDB

After running both, compare with:

    evalkit diff runs/<baseline_id> runs/<rag_id>
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

# Load .env from evalkit project root.
ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

from evalkit import Runner, TestCase, load_dataset
from evalkit.report import render_markdown, save_run

console = Console()

DATASET_PATH = Path(__file__).parent / "dataset.yaml"
RUNS_DIR = ROOT / "runs"

# Path to muguclu/turkish-legal-rag local clone.
LEGAL_RAG_REPO = Path("C:/Users/guclu/turkish-legal-rag")


# ---------------------------------------------------------------------------
# Baseline: vanilla Claude, no retrieval.
# ---------------------------------------------------------------------------
async def baseline_candidate(case: TestCase) -> str:
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=(
            "Sen Türk hukuku konusunda uzman bir asistansın. "
            "Sorulara açık ve doğru Türkçe ile cevap ver."
        ),
        messages=[{"role": "user", "content": case.input["question"]}],
    )
    return "".join(
        b.text for b in response.content if getattr(b, "type", None) == "text"
    )


# ---------------------------------------------------------------------------
# RAG: real turkish-legal-rag pipeline (LangChain + ChromaDB + Claude).
# ---------------------------------------------------------------------------
def _import_legal_rag():
    """Add the turkish-legal-rag repo to sys.path and import its ask()."""
    if str(LEGAL_RAG_REPO) not in sys.path:
        sys.path.insert(0, str(LEGAL_RAG_REPO))
    from src.chain import ask  # type: ignore

    return ask


async def rag_candidate(case: TestCase) -> str:
    ask = _import_legal_rag()
    result = await asyncio.to_thread(ask, case.input["question"])
    case.context = result["context"]
    return result["answer"]


CANDIDATES = {
    "baseline": (baseline_candidate, "claude-sonnet-4-6-noRAG"),
    "rag": (rag_candidate, "turkish-legal-rag-v1"),
}


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=list(CANDIDATES), default="baseline")
    parser.add_argument("--concurrency", type=int, default=3)
    args = parser.parse_args()

    candidate_fn, label = CANDIDATES[args.mode]
    cases = load_dataset(DATASET_PATH)
    console.print(
        f"[bold]Mode:[/bold] {args.mode}  "
        f"[bold]Candidate:[/bold] {label}  "
        f"[bold]Cases:[/bold] {len(cases)}"
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
