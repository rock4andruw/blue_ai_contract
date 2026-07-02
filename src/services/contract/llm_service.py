"""LLM Summary & Negotiation Service.

Receives structured risk_flags from RiskEngine and produces:
- Plain-language summary per flag
- 3-5 key change highlights
- 2-3 negotiation options per high-risk flag
"""

import json
import logging
import os
from pathlib import Path
from typing import List, Optional
from .schemas import RiskFlag, ReportSection, RISK_CODES
from .mas_service import run_mas
from .precedent_corpus import find_similar_precedent
from .verifier import categorize_candidate, RISK_CODE_CATEGORY

log = logging.getLogger(__name__)

_LEGAL_CACHE_PATH = os.path.join(os.path.dirname(__file__), "legal_citations_cache.json")
_legal_cache: Optional[dict] = None

# Reverse of verifier.RISK_CODE_CATEGORY: category label -> risk_codes that
# map to it. Lets a Case C flag (risk_code always "RISK_AGENT_AUDITED")
# still reach a cached citation by its actual risk category instead of its
# generic label — built once from the single source of truth in verifier.py
# rather than duplicating the category taxonomy here.
_CATEGORY_TO_RISK_CODES: dict = {}
for _code, _category in RISK_CODE_CATEGORY.items():
    _CATEGORY_TO_RISK_CODES.setdefault(_category, []).append(_code)


def _get_legal_citation(risk_code: str, trigger_reason: str = "") -> str:
    """Look up a real Civil Code article for risk_code from the offline
    cache built via mcp-taiwan-legal-db (see next_step_plan.md). Never
    calls the MCP server live — synchronous file read only, no network
    dependency in the request path. Returns "" if nothing cached for this
    risk_code (most categories have no clean statute match; that's fine).

    Rule Engine flags carry one of the 15 real risk_codes, matching the
    cache's keys directly. Verification Agent (Case C) flags all carry the
    generic risk_code "RISK_AGENT_AUDITED", which never has a cache entry —
    for those, categorize trigger_reason with the same taxonomy verifier.py
    uses for Case A/B/C matching, then look up any risk_code sharing that
    category. This is a deliberate fallback, not a guess: it reuses the
    exact classification already trusted elsewhere in the pipeline.
    """
    global _legal_cache
    if _legal_cache is None:
        try:
            with open(_LEGAL_CACHE_PATH, encoding="utf-8") as f:
                _legal_cache = json.load(f)
        except (OSError, json.JSONDecodeError):
            _legal_cache = {}

    entries = _legal_cache.get(risk_code) or []
    if not entries and trigger_reason:
        category = categorize_candidate(trigger_reason)
        for candidate_code in _CATEGORY_TO_RISK_CODES.get(category, []):
            if _legal_cache.get(candidate_code):
                entries = _legal_cache[candidate_code]
                break

    if not entries:
        return ""
    e = entries[0]
    return f"{e['law_name']}第{e['article_no']}條：{e['content']}"


def _load_skill_section(skill_path: str, section_header: str) -> str:
    """Extract a named ## section from a skill file. Returns "" on any failure.

    Same plain-text-file pattern as mas_service.py / verifier.py. Kept as a
    separate copy per module rather than a shared import — consistent with
    the existing precedent, avoids cross-module coupling for a ~10-line
    utility. (Worth extracting into a shared helper once there's a 4th
    caller and the duplication is undeniable; not now.)
    """
    try:
        content = Path(skill_path).read_text(encoding="utf-8")
        start = content.find(f"## {section_header}")
        if start == -1:
            return ""
        next_section = content.find("\n## ", start + 1)
        return content[start:next_section if next_section != -1 else len(content)].strip()
    except Exception:
        return ""


_SKILLS_DIR = Path(__file__).resolve().parents[3] / ".claude" / "skills"
_SKILL_NEGOTIATION_FRAMEWORK = _load_skill_section(
    str(_SKILLS_DIR / "negotiation-strategy.md"),
    "各風險類型的協商框架",
)

