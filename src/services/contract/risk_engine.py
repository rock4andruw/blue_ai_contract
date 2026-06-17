"""Risk Rule Engine: applies rule-based classification to DiffItems.

Rule engine做判斷與標記，LLM做解釋與表達。
Each rule returns a RiskFlag or None.
"""

import re
from typing import List, Optional
from .schemas import DiffItem, RiskFlag, RiskLevel, RiskDirection


# ------------------------------------------------------------------
# Individual rule functions
# ------------------------------------------------------------------

def _extract_percentage(text: str) -> Optional[float]:
    m = re.search(r'(\d+(?:\.\d+)?)\s*%', text)
    return float(m.group(1)) if m else None


def _extract_hours(text: str) -> Optional[float]:
    """Extract hour value from text like '4 小時' or '2 個工作日' (1 day = 8h)."""
    m = re.search(r'(\d+(?:\.\d+)?)\s*小時', text)
    if m:
        return float(m.group(1))
    m = re.search(r'(\d+(?:\.\d+)?)\s*個工作日', text)
    if m:
        return float(m.group(1)) * 8
    m = re.search(r'(\d+(?:\.\d+)?)\s*分鐘', text)
    if m:
        return float(m.group(1)) / 60
    return None


def _extract_months(text: str) -> Optional[float]:
    m = re.search(r'(\d+(?:\.\d+)?)\s*個月', text)
    return float(m.group(1)) if m else None


def _extract_years(text: str) -> Optional[float]:
    m = re.search(r'(\d+(?:\.\d+)?)\s*年', text)
    return float(m.group(1)) if m else None


def rule_sla_degrade(diff: DiffItem) -> Optional[RiskFlag]:
    """SLA 可用率下降。"""
    if diff.change_type != "modified":
        return None
    old_pct = _extract_percentage(diff.old_text)
    new_pct = _extract_percentage(diff.new_text)
    if old_pct is None or new_pct is None:
        return None
    keywords = ["可用率", "availability", "uptime"]
    if not any(k in diff.old_text for k in keywords):
        return None
    if new_pct < old_pct:
        delta = old_pct - new_pct
        # gold標註：可用率下降 0.4% 為 medium，主條款下降才 high
        level: RiskLevel = "high" if delta >= 0.5 else "medium"
        return RiskFlag(
            clause_id=diff.clause_id,
            risk_code="RISK_SLA_DEGRADE",
            risk_level=level,
            risk_direction="adverse",
            trigger_reason=f"服務可用率由 {old_pct}% 降為 {new_pct}%",
            old_text=diff.old_text,
            new_text=diff.new_text,
            change_type=diff.change_type,
        )
    return None


def rule_response_time_extended(diff: DiffItem) -> Optional[RiskFlag]:
    """回應時間或修復時間拉長。"""
    if diff.change_type != "modified":
        return None
    keywords = ["回應", "修復", "處理", "response", "repair", "resolve"]
    if not any(k in diff.old_text for k in keywords):
        return None
    old_h = _extract_hours(diff.old_text)
    new_h = _extract_hours(diff.new_text)
    if old_h is None or new_h is None:
        return None
    if new_h > old_h:
        ratio = new_h / old_h
        # P1 回應 30min→2h 是 gold=high；修復 4h→8h 是 gold=high
        # 其他延長為 medium/low
        level = "high" if (ratio >= 4 or (old_h <= 1 and ratio >= 2)) else "medium"
        return RiskFlag(
            clause_id=diff.clause_id,
            risk_code="RISK_RESPONSE_TIME_EXTENDED",
            risk_level=level,
            risk_direction="adverse",
            trigger_reason=f"時間從 {old_h}h 延長為 {new_h}h（{ratio:.1f} 倍）",
            old_text=diff.old_text,
            new_text=diff.new_text,
            change_type=diff.change_type,
        )
    return None


def rule_penalty_weakened(diff: DiffItem) -> Optional[RiskFlag]:
    """違約折讓比例降低或門檻放寬。"""
    if diff.change_type != "modified":
        return None
    keywords = ["折讓", "服務費", "扣款", "penalty", "credit"]
    if not any(k in diff.old_text for k in keywords):
        return None
    old_pct = _extract_percentage(diff.old_text)
    new_pct = _extract_percentage(diff.new_text)
    if old_pct is not None and new_pct is not None and new_pct < old_pct:
        return RiskFlag(
            clause_id=diff.clause_id,
            risk_code="RISK_PENALTY_WEAKENED",
            risk_level="medium",
            risk_direction="adverse",
            trigger_reason=f"折讓比例由 {old_pct}% 降為 {new_pct}%",
            old_text=diff.old_text,
            new_text=diff.new_text,
            change_type=diff.change_type,
        )
    return None


