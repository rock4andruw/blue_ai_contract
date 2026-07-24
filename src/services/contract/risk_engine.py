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

_CN_DIGITS = {"零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
              "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
_FRACTION_BASE = {"千分": 1000, "百分": 100, "萬分": 10000}


def _cn_num_to_int(s: str) -> Optional[int]:
    """Convert a simple Chinese numeral (0-99) to int. e.g. 三→3, 二十三→23, 十→10."""
    if not s:
        return None
    if s.isdigit():
        return int(s)
    if s == "十":
        return 10
    if "十" in s:
        tens_str, _, units_str = s.partition("十")
        tens = _CN_DIGITS.get(tens_str, 1) if tens_str else 1
        units = _CN_DIGITS.get(units_str, 0) if units_str else 0
        return tens * 10 + units
    return _CN_DIGITS.get(s)


def _extract_percentage(text: str) -> Optional[float]:
    """Extract a percentage from Arabic (12.5%／12.5％) or Chinese fraction
    notation (千分之一/百分之三十/萬分之五).

    千分之一 vs "0.3%" are semantically incomparable as raw strings —
    normalize both to the same 0-100 scale so numeric rules can compare
    across formats (千分之一 = 0.1%, distinct from 0.3%). Contracts also
    mix full-width ％ (U+FF05) with half-width %, both are accepted.

    NOTE: this grabs the *first* percentage found in the text. Clauses that
    state both a rate and a cap in one sentence (e.g. "每日 0.3% 違約金，
    總額以 30% 為上限") need a context-scoped extractor instead — see
    _extract_rate_percentage / _extract_cap_percentage.
    """
    m = re.search(r'(\d+(?:\.\d+)?)\s*[%％]', text)
    if m:
        return float(m.group(1))
    m = re.search(r'(千分|百分|萬分)之([零一二三四五六七八九十\d]+)', text)
    if m:
        base = _FRACTION_BASE[m.group(1)]
        num = _cn_num_to_int(m.group(2))
        if num is not None:
            return num / base * 100
    return None


def _extract_rate_percentage(text: str) -> Optional[float]:
    """Extract a penalty-rate percentage scoped to '...% 之懲罰性違約金'
    style phrasing, distinct from a liability-cap percentage that may
    appear later in the same clause (see _extract_cap_percentage).
    """
    m = re.search(r'(\d+(?:\.\d+)?)\s*[%％]\s*之?(?:懲罰性)?違約金', text)
    if m:
        return float(m.group(1))
    m = re.search(r'(千分|百分|萬分)之([零一二三四五六七八九十\d]+)\s*之?(?:懲罰性)?違約金', text)
    if m:
        base = _FRACTION_BASE[m.group(1)]
        num = _cn_num_to_int(m.group(2))
        if num is not None:
            return num / base * 100
    return None


def _extract_cap_percentage(text: str) -> Optional[float]:
    """Extract a liability-cap percentage scoped to '...% 為上限' / '不得
    超過...%' style phrasing, distinct from a penalty-rate percentage that
    may appear earlier in the same clause (see _extract_rate_percentage).
    """
    m = re.search(r'(\d+(?:\.\d+)?)\s*[%％]\s*為上限', text)
    if m:
        return float(m.group(1))
    m = re.search(r'(千分|百分|萬分)之([零一二三四五六七八九十\d]+)\s*為上限', text)
    if m:
        base = _FRACTION_BASE[m.group(1)]
        num = _cn_num_to_int(m.group(2))
        if num is not None:
            return num / base * 100
    m = re.search(r'(?:不得超過|不超過|不逾)[^%％為]{0,20}?(\d+(?:\.\d+)?)\s*[%％]', text)
    if m:
        return float(m.group(1))
    m = re.search(r'(?:不得超過|不超過|不逾)[^%％為]{0,20}?(千分|百分|萬分)之([零一二三四五六七八九十\d]+)', text)
    if m:
        base = _FRACTION_BASE[m.group(1)]
        num = _cn_num_to_int(m.group(2))
        if num is not None:
            return num / base * 100
    return None


def _extract_scoped_hours(text: str, keyword: str) -> Optional[float]:
    """Extract a duration (normalized to hours) tied to a specific SLA
    commitment keyword (回覆/到場/修復), scoped separately from other
    duration commitments stated in the same sentence.

    e.g. "4小時內回覆、於4小時內到場，並須於2日內完成修復" states three
    independent commitments — a single generic extractor can't tell them
    apart, so a change to just the repair time would be silently missed.
    """
    m = re.search(rf'(\d+(?:\.\d+)?)\s*(小時|個工作日|[日天]|分鐘)內?.{{0,4}}?{re.escape(keyword)}', text)
    if not m:
        return None
    value, unit = float(m.group(1)), m.group(2)
    if unit == "小時":
        return value
    if unit == "個工作日":
        return value * 8
    if unit in ("日", "天"):
        return value * 24
    return value / 60  # 分鐘


def _extract_months(text: str) -> Optional[float]:
    m = re.search(r'(\d+(?:\.\d+)?)\s*個月', text)
    return float(m.group(1)) if m else None


def _extract_years(text: str) -> Optional[float]:
    """Extract a year count from Arabic (5年) or Chinese numeral (五年/二年) notation.

    Contracts (especially NDAs) commonly write duration in Chinese numerals
    rather than Arabic digits -- without this fallback, rule_confidentiality_weakened()
    silently misses any "五年→二年" style change (confirmed via
    scratchpad/test_nda_confidentiality_rule.py: fires correctly on "5年→2年"
    but not at all on the Chinese-numeral equivalent).
    """
    m = re.search(r'(\d+(?:\.\d+)?)\s*年', text)
    if m:
        return float(m.group(1))
    m = re.search(r'([零一二三四五六七八九十]+)\s*年', text)
    if m:
        num = _cn_num_to_int(m.group(1))
        return float(num) if num is not None else None
    return None


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


# 一句條款常同時承諾多個時限（回覆／到場／修復），必須各自獨立比對，
# 否則像「回覆4小時、到場4小時、修復2日」這種句子，只有「修復」時間被
# 拉長時，會被誤判成沒有變化（因為第一個抓到的「4小時」沒變）。
_RESPONSE_TIME_COMMITMENTS = [
    ("回覆", "回應/回覆時間"),
    ("回應", "回應/回覆時間"),
    ("到場", "到場時間"),
    ("修復", "修復/處理時間"),
    ("處理", "修復/處理時間"),
]


def rule_response_time_extended(diff: DiffItem) -> Optional[RiskFlag]:
    """回應／到場／修復時間拉長（三種時限各自獨立比對）。"""
    if diff.change_type != "modified":
        return None
    keywords = ["回應", "回覆", "到場", "修復", "處理", "response", "repair", "resolve"]
    if not any(k in diff.old_text for k in keywords):
        return None

    checked_labels = set()
    for kw, label in _RESPONSE_TIME_COMMITMENTS:
        if label in checked_labels:
            continue
        old_h = _extract_scoped_hours(diff.old_text, kw)
        new_h = _extract_scoped_hours(diff.new_text, kw)
        if old_h is None or new_h is None or old_h <= 0:
            continue
        checked_labels.add(label)
        if new_h > old_h:
            ratio = new_h / old_h
            # P1 回應 30min→2h 是 gold=high；修復 4h→8h 是 gold=high
            level = "high" if (ratio >= 4 or (old_h <= 1 and ratio >= 2)) else "medium"
            return RiskFlag(
                clause_id=diff.clause_id,
                risk_code="RISK_RESPONSE_TIME_EXTENDED",
                risk_level=level,
                risk_direction="adverse",
                trigger_reason=f"{label}由 {old_h:g}h 延長為 {new_h:g}h（{ratio:.1f} 倍）",
                old_text=diff.old_text,
                new_text=diff.new_text,
                change_type=diff.change_type,
            )

    # 沒有情境限定的 fallback：泛用抽取（不管數字跟哪個關鍵字有沒有關聯）
    # 曾經造成假警報——例如付款條款裡的「發票處理」命中「處理」關鍵字，
    # 跟旁邊完全無關的月結天數（1日→60日）湊在一起被誤判成回應時間拉長
    # 60 倍。抓不到情境限定的時限就不判，交給 Verification Agent 語意判斷。
    return None


def rule_penalty_weakened(diff: DiffItem) -> Optional[RiskFlag]:
    """違約折讓比例或違約金費率降低。"""
    if diff.change_type != "modified":
        return None
    keywords = ["折讓", "服務費", "扣款", "penalty", "credit", "違約金", "罰款", "懲罰性"]
    if not any(k in diff.old_text for k in keywords):
        return None
    # 優先用情境限定的費率抽取（區分於責任上限百分比），避免同句中的
    # 上限數字被誤當成費率比較（見 _extract_rate_percentage）。
    old_pct = _extract_rate_percentage(diff.old_text) or _extract_percentage(diff.old_text)
    new_pct = _extract_rate_percentage(diff.new_text) or _extract_percentage(diff.new_text)
    if old_pct is not None and new_pct is not None and new_pct < old_pct:
        return RiskFlag(
            clause_id=diff.clause_id,
            risk_code="RISK_PENALTY_WEAKENED",
            risk_level="medium",
            risk_direction="adverse",
            trigger_reason=f"違約金/折讓比例由 {old_pct:g}% 降為 {new_pct:g}%",
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
            # 情境限定抽取責任上限的百分比（區分於同句中可能存在的違約金
            # 費率百分比），只有上限數值真的變小才判定為此類風險；
            # 上限數值不變（只是句子裡剛好也出現「上限」字樣）不算，
            # 讓其他規則（如 rule_penalty_weakened）去抓真正變化的部分。
            old_cap = _extract_cap_percentage(diff.old_text)
            new_cap = _extract_cap_percentage(diff.new_text)
            if old_cap is not None and new_cap is not None:
                if new_cap < old_cap:
                    return RiskFlag(
                        clause_id=diff.clause_id,
                        risk_code="RISK_LIABILITY_CAP_CHANGED",
                        risk_level="high",
                        risk_direction="adverse",
                        trigger_reason=f"責任上限比例由 {old_cap:g}% 降為 {new_cap:g}%",
                        old_text=diff.old_text,
                        new_text=diff.new_text,
                        change_type=diff.change_type,
                    )
                return None  # 上限數值不變或提高，非此規則要抓的變化

            has_adverse_old = any(k in diff.old_text for k in adverse_keywords)
            if not has_adverse_old:
                return RiskFlag(
                    clause_id=diff.clause_id,
                    risk_code="RISK_LIABILITY_CAP_CHANGED",
                    risk_level="high",
                    risk_direction="adverse",
                    trigger_reason="新增責任上限相關條款",
                    old_text=diff.old_text,
                    new_text=diff.new_text,
                    change_type=diff.change_type,
                )
            # 兩邊都有上限相關文字，但抓不到可比較的百分比（例如上限用
            # 絕對金額表示）——保守起見仍標記，避免漏判。
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

def rule_ip_ownership_changed(diff: DiffItem) -> Optional[RiskFlag]:
    """智慧財產權歸屬改變（NDA / 委外合約）。"""
    if diff.change_type != "modified":
        return None
    keywords = ["智慧財產權", "所有權", "著作權", "專利"]
    if not any(k in (diff.old_text or "") for k in keywords):
        return None
    # 歸屬從甲方→乙方或反向轉移
    old_owner = "甲方" if "歸甲方所有" in (diff.old_text or "") or "應為甲方所有" in (diff.old_text or "") else None
    new_owner = "乙方" if "歸乙方所有" in (diff.new_text or "") or "應為乙方所有" in (diff.new_text or "") else None
    if old_owner and new_owner:
        return RiskFlag(
            clause_id=diff.clause_id,
            risk_code="RISK_IP_OWNERSHIP_CHANGED",
            risk_level="high",
            risk_direction="adverse",
            trigger_reason=f"智慧財產權歸屬由{old_owner}改為{new_owner}，原有 IP 控制權喪失",
            old_text=diff.old_text,
            new_text=diff.new_text,
            change_type=diff.change_type,
        )
    return None


def rule_liability_direction_reversed(diff: DiffItem) -> Optional[RiskFlag]:
    """違約賠償責任方向反轉（由乙方賠甲方→甲方賠乙方，對甲方不利）。"""
    if diff.change_type != "modified":
        return None
    keywords = ["懲罰性違約金", "賠償", "違約"]
    if not any(k in (diff.old_text or "") for k in keywords):
        return None
    old_liable = "乙方" if re.search(r'乙方.{0,10}(違反|賠償|應賠)', diff.old_text or "") else None
    new_liable = "甲方" if re.search(r'甲方.{0,10}(違反|賠償|應賠)', diff.new_text or "") else None
    if old_liable and new_liable:
        return RiskFlag(
            clause_id=diff.clause_id,
            risk_code="RISK_LIABILITY_DIRECTION_REVERSED",
            risk_level="high",
            risk_direction="adverse",
            trigger_reason="違約賠償責任方向反轉：原本乙方賠甲方，改為甲方承擔賠償責任",
            old_text=diff.old_text,
            new_text=diff.new_text,
            change_type=diff.change_type,
        )
    return None


_BILATERAL_MARKERS = ["雙方", "互負保密義務", "互相保密", "互為保密", "雙務"]


def rule_confidentiality_scope_changed(diff: DiffItem) -> Optional[RiskFlag]:
    """保密義務範圍改變（單務→雙務）。

    僅在新版明確出現「雙方互保」這類雙務用語、且舊版沒有時才判定為範圍改變。
    先前版本用「乙方…接受方」關鍵字共現當代理指標，會被純粹的用詞替換（例如
    條款全文把「乙方」改稱「接受方」但義務主體完全沒變）誤觸發——「接受方」
    是 NDA 常見的角色泛稱，不能直接當作「變雙務」的證據（見
    scratchpad/test_confidentiality_scope_bug.py 的假警報重現案例）。
    """
    if diff.change_type != "modified":
        return None
    keywords = ["保密義務", "機密資訊"]
    if not any(k in (diff.old_text or "") for k in keywords):
        return None
    old_bilateral = any(m in (diff.old_text or "") for m in _BILATERAL_MARKERS)
    new_bilateral = any(m in (diff.new_text or "") for m in _BILATERAL_MARKERS)
    scope_change = new_bilateral and not old_bilateral
    if scope_change:
        return RiskFlag(
            clause_id=diff.clause_id,
            risk_code="RISK_CONFIDENTIALITY_SCOPE_CHANGED",
            risk_level="medium",
            risk_direction="adverse",
            trigger_reason="保密義務範圍改變：由單務（乙方保密）改為雙務（雙方互保），需確認對公司的實際影響",
            old_text=diff.old_text,
            new_text=diff.new_text,
            change_type=diff.change_type,
        )
    return None


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
    rule_ip_ownership_changed,
    rule_liability_direction_reversed,
    rule_confidentiality_scope_changed,
]


# ------------------------------------------------------------------
# Engine
# ------------------------------------------------------------------

class RiskEngine:
    def analyze(self, diffs: List[DiffItem]) -> List[RiskFlag]:
        flags: List[RiskFlag] = []
        for diff in diffs:
            for rule in RULES:
                flag = rule(diff)
                if flag is not None:
                    flags.append(flag)
                    break  # one flag per clause
        return flags
