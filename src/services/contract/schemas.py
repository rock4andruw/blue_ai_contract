"""Shared data schemas for the contract comparison pipeline."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional


# ------------------------------------------------------------------
# Layer 1: Parser output (re-exported for convenience)
# ------------------------------------------------------------------

@dataclass
class Clause:
    """A single parsed clause from a contract document."""
    clause_id: str                    # e.g. "4.1", "12.3"
    title: str                        # First line / heading
    content: str                      # Full clause text
    page_number: int
    content_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)


# ------------------------------------------------------------------
# Layer 2: Alignment output
# ------------------------------------------------------------------

@dataclass
class MatchBlock:
    """A matched (or unmatched) pair of clauses between two versions."""
    old_idx: Optional[int]
    new_idx: Optional[int]
    confidence: float
    method: str   # lcs_equal | clause_number_match | title_match | dp_similar
                  # lcs_deleted | lcs_inserted | dp_deleted | dp_inserted


# ------------------------------------------------------------------
# Layer 3: Diff output
# ------------------------------------------------------------------

ChangeType = Literal["modified", "inserted", "deleted", "unchanged"]

@dataclass
class DiffItem:
    """A single clause-level difference between two contract versions."""
    clause_id: str
    change_type: ChangeType
    old_text: str                     # Empty string if inserted
    new_text: str                     # Empty string if deleted
    confidence: float = 1.0
    match_method: str = ""


# ------------------------------------------------------------------
# Layer 4: Risk engine output
# ------------------------------------------------------------------

RiskLevel = Literal["high", "medium", "low", "none"]
RiskDirection = Literal["adverse", "favorable", "neutral"]

@dataclass
class RiskFlag:
    """A risk assessment for a single clause change."""
    clause_id: str
    risk_code: str                    # e.g. RISK_SLA_DEGRADE
    risk_level: RiskLevel
    risk_direction: RiskDirection
    trigger_reason: str               # One-line human-readable explanation
    old_text: str
    new_text: str
    change_type: ChangeType


# ------------------------------------------------------------------
# Layer 5: LLM / Report output
# ------------------------------------------------------------------

@dataclass
class ReportSection:
    """One entry in the final comparison report (maps to one key change)."""
    rank: int                         # 1-5 priority order
    clause_id: str
    risk_level: RiskLevel
    risk_code: str
    plain_summary: str                # White-language description
    business_impact: str              # Commercial/legal impact
    negotiation_options: List[str]    # 2-3 actionable negotiation strategies
    # MAS Phase 1.5 (defaults = no MAS ran)
    mas_status: str = "single_agent"  # confirmed | pending | single_agent
    mas_confidence: str = "low"       # high | low
    mas_agent_a_view: str = ""        # strict agent reasoning
    mas_agent_b_view: str = ""        # balanced agent reasoning


@dataclass
class ComparisonReport:
    """The complete output of one contract comparison run."""
    original_filename: str
    revised_filename: str
    total_changes: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    overall_risk_level: RiskLevel
    overall_assessment: str           # One-sentence overall verdict
    key_sections: List[ReportSection] # 3-5 prioritised changes
    all_risk_flags: List[RiskFlag]    # Full list for audit trail
    must_negotiate: List[str]         # clause_ids that must be negotiated
    suggested_negotiate: List[str]    # clause_ids worth negotiating
    acceptable: List[str]             # clause_ids that are acceptable


# ------------------------------------------------------------------
# Risk codes (single source of truth)
# ------------------------------------------------------------------

RISK_CODES = {
    "RISK_SLA_DEGRADE":              "服務可用率下降",
    "RISK_RESPONSE_TIME_EXTENDED":   "回應或修復時間拉長",
    "RISK_PENALTY_WEAKENED":         "違約折讓條件放寬或比例降低",
    "RISK_LIABILITY_CAP_CHANGED":    "責任上限變更",
    "RISK_LIABILITY_INCREASE":       "乙方責任加重（對甲方有利）",
    "RISK_PROTECTION_REMOVED":       "保護條款刪除或削弱",
    "RISK_PROTECTION_ADDED":         "保護條款新增（對甲方有利）",
    "RISK_CONFIDENTIALITY_WEAKENED": "保密義務期間縮短或削弱",
    "RISK_DATA_CONTROL_LOST":        "甲方對資料控制權降低",
    "RISK_TERMINATION_CHANGED":      "終止條款變更",
    "RISK_FORCE_MAJEURE_EXPANDED":   "不可抗力範圍擴大",
    "RISK_JURISDICTION_CHANGED":     "管轄法院變更",
    "RISK_IP_OWNERSHIP_CHANGED":          "智慧財產權歸屬改變",
    "RISK_LIABILITY_DIRECTION_REVERSED":  "違約賠償責任方向反轉",
    "RISK_CONFIDENTIALITY_SCOPE_CHANGED": "保密義務範圍改變",
    "RISK_OTHER":                         "其他變更",
    "none":                               "無風險",
}