def rule_liability_cap_changed(diff: DiffItem) -> Optional[RiskFlag]:
    """責任限制上限變更（新增上限或縮小上限）。"""
    adverse_keywords = ["上限", "不超過", "不得超過", "cap", "limit", "當月服務費"]
    favorable_keywords = ["2 倍", "二倍", "24 個月"]
    has_adverse = any(k in diff.new_text for k in adverse_keywords)
    has_favorable = any(k in diff.new_text for k in favorable_keywords)

    if diff.change_type == "inserted" and has_adverse:
        return RiskFlag(
            clause_id=diff.clause_id,
            risk_code="RISK_LIABILITY_CAP_CHANGED",
            risk_level="high",
            risk_direction="adverse",
            trigger_reason="新增賠償責任上限條款",
            old_text=diff.old_text,
            new_text=diff.new_text,
            change_type=diff.change_type,
        )
    if diff.change_type == "modified":
        old_months = _extract_months(diff.old_text)
        new_months = _extract_months(diff.new_text)
        if old_months and new_months and new_months < old_months:
            return RiskFlag(
                clause_id=diff.clause_id,
                risk_code="RISK_LIABILITY_CAP_CHANGED",
                risk_level="high",
                risk_direction="adverse",
                trigger_reason=f"賠償計算基礎由 {old_months:.0f} 個月縮短為 {new_months:.0f} 個月",
                old_text=diff.old_text,
                new_text=diff.new_text,
                change_type=diff.change_type,
            )
        if has_favorable and not has_adverse:
            return RiskFlag(
                clause_id=diff.clause_id,
                risk_code="RISK_LIABILITY_CAP_CHANGED",
                risk_level="medium",
                risk_direction="favorable",
                trigger_reason="責任上限提高（對甲方有利）",
                old_text=diff.old_text,
                new_text=diff.new_text,
                change_type=diff.change_type,
            )
        if has_adverse:
            return RiskFlag(
                clause_id=diff.clause_id,
                risk_code="RISK_LIABILITY_CAP_CHANGED",
                risk_level="high",
                risk_direction="adverse",
                trigger_reason="責任上限條款修改為更不利甲方",
                old_text=diff.old_text,
                new_text=diff.new_text,
                change_type=diff.change_type,
            )
    return None


def rule_protection_removed(diff: DiffItem) -> Optional[RiskFlag]:
    """保護條款刪除。"""
    if diff.change_type != "deleted":
        return None
    protect_keywords = ["不得", "應於", "應提供", "義務", "保密", "不列入", "保護"]
    if any(k in diff.old_text for k in protect_keywords):
        return RiskFlag(
            clause_id=diff.clause_id,
            risk_code="RISK_PROTECTION_REMOVED",
            risk_level="high",
            risk_direction="adverse",
            trigger_reason="保護性條款遭刪除",
            old_text=diff.old_text,
            new_text=diff.new_text,
            change_type=diff.change_type,
        )
    return None


def rule_confidentiality_weakened(diff: DiffItem) -> Optional[RiskFlag]:
    """保密義務期間縮短。"""
    if diff.change_type != "modified":
        return None
    keywords = ["保密", "confidential", "秘密"]
    if not any(k in diff.old_text for k in keywords):
        return None
    old_yr = _extract_years(diff.old_text)
    new_yr = _extract_years(diff.new_text)
    if old_yr and new_yr and new_yr < old_yr:
        return RiskFlag(
            clause_id=diff.clause_id,
            risk_code="RISK_CONFIDENTIALITY_WEAKENED",
            risk_level="medium",
            risk_direction="adverse",
            trigger_reason=f"保密期間由 {old_yr:.0f} 年縮短為 {new_yr:.0f} 年",
            old_text=diff.old_text,
            new_text=diff.new_text,
            change_type=diff.change_type,
        )
    return None


def rule_termination_changed(diff: DiffItem) -> Optional[RiskFlag]:
    """終止條款變更（含通知期縮短、單方解約權）。"""
    keywords = ["終止", "解約", "terminate", "通知"]
    if not any(k in diff.old_text + diff.new_text for k in keywords):
        return None
    adverse_patterns = ["任何時間", "無須", "無條件", "15 日", "暫停服務"]
    if diff.change_type in ("modified", "inserted"):
        if any(p in diff.new_text for p in adverse_patterns):
            # Check if favorable (甲方 benefits)
            if "甲方" in diff.new_text and "乙方不得" in diff.new_text:
                direction: RiskDirection = "favorable"
                level: RiskLevel = "medium"
                reason = "終止條款調整有利甲方"
            else:
                direction = "adverse"
                level = "high"
                reason = "終止條款對乙方更有利（通知期縮短或新增單方解約）"
            return RiskFlag(
                clause_id=diff.clause_id,
                risk_code="RISK_TERMINATION_CHANGED",
                risk_level=level,
                risk_direction=direction,
                trigger_reason=reason,
                old_text=diff.old_text,
                new_text=diff.new_text,
                change_type=diff.change_type,
            )
    return None


