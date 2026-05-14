# Findings: Turkish Legal Q&A across three Claude variants

Real eval run from EvalKit's first end-to-end dogfood. Same dataset
(8 Turkish legal questions, no retrieval), same judge (Claude Sonnet 4.6
with a 4-criterion weighted rubric: `faithfulness`, `legal_correctness`,
`completeness`, `language_quality`), three candidate models. Each
candidate is generated with `max_tokens=600` and `temperature=0` defaults
from the Anthropic SDK.

## Results

| Model | Pass rate | Mean score | Cost (judge + candidate) |
|---|---:|---:|---:|
| `claude-haiku-4-5`  | 0/8 (0%)    | 0.631 | $0.16 |
| `claude-sonnet-4-6` | 3/8 (37.5%) | **0.827** | $0.17 |
| `claude-opus-4-7`   | 3/8 (37.5%) | 0.812 | $0.16 |

The judge model is held constant (Sonnet 4.6) across all three runs, so
cost differences come almost entirely from the candidate model.

## Headline 1 — Opus is not free money

**Sonnet 4.6 matches Opus 4.7 on this task** despite Opus' list price
being roughly 5× higher per output token. Per-case score delta when
upgrading Sonnet → Opus:

```
kira_artis_orani         +0.214   Opus wins
senet_zaman_asimi        +0.033
isten_cikarma_tazminat   +0.003
bosanma_sure             -0.010
vergi_uzlasma            -0.033
tuketici_iade            -0.037
nafaka_turleri           -0.063
mirastan_feragat         -0.223   Opus loses
```

Net mean score delta: **−0.014** (Opus is fractionally *worse*).
Net pass-rate delta: **0**.

The two large swings roughly cancel, so on this dataset Opus buys you
nothing over Sonnet — except the bill. An eval framework that returned a
single number per run would call this a wash; the per-case deltas show
the actual structure of the trade.

## Headline 2 — Why structured rubrics matter

Aggregate scores hide *why* a model gained or lost. Two concrete cases
from the verdicts file, quoting the LLM judge's `evidence` field
verbatim:

**`kira_artis_orani` — Opus +0.214 over Sonnet.** Both models cite TBK
art. 344 correctly. The score gap is from the `contains` judge: Sonnet
wrote *"TÜFE (12 aylık ortalamalara göre değişim)"*, Opus wrote
*"tüketici fiyat endeksindeki (TÜFE)"*. The dataset requires both phrases
to appear; Sonnet missed *"tüketici fiyat endeksi"* as a literal phrase.
This is a **wording-not-meaning** failure that aggregate scores would
hide and that highlights a real fragility of `contains`-style assertions.

**`mirastan_feragat` — Opus −0.223 below Sonnet.** The judge's
`legal_correctness` evidence on the Opus answer:
*"TMK 545 aslında vasiyetnamenin resmi şeklini düzenler; feragat
sözleşmesinin şekli TMK 528'de düzenlenir"* — Opus cited TMK 545 (formal
wills) when the article actually governing feragat is TMK 528. Sonnet
got the article right (528-529). The judge also flagged both models on
`completeness=0.45/0.55` because both **ran out of output tokens** before
answering the *"geri alınabilir mi?"* half of the question.

## Headline 3 — `max_tokens=600` was a footgun

Both stronger models lost completeness points to truncation, not lack of
knowledge. From the Opus verdict on `mirastan_feragat`:
*"Cevap yalnızca yapılış şeklini açıklamış, 'geri alınabilir mi?' sorusuna
hiç yanıt vermemiştir"*. Sonnet's `kira_artis_orani` answer ended with
*"| **Artış zamanı** | Gen"* — cut mid-table-cell.

This is itself a finding worth surfacing: **the eval result is partially
an artifact of the budget we gave the model, not the model's
capability**. In production, this means you set `max_tokens` per task
(or use streaming and stop on natural boundaries), not per model.

## Why the absolute pass rate is so low

3/8 = 37.5% on the two stronger models. The dataset asks for things like
*"Bono ve poliçede zamanaşımı süresi ne kadardır?"* and *"Boşanma
sonrası verilen nafaka türleri nelerdir?"* — answers that need citations
to specific articles of the Turkish Civil/Commercial Code. Without
retrieval, the model knows the *shape* of the answer but mis-cites or
omits articles, and the rubric's `legal_correctness` criterion catches
that.

The next step is to run the same dataset with the `turkish-legal-rag`
retrieval pipeline and watch which cases *flip* — that's the regression
diff EvalKit is designed for.

## Reproducing this

```bash
# from repo root, on Windows
python -m venv .venv
.venv/Scripts/pip install -e core python-dotenv

# put your key in .env (not .env.txt — Windows likes to add .txt)
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# run all three
.venv/Scripts/python examples/turkish-legal-rag/run_eval.py --model claude-haiku-4-5
.venv/Scripts/python examples/turkish-legal-rag/run_eval.py --model claude-sonnet-4-6
.venv/Scripts/python examples/turkish-legal-rag/run_eval.py --model claude-opus-4-7

# inspect from the CLI
evalkit list runs
evalkit diff runs/<sonnet_id> runs/<opus_id>

# or in the browser
cd dashboard && npm run dev   # http://localhost:3000
```

Total cost for the three runs above: **$0.49**.
