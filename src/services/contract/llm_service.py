"""LLM Summary & Negotiation Service.

Receives structured risk_flags from RiskEngine and produces:
- Plain-language summary per flag
- 3-5 key change highlights
- 2-3 negotiation options per high-risk flag
"""

import os
from typing import List, Optional
from .schemas import RiskFlag, ReportSection, RISK_CODES


SYSTEM_PROMPT = """你是專業的合約審查助理，專注於台灣企業 SLA / NDA / 採購合約的風險分析。

你的任務是把已由規則引擎標記的風險條款，翻譯成：
1. 白話說明（非法律工程語言）
2. 商業影響（對公司運營的實際影響）
3. 協商對策（2-3 個可直接用於談判的具體方案）

輸出格式為 JSON，欄位：
{
  "plain_summary": "一句話白話說明",
  "business_impact": "商業影響說明",
  "negotiation_options": ["對策 A", "對策 B", "對策 C"]
}

注意：
- 使用繁體中文
- 協商對策要具體，不要模糊建議
- 不要重複 trigger_reason 的用詞，要用更口語的方式說明
"""


def _build_user_prompt(flag: RiskFlag, reference_clause: str = "") -> str:
    risk_name = RISK_CODES.get(flag.risk_code, flag.risk_code)
    ref_section = f"\n參考標準條款：\n{reference_clause}" if reference_clause else ""
    return f"""風險類型：{risk_name}
風險等級：{flag.risk_level}
觸發原因：{flag.trigger_reason}

原始條款：
{flag.old_text or '（無，為新增條款）'}

修改後條款：
{flag.new_text or '（已刪除）'}
{ref_section}

請產出 JSON 格式的分析結果。"""


def analyze_flag(flag: RiskFlag, reference_clause: str = "", api_key: Optional[str] = None) -> ReportSection:
    """Analyze a single RiskFlag using Claude API. Falls back to template if no API key."""
    key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")

    if key:
        return _analyze_with_claude(flag, reference_clause, key)
    else:
        return _analyze_with_template(flag)


def _analyze_with_claude(flag: RiskFlag, reference_clause: str, api_key: str) -> ReportSection:
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic not installed: pip install anthropic")

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _build_user_prompt(flag, reference_clause)}],
    )

    import json
    text = message.content[0].text.strip()
    # Extract JSON from response
    start = text.find("{")
    end = text.rfind("}") + 1
    data = json.loads(text[start:end])

    return ReportSection(
        rank=0,
        clause_id=flag.clause_id,
        risk_level=flag.risk_level,
        risk_code=flag.risk_code,
        plain_summary=data.get("plain_summary", ""),
        business_impact=data.get("business_impact", ""),
        negotiation_options=data.get("negotiation_options", []),
    )


