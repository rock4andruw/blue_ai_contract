"""API request / response models for the contract comparison endpoint."""

from typing import List, Optional
from pydantic import BaseModel, Field


# ── Request ──────────────────────────────────────────────────────────────────

class CompareRequest(BaseModel):
    """Body for POST /api/v1/contracts/compare when using base64 file content."""
    original_filename: str = Field(..., description="原始合約檔案名稱（含副檔名）")
    original_content: str = Field(..., description="原始合約檔案內容（base64 encoded）")
    revised_filename: str = Field(..., description="修訂合約檔案名稱（含副檔名）")
    revised_content: str = Field(..., description="修訂合約檔案內容（base64 encoded）")
    max_sections: int = Field(5, ge=1, le=10, description="最多顯示幾個主要變更（1-10）")
    example_id: Optional[str] = Field(None, description="範例模式 ID（v2/v3/v4/v5），設定後忽略上傳檔案")


# ── Response sub-models ───────────────────────────────────────────────────────

class NegotiationOption(BaseModel):
    text: str


class KeyChange(BaseModel):
    rank: int
    clause_id: str
    risk_level: str
    risk_code: str
    risk_name: str
    plain_summary: str
    business_impact: str
    negotiation_options: List[str]
    old_text: str = ""
    new_text: str = ""
    change_type: str = ""


class RiskFlagItem(BaseModel):
    clause_id: str
    risk_level: str
    risk_code: str
    risk_name: str
    trigger_reason: str
    risk_direction: str


class ReviewAdvice(BaseModel):
    must_negotiate: List[str]
    suggested_negotiate: List[str]
    acceptable_count: int


class NegotiateRequest(BaseModel):
    clause_id: str
    risk_code: str
    risk_name: str
    old_text: str = ""
    new_text: str = ""
    change_type: str = ""


class PlaybookTier(BaseModel):
    tier1: str
    tier1_clause: str = ""
    tier2: str
    tier2_clause: str = ""
    redline: str


class NegotiateResponse(BaseModel):
    clause_id: str
    risk_code: str
    playbook: PlaybookTier


class CompareResponse(BaseModel):
    # metadata
    original_filename: str
    revised_filename: str
    compare_date: str
    processing_time_ms: int
    summary_mode: str  # "claude_api" | "template_fallback"

    # 核心數字
    total_changes: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    overall_risk_level: str  # high | medium | low | none

    # 內容
    key_changes: List[KeyChange]
    all_risk_flags: List[RiskFlagItem]
    review_advice: ReviewAdvice

    # 完整 Markdown 報告
    markdown_report: str
