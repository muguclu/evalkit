# Eval run `969f34941021`

- **Candidate:** `claude-haiku-4-5-noRAG`
- **Dataset:** `C:\Users\guclu\evalkit\examples\turkish-legal-rag\dataset.yaml`
- **Started:** 2026-05-14T23:24:51.236537+00:00
- **Duration:** 55.2s
- **Cases:** 8
- **Pass rate:** 0.0%
- **Mean score:** 0.631
- **Cost:** $0.1623

## Per-case results

| Case | Score | Passed | Failed criteria |
|---|---:|:---:|---|
| `bosanma_sure` | 0.59 | ❌ | missing required phrases: ['duruşma']; faithfulness (score=0.60): Cevap genel olarak makul bilgiler içermekle birlikte,  |
| `kira_artis_orani` | 0.64 | ❌ | faithfulness (score=0.35): Cevap bazı hatalı/uydurma bilgiler içermektedir: '6098 sayılı Türk Medeni Kanunu' ifadesi yan |
| `mirastan_feragat` | 0.68 | ❌ | faithfulness (score=0.55): Cevap yazılı şekil ve noter onayı gibi doğru bilgiler içermektedir. Ancak 'İcra müdürlüğüne b |
| `isten_cikarma_tazminat` | 0.42 | ❌ | missing required phrases: ['ihbar']; faithfulness (score=0.35): Cevap bazı uydurma veya yanıltıcı bilgiler içeriyor: 'Uy |
| `senet_zaman_asimi` | 0.80 | ❌ | completeness (score=0.65): Süre (3 yıl) ve başlangıç noktası (ödeme tarihi) belirtilmiş. 'Zamanaşımı süresi, belirli şar |
| `tuketici_iade` | 0.78 | ❌ | — |
| `nafaka_turleri` | 0.45 | ❌ | missing required phrases: ['iştirak']; faithfulness (score=0.30): Mehir (Mahr), Suç Nafakası, Ekmeğini Kaybeden Nafakası |
| `vergi_uzlasma` | 0.69 | ❌ | faithfulness (score=0.50): Cevap 'Vergi Usul Kanunu (VUK) md. 127-132' olarak madde numarası belirtiyor; ancak uzlaşmaya |

## Tag breakdown

- `aile-hukuku` (2 cases): 0.0% pass
- `sure` (1 cases): 0.0% pass
- `borclar-hukuku` (1 cases): 0.0% pass
- `kira` (1 cases): 0.0% pass
- `miras-hukuku` (1 cases): 0.0% pass
- `is-hukuku` (1 cases): 0.0% pass
- `tazminat` (1 cases): 0.0% pass
- `ticaret-hukuku` (1 cases): 0.0% pass
- `zamanasimi` (1 cases): 0.0% pass
- `tuketici-hukuku` (1 cases): 0.0% pass
- `nafaka` (1 cases): 0.0% pass
- `vergi-hukuku` (1 cases): 0.0% pass