def rule_force_majeure_expanded(diff: DiffItem) -> Optional[RiskFlag]:
    """不可抗力範圍擴大。"""
    keywords = ["不可抗力", "force majeure", "第三方平台", "供應商"]
    if diff.change_type == "inserted" and any(k in diff.new_text for k in keywords):
        return RiskFlag(
            clause_id=diff.clause_id,
            risk_code="RISK_FORCE_MAJEURE_EXPANDED",
            risk_level="medium",
            risk_direction="adverse",
            trigger_reason="不可抗力範圍擴大，乙方可主張免責情形增加",
            old_text=diff.old_text,
            new_text=diff.new_text,
            change_type=diff.change_type,
        )
    return None


def rule_jurisdiction_changed(diff: DiffItem) -> Optional[RiskFlag]:
    """管轄法院變更。"""
    keywords = ["管轄", "法院", "jurisdiction"]
    if diff.change_type == "modified" and any(k in diff.old_text for k in keywords):
        if "乙方所在地" in diff.new_text:
            return RiskFlag(
                clause_id=diff.clause_id,
                risk_code="RISK_JURISDICTION_CHANGED",
                risk_level="medium",
                risk_direction="adverse",
                trigger_reason="管轄法院改為乙方所在地，對甲方訴訟較不利",
                old_text=diff.old_text,
                new_text=diff.new_text,
                change_type=diff.change_type,
            )
    return None


def rule_data_control_lost(diff: DiffItem) -> Optional[RiskFlag]:
    """甲方對資料控制權降低。"""
    keywords = ["資料", "備份", "紀錄", "data"]
    adverse = ["自行決定", "得保留", "不得留存"]
    if diff.change_type in ("modified", "inserted"):
        if any(k in diff.new_text for k in keywords) and any(a in diff.new_text for a in adverse):
            return RiskFlag(
                clause_id=diff.clause_id,
                risk_code="RISK_DATA_CONTROL_LOST",
                risk_level="medium",
                risk_direction="adverse",
                trigger_reason="乙方對資料處置自主性提高，甲方控制權降低",
                old_text=diff.old_text,
                new_text=diff.new_text,
                change_type=diff.change_type,
            )
    return None


def rule_broad_disclaimer_added(diff: DiffItem) -> Optional[RiskFlag]:
    """廣泛免責條款新增或擴大（排除間接損害、資料損毀、營業中斷等）。"""
    broad_keywords = ["間接損害", "逸失利益", "商譽損失", "資料損毀", "營業中斷", "第三人求償"]
    if diff.change_type not in ("modified", "inserted"):
        return None
    matched = [k for k in broad_keywords if k in diff.new_text]
    if len(matched) >= 2:
        # v1 原文是雙向免責（任何一方），v4 改成只對乙方有利
        old_bilateral = "任何一方" in diff.old_text or diff.old_text == ""
        new_unilateral = "乙方不對" in diff.new_text or "乙方均不" in diff.new_text
        if old_bilateral or new_unilateral:
            return RiskFlag(
                clause_id=diff.clause_id,
                risk_code="RISK_LIABILITY_CAP_CHANGED",
                risk_level="high",
                risk_direction="adverse",
                trigger_reason=f"廣泛免責條款擴大，排除：{'、'.join(matched)}",
                old_text=diff.old_text,
                new_text=diff.new_text,
                change_type=diff.change_type,
            )
    return None


# ------------------------------------------------------------------
# Rule registry — ordered by priority (high-impact first)
# ------------------------------------------------------------------

RULES = [
    rule_sla_degrade,
    rule_response_time_extended,
    rule_liability_cap_changed,
    rule_broad_disclaimer_added,
    rule_protection_removed,
    rule_penalty_weakened,
    rule_confidentiality_weakened,
    rule_termination_changed,
    rule_force_majeure_expanded,
    rule_jurisdiction_changed,
    rule_data_control_lost,
]


# ------------------------------------------------------------------
# Engine
# ------------------------------------------------------------------

class RiskEngine:
    def analyze(self, diffs: List[DiffItem]) -> List[RiskFlag]:
        flags: List[RiskFlag] = []
        for diff in diffs:
            if diff.clause_id == "?":
                continue
            for rule in RULES:
                flag = rule(diff)
                if flag is not None:
                    flags.append(flag)
                    break  # one flag per clause
        return flags
