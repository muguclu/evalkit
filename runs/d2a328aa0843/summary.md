# Eval run `d2a328aa0843`

- **Candidate:** `claude-opus-4-7-noRAG`
- **Dataset:** `C:\Users\guclu\evalkit\examples\turkish-legal-rag\dataset.yaml`
- **Started:** 2026-05-14T23:29:08.245894+00:00
- **Duration:** 57.5s
- **Cases:** 8
- **Pass rate:** 37.5%
- **Mean score:** 0.812
- **Cost:** $0.1550

## Per-case results

| Case | Score | Passed | Failed criteria |
|---|---:|:---:|---|
| `bosanma_sure` | 0.88 | ✅ | — |
| `kira_artis_orani` | 0.92 | ✅ | — |
| `mirastan_feragat` | 0.63 | ❌ | missing required phrases: ['yazılı']; completeness (score=0.45): Soru 'nasıl yapılır ve geri alınabilir mi?' diye iki kı |
| `isten_cikarma_tazminat` | 0.67 | ❌ | missing required phrases: ['ihbar']; completeness (score=0.65): Kıdem tazminatı, ihbar tazminatı ve işe iade davası/tazm |
| `senet_zaman_asimi` | 0.94 | ✅ | — |
| `tuketici_iade` | 0.86 | ❌ | completeness (score=0.60): Cevap 14 günlük süreyi, sürenin başlangıcını ve cayma hakkının kullanılamayacağı durumların b |
| `nafaka_turleri` | 0.76 | ❌ | missing required phrases: ['iştirak'] |
| `vergi_uzlasma` | 0.83 | ❌ | completeness (score=0.50): The answer covers the definition, two types of uzlaşma, scope, and exclusions. However, the a |

## Tag breakdown

- `aile-hukuku` (2 cases): 50.0% pass
- `sure` (1 cases): 100.0% pass
- `borclar-hukuku` (1 cases): 100.0% pass
- `kira` (1 cases): 100.0% pass
- `miras-hukuku` (1 cases): 0.0% pass
- `is-hukuku` (1 cases): 0.0% pass
- `tazminat` (1 cases): 0.0% pass
- `ticaret-hukuku` (1 cases): 100.0% pass
- `zamanasimi` (1 cases): 100.0% pass
- `tuketici-hukuku` (1 cases): 0.0% pass
- `nafaka` (1 cases): 0.0% pass
- `vergi-hukuku` (1 cases): 0.0% pass
