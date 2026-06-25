"""Three-tier Playbook negotiation service.

Given a risk_code + clause context, returns tier1 (preferred), tier2 (fallback),
and redline (walkaway) positions for negotiation.
"""

import json
import logging
import os
from typing import Optional

STATIC_PLAYBOOK: dict[str, dict] = {
    "RISK_SLA_DEGRADE": {
        "tier1": "要求恢復原可用率標準（如 99.9%），並保留現行賠償機制不變。",
        "tier1_clause": "服務可用率不得低於 99.9%（每月計算），未達標準時乙方應依第 X 條給付服務折讓。",
        "tier2": "接受可用率降至 99.5%，但要求對應提高賠償比例至 10% 以上，並加入停機主動通知義務。",
        "tier2_clause": "服務可用率不得低於 99.5%（每月計算）；未達標準時乙方應主動通知甲方並給付不低於當月服務費 10% 之折讓。",
        "redline": "可用率低於 99%，或賠償比例低於 5%，或取消主動通知義務——任一條件均不可接受。",
    },
    "RISK_RESPONSE_TIME_EXTENDED": {
        "tier1": "要求恢復原回應時間標準：P1 事件 1 小時內回應、4 小時內提供解決方案。",
        "tier1_clause": "乙方應於收到 P1 級故障通報後 1 小時內回應，並於 4 小時內提供解決方案或書面說明。",
        "tier2": "接受 P1 回應時間延至 2 小時，但要求超時後自動升級處理層級，並加計 5% 服務折讓。",
        "tier2_clause": "P1 級事件回應時間不得超過 2 小時；超時每小時加計 5% 服務折讓，並自動升級至乙方技術長層級。",
        "redline": "P1 回應時間超過 4 小時，或取消自動升級機制——不可接受。",
    },
    "RISK_LIABILITY_CAP_CHANGED": {
        "tier1": "要求恢復賠償計算基礎為最近 12 個月累積服務費，且故意或重大過失不適用上限。",
        "tier1_clause": "乙方賠償責任上限不得低於本合約前十二（12）個月累積服務費；故意或重大過失所致損害不受本條上限限制。",
        "tier2": "接受上限降至 6 個月服務費，但要求明確列出不適用上限的情形（故意、重大過失、資安事件）。",
        "tier2_clause": "乙方賠償責任上限為本合約前六（6）個月累積服務費；惟因故意、重大過失或資安事件所致損害，不受本條上限限制。",
        "redline": "賠償上限低於 3 個月服務費，或以單月服務費計算，且無任何例外條款——不可接受。",
    },
    "RISK_PROTECTION_REMOVED": {
        "tier1": "要求完整恢復被刪除條款，維持原有保護效力。",
        "tier1_clause": "（請恢復原合約對應條款全文）",
        "tier2": "若乙方堅持刪除，要求以附件形式保留約束效力，或以其他同等效力條款補充。",
        "tier2_clause": "雙方同意以附件 X《補充保護條款》補充規範本合約被刪除之相關義務，附件具同等法律效力。",
        "redline": "完全刪除且無任何替代補充機制——不可接受。",
    },
    "RISK_PENALTY_WEAKENED": {
        "tier1": "要求維持原折讓比例，未達服務水準時折讓不得低於 5%。",
        "tier1_clause": "未達服務水準協議之月份，乙方應給付甲方不低於當月服務費 5% 之服務折讓。",
        "tier2": "接受折讓比例降至 3%，但要求降低觸發門檻，或加入連續未達標的累計懲罰機制。",
        "tier2_clause": "未達服務水準協議之月份，乙方給付 3% 服務折讓；連續三個月未達標時，折讓比例自動提升至 8%。",
        "redline": "折讓比例低於 1%，或取消自動觸發機制，改為申請制——不可接受。",
    },
    "RISK_CONFIDENTIALITY_WEAKENED": {
        "tier1": "要求保密期間至少 3 年，並擴及乙方員工與委外廠商。",
        "tier1_clause": "保密義務自合約終止日起延續三（3）年；乙方應確保其員工及委外合作商受同等保密約束。",
        "tier2": "接受保密期間降至 2 年，但要求特定資料類型（客戶名單、定價）保密期間維持 3 年。",
        "tier2_clause": "一般保密資訊保密期間為二（2）年；客戶名單、定價資訊及技術文件保密期間為三（3）年。",
        "redline": "保密期間少於 1 年，或不覆蓋乙方員工——不可接受。",
    },
    "RISK_TERMINATION_CHANGED": {
        "tier1": "要求終止通知期至少 30 天，並明確列出可終止事由。",
        "tier1_clause": "任一方欲終止本合約，應提前三十（30）日以書面通知他方；可終止事由限於以下明確情形：[列舉]。",
        "tier2": "接受通知期縮短至 14 天，但要求乙方在終止後 7 天內完成資料交接及返還。",
        "tier2_clause": "終止通知期不得少於十四（14）日；乙方應於終止生效後七（7）日內完成資料返還及系統存取權限撤銷。",
        "redline": "無通知期或單方即時終止權，且無交接義務——不可接受。",
    },
    "RISK_FORCE_MAJEURE_EXPANDED": {
        "tier1": "要求限縮不可抗力定義，排除乙方供應商故障、第三方平台中斷等可預見風險。",
        "tier1_clause": "不可抗力事件限於天災、戰爭、政府命令等乙方無法合理預見或控制之情形；乙方供應商或第三方服務商之故障不在此列。",
        "tier2": "接受第三方平台故障列入不可抗力，但要求乙方建立備援機制，且不可抗力期間超過 30 天時甲方有權終止。",
        "tier2_clause": "不可抗力期間持續逾三十（30）日時，甲方得以書面通知乙方無條件終止本合約，免付任何違約金。",
        "redline": "不可抗力定義無限擴大，涵蓋一般技術故障，且無時限限制——不可接受。",
    },
    "RISK_IP_OWNERSHIP_CHANGED": {
        "tier1": "要求所有履約成果之智財權歸甲方所有，乙方僅保留原有底層技術授權。",
        "tier1_clause": "乙方因履行本合約所產生之所有成果、文件、程式碼之智慧財產權歸屬甲方；乙方原有技術之智財權不受影響，乙方授予甲方永久無償使用授權。",
        "tier2": "若乙方堅持保留部分 IP，要求甲方取得永久無償使用授權及再授權第三人之權利。",
        "tier2_clause": "乙方保留履約成果之智慧財產權，但須授予甲方全球性、永久性、免費之使用、複製及再授權權利。",
        "redline": "智財權完全歸屬乙方且甲方無授權使用——不可接受。",
    },
    "RISK_LIABILITY_DIRECTION_REVERSED": {
        "tier1": "要求恢復原條款：違約賠償責任由乙方單向承擔，甲方不負懲罰性違約金義務。",
        "tier1_clause": "因乙方違約所致損害，由乙方負賠償責任；甲方之違約責任以實際損害為限，不適用懲罰性違約金條款。",
        "tier2": "接受雙向責任，但要求明確限縮甲方可能違約之情境，並將懲罰性違約金上限降至合約總值 10%。",
        "tier2_clause": "雙方違約賠償以實際損害為限；懲罰性違約金僅適用於以下明確事由：[列舉]，且上限為合約總值之百分之十（10%）。",
        "redline": "甲方須承擔高額固定懲罰性違約金（超過合約總值 20%）且無例外條款——不可接受。",
    },
    "RISK_CONFIDENTIALITY_SCOPE_CHANGED": {
        "tier1": "確認雙務保密是否對公司有利；若不接受，要求恢復單務保密條款。",
        "tier1_clause": "保密義務由乙方單向承擔，甲方不負本合約保密義務；乙方應對甲方提供之一切資訊負保密責任。",
        "tier2": "接受雙務保密，但要求明確定義甲方機密資訊範圍，避免模糊條款擴大甲方責任。",
        "tier2_clause": "雙方互負保密義務；甲方機密資訊限於以書面標示「機密」之文件，口頭揭露需於七（7）日內書面確認。",
        "redline": "雙務保密且甲方機密範圍無限制定義，導致甲方日常溝通均可能觸發違約——不可接受。",
    },
    "RISK_JURISDICTION_CHANGED": {
        "tier1": "要求維持以台灣臺北地方法院為第一審管轄法院。",
        "tier1_clause": "因本合約所生之爭議，以台灣臺北地方法院為第一審管轄法院。",
        "tier2": "若乙方堅持，提出以中華民國仲裁協會仲裁替代訴訟，仲裁地點設於台北市。",
        "tier2_clause": "因本合約所生之爭議，雙方同意提付中華民國仲裁協會仲裁，仲裁地點為台北市，仲裁語言為中文。",
        "redline": "管轄地設於境外，或要求以外國法律適用——不可接受。",
    },
    "RISK_DATA_CONTROL_LOST": {
        "tier1": "要求合約終止後 7 天內完成資料刪除並提供書面證明，且不得留存任何衍生資料。",
        "tier1_clause": "本合約終止後七（7）日內，乙方應將甲方提供之所有資料及衍生資料予以刪除或返還，並提供書面刪除證明。",
        "tier2": "接受返還期限延至 14 天，但要求乙方提供稽核權，甲方可驗證資料處置狀況。",
        "tier2_clause": "本合約終止後十四（14）日內完成資料返還或刪除；甲方有權於完成後三十（30）日內要求乙方配合稽核確認。",
        "redline": "無資料返還/刪除義務，或乙方可將甲方資料用於商業目的——不可接受。",
    },
}

