# Eval run `76f17871fb40`

- **Candidate:** `claude-sonnet-4-6-noRAG`
- **Dataset:** `C:\Users\guclu\evalkit\examples\turkish-legal-rag\dataset.yaml`
- **Started:** 2026-05-14T23:27:35.133785+00:00
- **Duration:** 62.3s
- **Cases:** 8
- **Pass rate:** 37.5%
- **Mean score:** 0.827
- **Cost:** $0.1656

## Per-case results

| Case | Score | Passed | Failed criteria |
|---|---:|:---:|---|
| `bosanma_sure` | 0.89 | ✅ | — |
| `kira_artis_orani` | 0.70 | ❌ | missing required phrases: ['tüketici fiyat endeksi'] |
| `mirastan_feragat` | 0.85 | ❌ | completeness (score=0.55): Sözleşmenin yapılış şartları, taraflar, ivaz ve feragatin kapsamı ele alınmış; ancak geri alı |
| `isten_cikarma_tazminat` | 0.66 | ❌ | missing required phrases: ['ihbar'] |
| `senet_zaman_asimi` | 0.91 | ✅ | — |
| `tuketici_iade` | 0.90 | ✅ | — |
| `nafaka_turleri` | 0.83 | ❌ | missing required phrases: ['iştirak'] |
| `vergi_uzlasma` | 0.87 | ❌ | completeness (score=0.65): Cevap uzlaşma türlerini, kapsamını, süreyi (30 gün) ve önemli bir istisnayı (kaçakçılık/3 kat |

## Tag breakdown

- `aile-hukuku` (2 cases): 50.0% pass
- `sure` (1 cases): 100.0% pass
- `borclar-hukuku` (1 cases): 0.0% pass
- `kira` (1 cases): 0.0% pass
- `miras-hukuku` (1 cases): 0.0% pass
- `is-hukuku` (1 cases): 0.0% pass
- `tazminat` (1 cases): 0.0% pass
- `ticaret-hukuku` (1 cases): 100.0% pass
- `zamanasimi` (1 cases): 100.0% pass
- `tuketici-hukuku` (1 cases): 100.0% pass
- `nafaka` (1 cases): 0.0% pass
- `vergi-hukuku` (1 cases): 0.0% pass
