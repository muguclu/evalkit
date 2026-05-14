# EvalKit

> A small, opinionated LLM evaluation framework with **structured rubrics**, **regression detection**, and **run comparison**.

Most eval tools give you a number. EvalKit tells you *which rubric criterion failed and why*, then catches it the next time your prompt changes.

---

## What's different

| Feature | EvalKit | Typical RAGAS/DeepEval flow |
|---|---|---|
| Judge output | Structured Pydantic verdict per rubric criterion (score + evidence + passed) | Single numeric score |
| Failure messages | "faithfulness=0.40: the answer claims X but the context says Y" | "score: 0.7" |
| Regression detection | First-class: `evalkit diff` exits 1 if any case regresses | Manual |
| CI integration | GitHub Action template included | Roll your own |
| Provider | Claude (default), pluggable | Mixed |
| Run history | Persisted as `runs/<id>/results.json` + Markdown summary | Often ephemeral |

## Architecture

```
┌──────────────┐    ┌────────────┐    ┌───────────────────────┐
│ dataset.yaml │───▶│   Runner   │───▶│   Judges (async)      │
│  TestCases   │    │  (asyncio) │    │  - contains           │
└──────────────┘    └─────┬──────┘    │  - exact_match        │
                          │           │  - llm_judge (Claude) │
                          │           │  - composite          │
                          │           └───────────┬───────────┘
                          ▼                       │
                  ┌───────────────┐               │
                  │  CaseResult   │◀──────────────┘
                  │  + verdicts   │
                  └───────┬───────┘
                          ▼
              ┌───────────────────────┐
              │ runs/<id>/results.json│
              │ runs/<id>/summary.md  │
              └───────────┬───────────┘
                          ▼
               ┌──────────────────────┐
               │  evalkit diff A B    │
               │  → regression report │
               └──────────────────────┘
```

## Install

```bash
cd core
pip install -e .
```

## 60-second example

```yaml
# dataset.yaml
cases:
  - id: capital_of_france
    input: { question: "What is the capital of France?" }
    expected:
      must_mention: ["Paris"]
    judges:
      - kind: contains
        weight: 0.4
      - kind: llm_judge
        weight: 0.6
        config:
          rubric:
            - { name: factual_accuracy, description: "Answer is factually correct.", weight: 1.0 }
            - { name: conciseness,      description: "Answer is short and direct.",  weight: 0.5 }
```

```python
# run.py
import asyncio
from evalkit import Runner, load_dataset
from evalkit.report import save_run

async def candidate_fn(case):
    return await my_llm_app(case.input["question"])

async def main():
    cases = load_dataset("dataset.yaml")
    runner = Runner(candidate_fn=candidate_fn, candidate_label="v1")
    run = await runner.run(cases, dataset_path="dataset.yaml")
    save_run(run, "runs/")

asyncio.run(main())
```

```bash
evalkit report runs/<run_id>
evalkit diff runs/<baseline_id> runs/<candidate_id> --fail-on-regression
```

## Judges

- **`exact_match`** — strict equality against `expected.answer`, with optional case/whitespace normalization
- **`contains`** — `expected.must_mention` and `expected.must_not_mention` phrase checks
- **`llm_judge`** — Claude scores the candidate against a weighted Pydantic-validated rubric; returns per-criterion score, passed flag, and supporting evidence
- **`composite`** — weighted blend of multiple inner judges

Every verdict carries: `score`, `passed`, `reasoning`, `failed_criteria`, `cost_usd`, `latency_ms`.

## Real-world example: Turkish Legal RAG

`examples/turkish-legal-rag/` evaluates a RAG pipeline over Turkish legal documents with an 8-case golden set and a four-criterion legal-correctness rubric. Drop in your own `candidate_fn` to plug in your retrieval chain.

## Why I built this

Built as part of my AI engineer portfolio. The goal: show that **shipping LLM apps without an eval harness is shipping blind**, and that "an eval harness" should mean *typed failure analysis*, not a single number.

## Status

Day 1 of a 6-day build. Currently shipped: core engine, four judges, runner, CLI for reports/diffs, a real-world example.

Up next:
- [ ] Next.js dashboard for run-to-run comparison
- [ ] GitHub Action for PR regression checks
- [ ] More judges: `regex`, `json_schema`, `tool_call_match`

## License

MIT