NEGOTIATE_SYSTEM_PROMPT = """你是企業法務顧問，專精台灣 SLA、採購、NDA 合約談判。

針對合約問題條款，輸出三層談判立場（JSON 格式）：
- tier1：企業最理想的首選立場說明（一到兩句）
- tier1_clause：對應 tier1 的替換條款建議文字（可直接貼入合約）
- tier2：可接受的退讓方案說明（一到兩句），不需每次請示法務
- tier2_clause：對應 tier2 的替換條款建議文字
- redline：絕對底線說明，低於此線需升級法務（一到兩句）

輸出格式：
{
  "tier1": "...",
  "tier1_clause": "...",
  "tier2": "...",
  "tier2_clause": "...",
  "redline": "..."
}

規則：
- 使用繁體中文
- tier1_clause / tier2_clause 需為可直接使用的條款文字
- 不要重複說明，聚焦在具體立場與條款
"""


def _build_negotiate_prompt(
    risk_code: str,
    risk_name: str,
    old_text: str,
    new_text: str,
    change_type: str,
    playbook_hint: dict,
) -> str:
    change_map = {"inserted": "乙方新增", "deleted": "乙方刪除", "modified": "乙方修改"}
    attr = change_map.get(change_type, "變更")
    return f"""風險類型：{risk_name}（{risk_code}）
變更性質：{attr}

原始條款：
{old_text or '（無，為新增條款）'}

修改後條款：
{new_text or '（已刪除）'}

參考立場提示（可作為基礎，結合實際條款文字調整）：
首選立場：{playbook_hint.get('tier1', '')}
可退讓：{playbook_hint.get('tier2', '')}
底線：{playbook_hint.get('redline', '')}

請根據實際條款文字，輸出精準的三層協商立場與替換條款文字。"""


