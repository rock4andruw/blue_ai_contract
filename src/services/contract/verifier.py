"""Verification Agent: LLM semantic sweep to catch Rule Engine gaps (Layer 2)."""

import json
import re
import difflib
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .schemas import RiskFlag, DiffItem

log = logging.getLogger(__name__)

RISK_CODE_AGENT = "RISK_AGENT_AUDITED"

# ------------------------------------------------------------------
# Candidate rule log: Case C findings are NOT auto-promoted into Rule
# Engine rules (an LLM-authored regex reviewed by nobody could silently
# misfire on every future contract). Instead we accumulate them here so
# a human can spot recurring patterns and hand-write a permanent rule
# once the same category keeps showing up across contracts.
# ------------------------------------------------------------------

CANDIDATE_LOG_PATH = Path(__file__).resolve().parents[3] / "candidate_rules.jsonl"

CATEGORY_KEYWORDS = {
    "SLA/可用率": ["可用率", "SLA", "uptime"],
    "回應/修復時間": ["回應時間", "修復時間", "處理時限"],
    "違約金/罰則": ["違約金", "罰款", "折讓", "懲罰性"],
    "賠償上限": ["賠償上限", "責任上限", "求償金額", "損害賠償總額"],
    "保護條款": ["保護條款", "義務", "保證"],
    "保密義務": ["保密", "機密"],
    "智慧財產權": ["智慧財產權", "著作權", "專利", "所有權", "使用權"],
    "終止/解約": ["終止", "解約"],
    "不可抗力": ["不可抗力", "免責"],
    "管轄法院": ["管轄", "法院"],
    "資料控制權": ["資料", "個資", "備份"],
    "付款/財務條件": ["付款", "分期", "月結", "利息"],
    "驗收條件": ["驗收"],
}


def categorize_candidate(trigger_reason: str) -> str:
    """Guess which existing risk category a Case C finding resembles.

    Not used for judgment — only to help a human spot recurring patterns
    worth turning into a permanent Rule Engine rule.
    """
    for category, kws in CATEGORY_KEYWORDS.items():
        if any(kw in trigger_reason for kw in kws):
            return category
    return "新類別候選（未歸類）"


def log_candidate_rule(af: Dict[str, Any], contract_pair: str = "") -> None:
    """Append a Case C finding to the candidate-rule review log.

    This does NOT create a rule automatically. It only accumulates
    evidence so a human can later hand-write a Rule Engine rule once a
    pattern repeats across multiple contracts.
    """
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "contract_pair": contract_pair,
        "clause_id": af.get("clause_id", ""),
        "risk_level": normalize_risk_level(af.get("risk_level")),
        "trigger_reason": af.get("trigger_reason", ""),
        "evidence_text": af.get("evidence_text", ""),
        "category_guess": categorize_candidate(af.get("trigger_reason", "")),
    }
    try:
        with open(CANDIDATE_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as e:
        log.warning(f"candidate rule log write failed: {e}")

VERIFICATION_SYSTEM_PROMPT = """你是資深甲方法律顧問與合約審查專家。

任務：
審查以下合約條款的修改內容，找出對甲方（買方）不利的實質風險變更。

評估重點：
- SLA 可用率降低
- 回應或修復時間拉長
- 賠償上限縮水
- 保護條款被刪除
- 保密期縮短
- 智財權移轉至乙方
- 責任方向反轉
- 不可抗力範圍擴大
- 管轄地改變
- 資料控制權喪失
- 違約金費率或金額降低（特別注意：中文數字寫法如「千分之一」= 0.1%，「千分之三」= 0.3%，需與阿拉伯數字寫法作語意比較）

忽略：純字詞修正、排版調整、對甲方有利的修改。

必須輸出 JSON 陣列（不含任何說明文字，直接輸出 JSON）：
[
  {
    "clause_id": "條文編號或標題",
    "risk_level": "high | medium | low",
    "trigger_reason": "修改差異與不利影響說明（需說明數值換算結果）",
    "evidence_text": "修改版中的關鍵句子"
  }
]

若無任何風險，輸出空陣列：[]
"""


def _build_diff_prompt(diffs: List[DiffItem]) -> str:
    items = [d for d in diffs if d.change_type != "unchanged"]
    if not items:
        return ""
    parts = []
    for d in items:
        old = d.old_text or "（無，為新增條款）"
        new = d.new_text or "（已刪除）"
        parts.append(f"【條款 {d.clause_id}】\n原文：{old}\n修改後：{new}")
    return "\n\n".join(parts)


class VerificationAgent:
    """Layer 2: LLM semantic sweep that runs after the Rule Engine.

    Catches what Regex misses: non-standard numeric formats (千分之一 vs 0.3%),
    new risk types, and clauses the parser split incorrectly.
    """

    def audit_diffs(self, diffs: List[DiffItem]) -> List[Dict[str, Any]]:
        """Send diff content to LLM, return list of agent-identified risks."""
        gemini_key = os.environ.get("GEMINI_API_KEY", "")
        claude_key = os.environ.get("ANTHROPIC_API_KEY", "")

        prompt = _build_diff_prompt(diffs)
        if not prompt:
            return []

        if gemini_key:
            return self._call_gemini(prompt, gemini_key)
        elif claude_key:
            return self._call_claude(prompt, claude_key)
        else:
            log.warning("VerificationAgent: no API key, skipping LLM sweep")
            return []

    def _call_gemini(self, prompt: str, api_key: str) -> List[Dict[str, Any]]:
        try:
            from google import genai
            from google.genai import types
        except ImportError:
            log.warning("google-genai not installed, VerificationAgent skipped")
            return []
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(system_instruction=VERIFICATION_SYSTEM_PROMPT),
            )
            return _parse_agent_response(response.text)
        except Exception as e:
            log.warning(f"VerificationAgent Gemini error: {e}")
            return []

    def _call_claude(self, prompt: str, api_key: str) -> List[Dict[str, Any]]:
        try:
            import anthropic
        except ImportError:
            log.warning("anthropic not installed, VerificationAgent skipped")
            return []
        try:
            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=1024,
                system=VERIFICATION_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            return _parse_agent_response(message.content[0].text)
        except Exception as e:
            log.warning(f"VerificationAgent Claude error: {e}")
            return []