def _analyze_with_template(flag: RiskFlag) -> ReportSection:
    """Rule-based fallback when no API key is available."""
    templates = {
        "RISK_SLA_DEGRADE": {
            "plain_summary": f"服務可用率標準降低（{flag.trigger_reason}），允許更多停機時間。",
            "business_impact": "系統停機容忍時間增加，對業務關鍵系統影響顯著，可能導致服務中斷風險上升。",
            "negotiation_options": [
                "要求維持原可用率標準，以業務關鍵性為談判依據",
                "若接受降低，要求對應提高賠償比例（如從 5% 提高至 15%）",
                "要求加入即時監控與停機主動通知義務作為補償",
            ],
        },
        "RISK_RESPONSE_TIME_EXTENDED": {
            "plain_summary": f"事件回應或修復時間拉長（{flag.trigger_reason}），故障處理速度下降。",
            "business_impact": "重大故障發生時，服務恢復時間延長，業務中斷影響加大，客戶滿意度風險上升。",
            "negotiation_options": [
                "要求維持原回應時間標準，至少 P1 事件不得放寬",
                "若接受放寬，要求對超時部分加計賠償或服務折讓",
                "要求加入 escalation 機制，超時自動升級處理層級",
            ],
        },
        "RISK_LIABILITY_CAP_CHANGED": {
            "plain_summary": f"賠償責任上限條款變更（{flag.trigger_reason}），實際可求償金額降低。",
            "business_impact": "即使乙方嚴重違約，可求償金額受到限制，對甲方保障大幅降低。",
            "negotiation_options": [
                "要求恢復原賠償計算基礎（最近 12 個月服務費）",
                "要求明確列出不適用上限的情形（如重大過失、資安事件）",
                "要求賠償上限不低於合約總值的 50%",
            ],
        },
        "RISK_PROTECTION_REMOVED": {
            "plain_summary": f"保護性條款遭刪除（{flag.trigger_reason}），原有權益喪失。",
            "business_impact": "原合約中保護甲方的條款消失，乙方義務減少，甲方可追訴空間縮小。",
            "negotiation_options": [
                "要求恢復被刪除的條款",
                "若乙方堅持，要求以其他條款補償對應的保護效果",
                "要求將刪除條款的內容改列為附件，維持約束效力",
            ],
        },
        "RISK_PENALTY_WEAKENED": {
            "plain_summary": f"違約折讓條件放寬（{flag.trigger_reason}），乙方違約代價降低。",
            "business_impact": "乙方未達服務水準時，甲方可獲得的補償減少，對乙方的約束力下降。",
            "negotiation_options": [
                "要求維持原折讓比例（至少 5%）",
                "若折讓比例降低，要求降低觸發門檻作為補償",
                "要求加入累計未達標的懲罰機制",
            ],
        },
        "RISK_CONFIDENTIALITY_WEAKENED": {
            "plain_summary": f"保密義務期間縮短（{flag.trigger_reason}），機密保護期間減少。",
            "business_impact": "合約終止後，商業機密、客戶資料的保護期間縮短，外洩風險上升。",
            "negotiation_options": [
                "要求維持保密期間至少 3 年",
                "要求將特定類型資料（如客戶名單、定價）保密期間延長至 5 年",
                "要求保密義務適用範圍擴及乙方員工與委外合作商",
            ],
        },
        "RISK_TERMINATION_CHANGED": {
            "plain_summary": f"終止條款變更（{flag.trigger_reason}）。",
            "business_impact": "合約終止條件改變，可能影響雙方對合約期間的掌控與規劃。",
            "negotiation_options": [
                "要求終止通知期至少 30 天",
                "要求明確列出可終止事由，避免模糊條款",
                "要求終止後的交接與資料返還義務加入違約罰則",
            ],
        },
        "RISK_FORCE_MAJEURE_EXPANDED": {
            "plain_summary": f"不可抗力範圍擴大（{flag.trigger_reason}），乙方免責空間增加。",
            "business_impact": "第三方平台故障、供應商問題等也可被視為不可抗力，乙方可更容易主張免責。",
            "negotiation_options": [
                "要求限縮不可抗力定義，排除乙方可合理預見或控制的情形",
                "要求不可抗力期間超過 30 天時，甲方有權終止合約",
                "要求乙方建立備援機制，不可抗力不得作為長期免責依據",
            ],
        },
        "RISK_JURISDICTION_CHANGED": {
            "plain_summary": f"管轄法院改變（{flag.trigger_reason}），訴訟地點對甲方較不利。",
            "business_impact": "爭議發生時，甲方需前往乙方所在地提告，增加訴訟成本與不便。",
            "negotiation_options": [
                "要求維持台灣臺北地方法院為第一審管轄",
                "若乙方堅持，提出以雙方協商地點或仲裁替代訴訟",
                "要求加入線上仲裁條款，降低地點不利的實際影響",
            ],
        },
        "RISK_DATA_CONTROL_LOST": {
            "plain_summary": f"甲方對資料的控制權降低（{flag.trigger_reason}）。",
            "business_impact": "合約終止後，乙方可能保留敏感資料，增加資料外洩或濫用風險。",
            "negotiation_options": [
                "要求合約終止後 7 日內完成資料刪除並提供書面證明",
                "要求乙方不得將履約資料用於任何商業目的",
                "要求加入資料稽核權，甲方可查驗資料處置狀況",
            ],
        },
    }

    t = templates.get(flag.risk_code, {
        "plain_summary": f"條款變更：{flag.trigger_reason}",
        "business_impact": "需進一步評估商業影響。",
        "negotiation_options": ["建議法務人員進一步審閱此條款"],
    })

    return ReportSection(
        rank=0,
        clause_id=flag.clause_id,
        risk_level=flag.risk_level,
        risk_code=flag.risk_code,
        plain_summary=t["plain_summary"],
        business_impact=t["business_impact"],
        negotiation_options=t["negotiation_options"],
    )


def generate_sections(
    flags: List[RiskFlag],
    api_key: Optional[str] = None,
    max_sections: int = 5,
) -> List[ReportSection]:
    """Generate ReportSections for the top N highest-risk flags."""
    # Prioritise: high > medium > low, then by clause_id order
    level_order = {"high": 0, "medium": 1, "low": 2, "none": 3}
    adverse_flags = [f for f in flags if f.risk_direction == "adverse"]
    sorted_flags = sorted(adverse_flags, key=lambda f: level_order.get(f.risk_level, 9))
    top_flags = sorted_flags[:max_sections]

    sections = []
    for rank, flag in enumerate(top_flags, start=1):
        section = analyze_flag(flag, api_key=api_key)
        section.rank = rank
        sections.append(section)

    return sections