def generate_playbook(
    clause_id: str,
    risk_code: str,
    risk_name: str,
    old_text: str = "",
    new_text: str = "",
    change_type: str = "",
) -> dict:
    """Return three-tier playbook. LLM-enhanced if API key available, else static."""
    static = STATIC_PLAYBOOK.get(risk_code, {
        "tier1": f"要求恢復原條款，維持甲方原有保護。",
        "tier1_clause": "（請法務人員依合約原文補充替換條款）",
        "tier2": "若乙方堅持，要求以書面附件補充同等效力條款。",
        "tier2_clause": "雙方同意以附件補充規範相關義務，附件具同等法律效力。",
        "redline": "完全取消甲方保護且無任何補充機制——不可接受，須升級法務。",
    })

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    claude_key = os.environ.get("ANTHROPIC_API_KEY", "")

    if gemini_key:
        result = _llm_gemini(gemini_key, risk_code, risk_name, old_text, new_text, change_type, static)
    elif claude_key:
        result = _llm_claude(claude_key, risk_code, risk_name, old_text, new_text, change_type, static)
    else:
        result = static

    return result


def _llm_gemini(api_key, risk_code, risk_name, old_text, new_text, change_type, static) -> dict:
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        prompt = _build_negotiate_prompt(risk_code, risk_name, old_text, new_text, change_type, static)
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=NEGOTIATE_SYSTEM_PROMPT),
        )
        text = response.text.strip()
        start, end = text.find("{"), text.rfind("}") + 1
        return json.loads(text[start:end])
    except Exception as e:
        logging.warning(f"Negotiate Gemini error: {e} — using static playbook")
        return static


def _llm_claude(api_key, risk_code, risk_name, old_text, new_text, change_type, static) -> dict:
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        prompt = _build_negotiate_prompt(risk_code, risk_name, old_text, new_text, change_type, static)
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=NEGOTIATE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        text = msg.content[0].text.strip()
        start, end = text.find("{"), text.rfind("}") + 1
        return json.loads(text[start:end])
    except Exception as e:
        logging.warning(f"Negotiate Claude error: {e} — using static playbook")
        return static