def _parse_agent_response(text: str) -> List[Dict[str, Any]]:
    text = text.strip()
    start = text.find("[")
    end = text.rfind("]") + 1
    if start == -1 or end == 0:
        return []
    try:
        result = json.loads(text[start:end])
        return [r for r in result if isinstance(r, dict) and "clause_id" in r]
    except json.JSONDecodeError as e:
        log.warning(f"VerificationAgent JSON parse error: {e} — raw: {text[:200]}")
        return []


VALID_RISK_LEVELS = {"high", "medium", "low"}


def normalize_risk_level(level: Any) -> str:
    """Clamp an LLM-returned risk_level to a valid value; default to 'medium'.

    LLM output isn't schema-enforced, so it occasionally returns Chinese
    ("高") or other variants instead of the requested "high|medium|low".
    An unrecognized value must not silently drop the flag from summary
    counts, so we default it to a safe middle value instead of passing
    it through unchecked.
    """
    if isinstance(level, str) and level.strip().lower() in VALID_RISK_LEVELS:
        return level.strip().lower()
    zh_map = {"高": "high", "中": "medium", "低": "low"}
    if isinstance(level, str) and level.strip() in zh_map:
        return zh_map[level.strip()]
    return "medium"


def normalize_clause_id(cid: str) -> str:
    cid = re.sub(r'^第|條$|款$', '', cid.strip())
    return cid.replace(' ', '').lower()


def find_matching_diff(agent_clause_id: str, diffs: List[DiffItem]) -> Optional[DiffItem]:
    normalized = normalize_clause_id(agent_clause_id)
    for d in diffs:
        if normalize_clause_id(str(d.clause_id)) == normalized:
            return d
    ids = [str(d.clause_id) for d in diffs]
    matches = difflib.get_close_matches(agent_clause_id, ids, n=1, cutoff=0.8)
    return next((d for d in diffs if str(d.clause_id) == matches[0]), None) if matches else None


def cross_check_risks(
    engine_flags: List[RiskFlag],
    agent_flags: List[Dict[str, Any]],
    diffs: List[DiffItem],
    contract_pair: str = "",
) -> List[RiskFlag]:
    """Merge Rule Engine and Verification Agent outputs.

    Case A: both flagged → keep engine flag (already confirmed)
    Case B: engine only → keep engine flag
    Case C: agent only → append as RISK_AGENT_AUDITED (補漏)
    """
    final_flags = list(engine_flags)
    engine_ids = {normalize_clause_id(str(f.clause_id)) for f in engine_flags}
    seen_agent_ids = set()

    for af in agent_flags:
        normalized = normalize_clause_id(af.get("clause_id", ""))
        if not normalized or normalized in engine_ids:
            continue  # Case A or B
        if normalized in seen_agent_ids:
            log.info(f"VerificationAgent skipped duplicate Case C flag: {af['clause_id']}")
            continue  # duplicate agent finding for the same clause
        seen_agent_ids.add(normalized)

        # Case C: agent-only finding
        matched = find_matching_diff(af["clause_id"], diffs)
        flag = RiskFlag(
            clause_id=af["clause_id"],
            risk_code=RISK_CODE_AGENT,
            risk_level=normalize_risk_level(af.get("risk_level")),
            risk_direction="adverse",
            trigger_reason=f"【⚠ Agent 補漏】{af.get('trigger_reason', '')}",
            old_text=matched.old_text if matched else "",
            new_text=matched.new_text if matched else af.get("evidence_text", ""),
            change_type=matched.change_type if matched else "modified",
        )
        final_flags.append(flag)
        log_candidate_rule(af, contract_pair=contract_pair)
        log.info(f"VerificationAgent added Case C flag: {af['clause_id']} ({flag.risk_level})")

    return final_flags
