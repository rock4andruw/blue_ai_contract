"""POST /api/v1/contracts/compare — contract comparison endpoint."""

import base64
import os
import time
import tempfile
from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse

from .schemas_api import CompareResponse, KeyChange, RiskFlagItem, ReviewAdvice
from ..services.contract.orchestrator import compare as run_pipeline
from ..services.contract.parser import ContractParser
from ..services.contract.alignment import ContractAligner
from ..services.contract.diff_engine import DiffEngine
from ..services.contract.risk_engine import RiskEngine
from ..services.contract.llm_service import generate_sections
from ..services.contract.report_generator import build_report, to_markdown, LEVEL_ZH
from ..services.contract.schemas import RISK_CODES

router = APIRouter(prefix="/api/v1/contracts", tags=["contracts"])

# 範例合約路徑（相對於專案根目錄）
_BASE_DIR = Path(__file__).resolve().parents[2]
EXAMPLE_CONTRACTS = {
    "v1": _BASE_DIR / "sla_contract" / "SLA-like Base Contract v1.md",
    "v2": _BASE_DIR / "sla_contract" / "sla_v2_degrade.md",
    "v3": _BASE_DIR / "sla_contract" / "sla_v3_liability.md",
    "v4": _BASE_DIR / "sla_contract" / "sla_v4_remove_protection.md",
    "v5": _BASE_DIR / "sla_contract" / "sla_v5_termination.md",
}


def _get_api_key() -> Optional[str]:
    return os.environ.get("ANTHROPIC_API_KEY") or None


def _build_response(
    original_path: str,
    revised_path: str,
    original_filename: str,
    revised_filename: str,
    api_key: Optional[str],
    start_time: float,
) -> CompareResponse:
    """Run pipeline and assemble CompareResponse."""
    parser = ContractParser()
    original_doc = parser.parse_file(original_path)
    revised_doc = parser.parse_file(revised_path)

    aligner = ContractAligner()
    alignment = aligner.align_documents(original_doc.clauses, revised_doc.clauses)

    diff_engine = DiffEngine()
    diffs = diff_engine.compute_diffs(original_doc.clauses, revised_doc.clauses, alignment)

    risk_engine = RiskEngine()
    flags = risk_engine.analyze(diffs)

    sections, summary_mode = generate_sections(
        flags, api_key=api_key, return_mode=True
    )

    report = build_report(
        original_filename=original_filename,
        revised_filename=revised_filename,
        diffs=diffs,
        flags=flags,
        sections=sections,
    )
    md = to_markdown(report)

    elapsed_ms = int((time.time() - start_time) * 1000)

    key_changes = [
        KeyChange(
            rank=s.rank,
            clause_id=s.clause_id,
            risk_level=s.risk_level,
            risk_code=s.risk_code,
            risk_name=RISK_CODES.get(s.risk_code, s.risk_code),
            plain_summary=s.plain_summary,
            business_impact=s.business_impact,
            negotiation_options=s.negotiation_options,
        )
        for s in report.key_sections
    ]

    all_flags = [
        RiskFlagItem(
            clause_id=f.clause_id,
            risk_level=f.risk_level,
            risk_code=f.risk_code,
            risk_name=RISK_CODES.get(f.risk_code, f.risk_code),
            trigger_reason=f.trigger_reason,
            risk_direction=f.risk_direction,
        )
        for f in report.all_risk_flags
    ]

    return CompareResponse(
        original_filename=original_filename,
        revised_filename=revised_filename,
        compare_date=date.today().isoformat(),
        processing_time_ms=elapsed_ms,
        summary_mode=summary_mode,
        total_changes=report.total_changes,
        high_risk_count=report.high_risk_count,
        medium_risk_count=report.medium_risk_count,
        low_risk_count=report.low_risk_count,
        overall_risk_level=report.overall_risk_level,
        key_changes=key_changes,
        all_risk_flags=all_flags,
        review_advice=ReviewAdvice(
            must_negotiate=report.must_negotiate,
            suggested_negotiate=report.suggested_negotiate,
            acceptable_count=len(report.acceptable),
        ),
        markdown_report=md,
    )


# ── Endpoint: multipart file upload ──────────────────────────────────────────

@router.post("/compare", response_model=CompareResponse, summary="比對兩份合約")
async def compare_contracts(
    original_file: UploadFile = File(..., description="原始合約（PDF/DOCX/MD）"),
    revised_file: UploadFile = File(..., description="修訂合約（PDF/DOCX/MD）"),
    api_key: Optional[str] = Depends(_get_api_key),
):
    """上傳兩份合約，回傳完整比對報告（JSON）。"""
    start = time.time()

    original_bytes = await original_file.read()
    revised_bytes = await revised_file.read()

    if len(original_bytes) > 50 * 1024 * 1024 or len(revised_bytes) > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="檔案大小超過 50MB 限制")

    suffix_orig = Path(original_file.filename or "contract.md").suffix or ".md"
    suffix_rev = Path(revised_file.filename or "contract.md").suffix or ".md"

    with tempfile.NamedTemporaryFile(suffix=suffix_orig, delete=False) as f_orig:
        f_orig.write(original_bytes)
        orig_path = f_orig.name

    with tempfile.NamedTemporaryFile(suffix=suffix_rev, delete=False) as f_rev:
        f_rev.write(revised_bytes)
        rev_path = f_rev.name

    try:
        result = _build_response(
            original_path=orig_path,
            revised_path=rev_path,
            original_filename=original_file.filename or "original",
            revised_filename=revised_file.filename or "revised",
            api_key=api_key,
            start_time=start,
        )
    finally:
        Path(orig_path).unlink(missing_ok=True)
        Path(rev_path).unlink(missing_ok=True)

    return result


# ── Endpoint: example mode ────────────────────────────────────────────────────

@router.get(
    "/compare/example/{example_id}",
    response_model=CompareResponse,
    summary="範例模式（v2/v3/v4/v5）",
)
async def compare_example(
    example_id: str,
    api_key: Optional[str] = Depends(_get_api_key),
):
    """使用內建範例合約進行比對，example_id 為 v2 / v3 / v4 / v5。"""
    if example_id not in EXAMPLE_CONTRACTS:
        raise HTTPException(
            status_code=404,
            detail=f"範例不存在，可用值：{list(EXAMPLE_CONTRACTS.keys())[1:]}",
        )

    orig_path = str(EXAMPLE_CONTRACTS["v1"])
    rev_path = str(EXAMPLE_CONTRACTS[example_id])

    if not Path(orig_path).exists() or not Path(rev_path).exists():
        raise HTTPException(status_code=500, detail="範例合約檔案未找到")

    start = time.time()
    return _build_response(
        original_path=orig_path,
        revised_path=rev_path,
        original_filename="SLA-like Base Contract v1.md",
        revised_filename=Path(rev_path).name,
        api_key=api_key,
        start_time=start,
    )


# ── Endpoint: health check ────────────────────────────────────────────────────

@router.get("/health", summary="健康檢查")
async def health():
    return {"status": "ok", "examples_available": list(EXAMPLE_CONTRACTS.keys())[1:]}