SYSTEM_PROMPT = """你是專業的合約審查助理，專注於台灣企業 SLA / NDA / 採購合約的風險分析。

你的任務是把已由規則引擎標記的風險條款，翻譯成：
1. 白話說明（非法律工程語言）
2. 商業影響（對公司運營的實際影響）
3. 協商對策（2-3 個可直接用於談判的具體方案）

{skill}

輸出格式為 JSON，欄位：
{{
  "plain_summary": "一句話白話說明",
  "business_impact": "商業影響說明",
  "negotiation_options": ["對策 A", "對策 B", "對策 C"],
  "legal_basis": "若下方提供了「檢索到的法條」或「相似先例」才填寫，否則留空字串"
}}

注意：
- 使用繁體中文
- 協商對策要具體，不要模糊建議
- 不要重複 trigger_reason 的用詞，要用更口語的方式說明
- 上方協商框架若有涵蓋此風險類型，優先參考其「最佳/折衷/底線」結構，但需依實際條款文字調整措辭，不可照抄

若使用者輸入包含「檢索到的法條」或「相似先例」，額外遵守：
- legal_basis 只能引用「檢索到的法條」欄位裡提供的原文，絕對不可自行引用、推測或編造任何法條號碼或條文——沒有提供就把 legal_basis 留空字串，不得虛構
- 若有相似先例，協商對策可參考其處理邏輯，但需依本案情境調整用詞，不可照抄
- 若法條與本風險直接相關，negotiation_options 中至少一項應引用該法條作為談判依據
""".format(skill=_SKILL_NEGOTIATION_FRAMEWORK or "（協商框架知識庫未載入，依訓練知識判斷協商對策）")


def _build_user_prompt(
    flag: RiskFlag,
    reference_clause: str = "",
    legal_citation: str = "",
    precedent_case: str = "",
) -> str:
    risk_name = RISK_CODES.get(flag.risk_code, flag.risk_code)
    ref_section = f"\n參考標準條款：\n{reference_clause}" if reference_clause else ""
    legal_section = f"\n檢索到的法條：\n{legal_citation}" if legal_citation else ""
    precedent_section = f"\n相似先例：\n{precedent_case}" if precedent_case else ""
    return f"""風險類型：{risk_name}
風險等級：{flag.risk_level}
觸發原因：{flag.trigger_reason}

原始條款：
{flag.old_text or '（無，為新增條款）'}

修改後條款：
{flag.new_text or '（已刪除）'}
{ref_section}{legal_section}{precedent_section}

請產出 JSON 格式的分析結果。"""


def analyze_flag(flag: RiskFlag, reference_clause: str = "", api_key: Optional[str] = None) -> ReportSection:
    """Analyze a single RiskFlag. Priority: Gemini > Claude > template fallback."""
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    claude_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")

    # Layer 4 grounding: synchronous cache lookup (legal citation) + a single
    # embedding call (precedent similarity) — neither blocks on a live MCP
    # subprocess or PostgreSQL. Best-effort: missing/failed lookups just
    # mean an ungrounded (but still valid) negotiation suggestion, same as
    # before Layer 4 existed.
    legal_citation = _get_legal_citation(flag.risk_code, flag.trigger_reason)
    precedent = None
    if gemini_key:
        try:
            precedent = find_similar_precedent(flag.trigger_reason, gemini_key=gemini_key)
        except Exception as e:
            log.warning(f"precedent retrieval failed: {e}")
    precedent_text = precedent["case_summary"] + "\n過去協商結果：" + precedent["negotiation_stance"] if precedent else ""
    precedent_display = (
        f"{precedent['case_summary']}\n過去協商結果：{precedent['negotiation_stance']}（相似度 {precedent['similarity']:.0%}）"
        if precedent else ""
    )

    if gemini_key:
        section = _analyze_with_gemini(flag, reference_clause, gemini_key, legal_citation, precedent_text)
    elif claude_key:
        section = _analyze_with_claude(flag, reference_clause, claude_key, legal_citation, precedent_text)
    else:
        section = _analyze_with_template(flag)

    # Attach the raw retrieved sources regardless of which branch produced the
    # section, so the UI can show "what Layer 4 actually found" independent
    # of how the LLM chose to word legal_basis (or whether it wrote one at all).
    section.legal_citation_raw = legal_citation
    section.precedent_raw = precedent_display
    return section


def _analyze_with_gemini(
    flag: RiskFlag, reference_clause: str, api_key: str,
    legal_citation: str = "", precedent_text: str = "",
) -> ReportSection:
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise ImportError("google-genai not installed: pip install google-genai")

    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=_build_user_prompt(flag, reference_clause, legal_citation, precedent_text),
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        )
        text = response.text.strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        data = json.loads(text[start:end])
    except Exception as e:
        # Fallback to template on quota / network errors
        log.warning(f"Gemini API error ({type(e).__name__}): {e} — falling back to template")
        return _analyze_with_template(flag)

    return ReportSection(
        rank=0,
        clause_id=flag.clause_id,
        risk_level=flag.risk_level,
        risk_code=flag.risk_code,
        plain_summary=data.get("plain_summary", ""),
        business_impact=data.get("business_impact", ""),
        negotiation_options=data.get("negotiation_options", []),
        legal_basis=data.get("legal_basis", "") or "",
    )


