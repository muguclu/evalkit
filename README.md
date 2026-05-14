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

## Real-world example: Turkish Legal Q&A across three Claude variants

`examples/turkish-legal-rag/` runs the same 8-case Turkish legal Q&A
dataset through three Claude variants (Haiku 4.5 / Sonnet 4.6 / Opus 4.7)
with a four-criterion legal-correctness rubric. Full writeup including
the LLM judge's evidence quotes lives at
[`examples/turkish-legal-rag/FINDINGS.md`](examples/turkish-legal-rag/FINDINGS.md).

| Model | Pass rate | Mean score | Cost |
|---|---:|---:|---:|
| `claude-haiku-4-5`  | 0/8 (0%)    | 0.631 | $0.16 |
| `claude-sonnet-4-6` | 3/8 (37.5%) | **0.827** | $0.17 |
| `claude-opus-4-7`   | 3/8 (37.5%) | 0.812 | $0.16 |

The headline: **Opus 4.7 doesn't beat Sonnet 4.6 on this task.**
Mean-score delta is −0.014 in Sonnet's favor; per-case deltas show two
roughly-canceling swings (Opus is +0.21 on one case, −0.22 on another).
This is the kind of judgement aggregate-score frameworks can't make.

## Why I built this

Built as part of my AI engineer portfolio. The goal: show that **shipping LLM apps without an eval harness is shipping blind**, and that "an eval harness" should mean *typed failure analysis*, not a single number.

## Dashboard

A Next.js 14 dashboard lives in `dashboard/`. It reads from the same `runs/` directory, so any local eval run shows up immediately.

```bash
cd dashboard
npm install
npm run dev     # http://localhost:3000
```

Three views:

- `/` — list of runs (pass rate, mean score, total cost, sortable by recency)
- `/runs/[id]` — per-case results with expandable rubric breakdowns (per-criterion score, evidence quote, failed criteria)
- `/compare?a=...&b=...` — diff two runs (regressions in red, fixes in green, per-case score deltas)

The dashboard is filesystem-backed — no database, no auth, no deploy required for local use.

## Status

Days 1, 3, 5 shipped. Currently:
- ✅ Python core engine, four judges, async runner, CLI
- ✅ Next.js 14 dashboard with run list / detail / compare views
- ✅ Real-world example: three Claude models head-to-head on Turkish
  legal Q&A, with findings writeup

Up next:
- [ ] GitHub Action: PR regression check (Day 4)
- [ ] Repeat the dogfood with real retrieval (turkish-legal-rag chain)
- [ ] More judges: `regex`, `json_schema`, `tool_call_match`
- [ ] README screenshots / demo gif

## License

MIT
