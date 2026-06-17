"""Orchestrator: runs the full contract comparison pipeline end-to-end."""

import os
import sys
from pathlib import Path
from typing import Optional

from .parser import ContractParser
from .alignment import ContractAligner
from .diff_engine import DiffEngine
from .risk_engine import RiskEngine
from .llm_service import generate_sections
from .report_generator import build_report, to_markdown


def compare(
    original_path: str,
    revised_path: str,
    api_key: Optional[str] = None,
    max_sections: int = 5,
    output_path: Optional[str] = None,
) -> str:
    """Run full pipeline: parse → align → diff → risk → llm → report.

    Returns the Markdown report string.
    Writes to output_path if provided.
    """
    key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")

    # Step 1: Parse
    parser = ContractParser()
    original_doc = parser.parse_file(original_path)
    revised_doc = parser.parse_file(revised_path)

    # Step 2: Align
    aligner = ContractAligner()
    alignment = aligner.align_documents(original_doc.clauses, revised_doc.clauses)

    # Step 3: Diff
    diff_engine = DiffEngine()
    diffs = diff_engine.compute_diffs(original_doc.clauses, revised_doc.clauses, alignment)

    # Step 4: Risk
    risk_engine = RiskEngine()
    flags = risk_engine.analyze(diffs)

    # Step 5: LLM summary (uses template fallback if no API key)
    sections = generate_sections(flags, api_key=key or None, max_sections=max_sections)

    # Step 6: Report
    report = build_report(
        original_filename=Path(original_path).name,
        revised_filename=Path(revised_path).name,
        diffs=diffs,
        flags=flags,
        sections=sections,
    )
    md = to_markdown(report)

    if output_path:
        Path(output_path).write_text(md, encoding="utf-8")

    return md


def main():
    import argparse
    parser = argparse.ArgumentParser(description="合約智能比對助理")
    parser.add_argument("original", help="原始合約路徑（PDF / DOCX / MD）")
    parser.add_argument("revised", help="修訂合約路徑（PDF / DOCX / MD）")
    parser.add_argument("--output", "-o", help="輸出報告路徑（預設印到 stdout）")
    parser.add_argument("--sections", "-n", type=int, default=5, help="最多顯示幾個重點變更（預設 5）")
    args = parser.parse_args()

    md = compare(
        original_path=args.original,
        revised_path=args.revised,
        max_sections=args.sections,
        output_path=args.output,
    )

    if not args.output:
        print(md)
    else:
        print(f"報告已儲存至：{args.output}")


if __name__ == "__main__":
    main()