def _analyze_with_claude(
    flag: RiskFlag, reference_clause: str, api_key: str,
    legal_citation: str = "", precedent_text: str = "",
) -> ReportSection:
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic not installed: pip install anthropic")

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _build_user_prompt(flag, reference_clause, legal_citation, precedent_text)}],
    )

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
        legal_basis=data.get("legal_basis", "") or "",
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
        "RISK_IP_OWNERSHIP_CHANGED": {
            "plain_summary": f"智慧財產權歸屬由甲方改為乙方（{flag.trigger_reason}），原有 IP 控制權喪失。",
            "business_impact": "合約執行期間開發的成果、文件、程式碼等智慧財產權將歸屬乙方，公司未來使用或授權他人使用的空間大幅縮減。",
            "negotiation_options": [
                "要求恢復原條款：所有執行本合約所產生的智財權歸甲方所有",
                "若乙方堅持，要求明確列出例外範圍（乙方原有技術不受影響），其餘仍歸甲方",
                "要求甲方取得永久無償使用授權及再授權第三人之權利",
            ],
        },
        "RISK_LIABILITY_DIRECTION_REVERSED": {
            "plain_summary": f"違約賠償責任方向反轉（{flag.trigger_reason}），原本乙方須賠甲方，現改為甲方須賠乙方。",
            "business_impact": "合約中的懲罰性違約金與賠償義務改由甲方承擔，若發生爭議，公司（甲方）反而須支付鉅額賠償（200 萬元以上）。",
            "negotiation_options": [
                "要求恢復原條款：違約賠償責任由乙方單向承擔",
                "若接受雙向責任，要求明確列出甲方可能違約的情境，限縮甲方承擔範圍",
                "要求將懲罰性違約金上限降低，或改為實際損害賠償，避免固定高額罰款",
            ],
        },
        "RISK_CONFIDENTIALITY_SCOPE_CHANGED": {
            "plain_summary": f"保密義務範圍改變（{flag.trigger_reason}），由單方保密改為雙方互保。",
            "business_impact": "保密方向改變，雙方均負有保密義務，乙方可能以此主張甲方揭露其機密資訊時亦需承擔保密責任，增加甲方合規負擔。",
            "negotiation_options": [
                "確認雙務保密對公司是否有利（若公司也有機密需保護，雙務版反而更好）",
                "若不接受雙務，要求恢復單務版：僅乙方對甲方負保密義務",
                "若接受雙務，要求明確定義甲方機密資訊的範圍，避免模糊條款擴大責任",
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
    max_medium: int = 3,
    return_mode: bool = False,
):
    """Generate ReportSections: all high-risk + top max_medium medium-risk flags.

    Args:
        max_medium: maximum number of medium-risk items to include (default 3).
        return_mode: if True, returns (sections, mode_str) instead of just sections.
                     mode_str is "claude_api", "gemini_api", or "template_fallback".
    """
    level_order = {"high": 0, "medium": 1, "low": 2, "none": 3}
    adverse_flags = [f for f in flags if f.risk_direction == "adverse"]
    high_flags   = [f for f in adverse_flags if f.risk_level == "high"]
    medium_flags = [f for f in adverse_flags if f.risk_level == "medium"][:max_medium]
    top_flags = high_flags + medium_flags

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    claude_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
    key = gemini_key or claude_key
    if gemini_key:
        mode = "gemini_api"
    elif claude_key:
        mode = "claude_api"
    else:
        mode = "template_fallback"

    sections = []
    for rank, flag in enumerate(top_flags, start=1):
        section = analyze_flag(flag, api_key=key or None)
        section.rank = rank

        # MAS: cross-validate high-risk flags only (cost control)
        if flag.risk_level == "high" and key:
            mas = run_mas(flag, gemini_key=gemini_key, claude_key=claude_key)
            section.mas_status = mas["mas_status"]
            section.mas_confidence = mas["mas_confidence"]
            section.mas_agent_a_view = mas["agent_a_view"]
            section.mas_agent_b_view = mas["agent_b_view"]
            # Apply Judge downgrade if both agents agree on lower level
            if mas["final_risk_level"] != flag.risk_level:
                section.risk_level = mas["final_risk_level"]

        sections.append(section)

    if return_mode:
        return sections, mode
    return sections
