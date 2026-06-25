"""Report Generator: assembles all pipeline outputs into a ComparisonReport and Markdown."""

import re
from datetime import date
from typing import List
from .schemas import (
    ComparisonReport, DiffItem, ReportSection, RiskFlag, RiskLevel, RISK_CODES
)


LEVEL_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢", "none": "⚪"}
LEVEL_ZH = {"high": "高風險", "medium": "中風險", "low": "低風險", "none": "無風險"}
OVERALL_VERDICT = {
    "high":   "🔴 **高度風險，建議協商後再簽署，必要時請法務審閱**",
    "medium": "🟡 **中度風險，建議就以下條款協商後再簽署**",
    "low":    "🟢 **低風險，可接受，留意標記條款即可**",
    "none":   "🟢 **無顯著風險，可接受**",
}


def _overall_level(flags: List[RiskFlag]) -> RiskLevel:
    levels = {f.risk_level for f in flags if f.risk_direction == "adverse"}
    if "high" in levels:
        return "high"
    if "medium" in levels:
        return "medium"
    if "low" in levels:
        return "low"
    return "none"


def build_report(
    original_filename: str,
    revised_filename: str,
    diffs: List[DiffItem],
    flags: List[RiskFlag],
    sections: List[ReportSection],
) -> ComparisonReport:
    adverse = [f for f in flags if f.risk_direction == "adverse"]
    high = [f for f in adverse if f.risk_level == "high"]
    medium = [f for f in adverse if f.risk_level == "medium"]
    low = [f for f in adverse if f.risk_level == "low"]
    overall = _overall_level(flags)

    must_negotiate = [f.clause_id for f in high]
    suggested = [f.clause_id for f in medium]
    acceptable = [d.clause_id for d in diffs
                  if d.clause_id not in must_negotiate + suggested and d.clause_id != "?"]

    return ComparisonReport(
        original_filename=original_filename,
        revised_filename=revised_filename,
        total_changes=len([d for d in diffs if d.clause_id != "?"]),
        high_risk_count=len(high),
        medium_risk_count=len(medium),
        low_risk_count=len(low),
        overall_risk_level=overall,
        overall_assessment=OVERALL_VERDICT[overall],
        key_sections=sections,
        all_risk_flags=adverse,
        must_negotiate=must_negotiate,
        suggested_negotiate=suggested,
        acceptable=acceptable,
    )


def to_markdown(report: ComparisonReport) -> str:
    today = date.today().strftime("%Y-%m-%d")
    lines = []

    lines.append("# 合約比對報告\n")
    lines.append(f"**原始版本**: {report.original_filename}  ")
    lines.append(f"**修訂版本**: {report.revised_filename}  ")
    lines.append(f"**比對日期**: {today}  ")
    lines.append(
        f"**總變動**: {report.total_changes} 處"
        f"（高風險 {report.high_risk_count}、"
        f"中風險 {report.medium_risk_count}、"
        f"低風險 {report.low_risk_count}）\n"
    )
    lines.append("---\n")

    lines.append("## 整體評估\n")
    lines.append(report.overall_assessment)
    lines.append("\n---\n")

    lines.append("## 主要變更重點\n")
    if not report.key_sections:
        lines.append("_未偵測到顯著風險條款。_\n")
    else:
        for s in report.key_sections:
            emoji = LEVEL_EMOJI.get(s.risk_level, "")
            level_zh = LEVEL_ZH.get(s.risk_level, "")
            risk_name = RISK_CODES.get(s.risk_code, s.risk_code)
            clause_label = f"第 {s.clause_id} 條" if re.match(r'^[\d一二三四五六七八九十\.]+$', s.clause_id) else s.clause_id
            lines.append(f"### {s.rank}. {emoji} {risk_name}（{clause_label}）\n")
            lines.append(f"**風險等級**: {level_zh}  ")
            lines.append(f"**說明**: {s.plain_summary}  ")
            lines.append(f"**商業影響**: {s.business_impact}\n")
            lines.append("**協商對策**：\n")
            for opt in s.negotiation_options:
                lines.append(f"- {opt}")
            lines.append("")

    lines.append("\n---\n")
    lines.append("## 審閱建議\n")

    def _fmt_clause(cid: str) -> str:
        return f"第 {cid} 條" if re.match(r'^[\d一二三四五六七八九十\.]+$', cid) else cid

    if report.must_negotiate:
        lines.append(f"**必須協商**：{'、'.join(_fmt_clause(c) for c in report.must_negotiate)}  ")
    if report.suggested_negotiate:
        lines.append(f"**建議協商**：{'、'.join(_fmt_clause(c) for c in report.suggested_negotiate)}  ")
    if report.acceptable:
        lines.append(f"**可接受**：其他 {len(report.acceptable)} 處行政性變更")

    lines.append("\n---\n")
    lines.append("## 完整風險旗標\n")
    lines.append("| 條款 | 風險等級 | 風險類型 | 觸發原因 |")
    lines.append("| --- | --- | --- | --- |")
    for f in report.all_risk_flags:
        emoji = LEVEL_EMOJI.get(f.risk_level, "")
        risk_name = RISK_CODES.get(f.risk_code, f.risk_code)
        lines.append(f"| {f.clause_id} | {emoji} {LEVEL_ZH.get(f.risk_level,'')} | {risk_name} | {f.trigger_reason} |")

    lines.append("\n---\n")
    lines.append("_本報告由 AI 輔助生成，所有分析僅供參考，最終決策需由法務人員確認。_")

    return "\n".join(lines)
