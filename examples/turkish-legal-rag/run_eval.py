"""Dogfood example: evaluate a Turkish legal RAG pipeline with EvalKit.

This script is a template. Plug in your own RAG chain in `candidate_fn`
and point DATASET_PATH at the YAML file.

Usage:
    export ANTHROPIC_API_KEY=...
    python run_eval.py
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from rich.console import Console

from evalkit import Runner, TestCase, load_dataset
from evalkit.report import render_markdown, save_run

console = Console()

DATASET_PATH = Path(__file__).parent / "dataset.yaml"
RUNS_DIR = Path(__file__).parent.parent.parent / "runs"


# ---------------------------------------------------------------------------
# Plug your RAG pipeline here.
# ---------------------------------------------------------------------------
async def candidate_fn(case: TestCase) -> str:
    """Return the candidate system's answer for a single test case.

    Replace the body of this function with a call into your RAG chain.
    For example, if you have a LangChain `rag_chain`:

        from rag.chain import rag_chain
        result = await rag_chain.ainvoke({"question": case.input["question"]})
        return result["answer"]
    """
    # Placeholder: call Claude directly with no retrieval. Replace with your RAG.
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
    return "".join(b.text for b in response.content if getattr(b, "type", None) == "text")


async def main() -> None:
    cases = load_dataset(DATASET_PATH)
    console.print(f"[bold]Loaded {len(cases)} cases from {DATASET_PATH}[/bold]")

    runner = Runner(
        candidate_fn=candidate_fn,
        candidate_label="claude-sonnet-4-6-noRAG-baseline",
        concurrency=3,
        on_case_complete=lambda r: console.print(
            f"  {'✅' if r.passed else '❌'} {r.case_id} → {r.aggregate_score:.2f}"
        ),
    )
    run = await runner.run(cases, dataset_path=str(DATASET_PATH))

    run_dir = save_run(run, RUNS_DIR)
    console.print(f"\n[green]Saved run to {run_dir}[/green]")
    console.print(render_markdown(run))


if __name__ == "__main__":
    asyncio.run(main())
