"""Run the turkish-legal-rag chain over the EvalKit dataset and dump outputs to JSON.

This script lives in the EvalKit repo for traceability, but it is meant to be run
*inside* the muguclu/turkish-legal-rag repo (where chain.py and chroma_db live).

Steps:
    1. Copy this file to the root of your turkish-legal-rag clone:
           cp tools/collect_rag_outputs.py <path-to-turkish-legal-rag>/collect_rag_outputs.py
    2. Activate that project's venv and make sure chroma_db/ is built.
    3. Run:
           python collect_rag_outputs.py
    4. It will write rag_outputs.json next to itself. Send that file back into
       EvalKit at examples/turkish-legal-rag/rag_outputs.json.
    5. Eval it like any other candidate:
           python examples/turkish-legal-rag/run_eval.py \
               --model json:examples/turkish-legal-rag/rag_outputs.json \
               --label turkish-legal-rag-v1
"""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path
from typing import Any

# The 8 questions from examples/turkish-legal-rag/dataset.yaml — keep IDs in sync.
QUESTIONS: list[tuple[str, str]] = [
    ("bosanma_sure", "Anlaşmalı boşanma davası ne kadar sürer?"),
    ("kira_artis_orani", "Konut kira sözleşmelerinde yıllık kira artış oranı nasıl belirlenir?"),
    ("mirastan_feragat", "Mirastan feragat sözleşmesi nasıl yapılır ve geri alınabilir mi?"),
    ("isten_cikarma_tazminat", "İşveren tarafından geçerli sebep olmadan işten çıkarılan işçi hangi tazminatları talep edebilir?"),
    ("senet_zaman_asimi", "Bono ve poliçede zamanaşımı süresi ne kadardır?"),
    ("tuketici_iade", "Mesafeli satışlarda tüketicinin cayma hakkı kaç gündür ve hangi durumlarda kullanılamaz?"),
    ("nafaka_turleri", "Boşanma sonrası verilen nafaka türleri nelerdir?"),
    ("vergi_uzlasma", "Vergi ziyaı cezasında uzlaşma müessesesi nedir?"),
]


def main() -> None:
    # Resolve to absolute path early so we know where the JSON ends up.
    output_path = Path("rag_outputs.json").resolve()

    try:
        from src.chain import ask  # noqa: E402
    except ImportError as e:
        print(f"ERROR: could not import src.chain.ask — are you running this from the turkish-legal-rag repo root?\n{e}", file=sys.stderr)
        sys.exit(1)

    outputs: dict[str, Any] = {}
    for i, (case_id, question) in enumerate(QUESTIONS, 1):
        print(f"[{i}/{len(QUESTIONS)}] {case_id}: {question[:70]}...")
        try:
            result = ask(question)
            outputs[case_id] = {
                "question": question,
                "answer": result["answer"],
                "context": result.get("context", ""),
                "source_documents": [
                    {
                        "source": doc.metadata.get("source", "unknown"),
                        "page": doc.metadata.get("page", "?"),
                        "chunk_index": doc.metadata.get("chunk_index", "?"),
                    }
                    for doc in result.get("source_documents", [])
                ],
            }
        except Exception as e:
            outputs[case_id] = {
                "question": question,
                "answer": "",
                "context": "",
                "source_documents": [],
                "error": f"{type(e).__name__}: {e}",
            }
            traceback.print_exc()

    output_path.write_text(json.dumps(outputs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved {len(outputs)} outputs to {output_path}")
    print(f"Send this file to EvalKit at examples/turkish-legal-rag/rag_outputs.json")


if __name__ == "__main__":
    main()
