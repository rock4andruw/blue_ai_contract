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

    Used both to help a human spot recurring Case-C patterns worth turning
    into a permanent Rule Engine rule, AND to scope Case A/B/C matching in
    cross_check_risks() to "same clause AND same risk dimension" instead of
    "same clause" alone (see RISK_CODE_CATEGORY).

    KNOWN LIMITATION: single-keyword-bucket classification can't cleanly
    separate overlapping concepts — e.g. "違約金上限降低" (a penalty CAP)
    contains the keyword "違約金" and gets bucketed as "違約金/罰則" even
    though the engine categorizes the same clause as "賠償上限". Worst case
    this produces a redundant Case C flag alongside the engine's flag,
    not a dropped one — acceptable given the project's 寧可多判不漏判
    principle (a harmless duplicate beats silently losing a finding, which
    is the failure mode this whole matching scheme exists to prevent).
    Not tuning further: reordering CATEGORY_KEYWORDS to fix this shifts the
    same ambiguity onto other real, validated cases (see verifier tests).
    """
    for category, kws in CATEGORY_KEYWORDS.items():
        if any(kw in trigger_reason for kw in kws):
            return category
    return "新類別候選（未歸類）"


# Maps each Rule Engine risk_code to the same category taxonomy used by
# categorize_candidate(), so an Agent finding on the same clause_id but a
# different risk dimension isn't mistaken for "already covered by the
# engine" and silently dropped (see cross_check_risks()).
RISK_CODE_CATEGORY = {
    "RISK_SLA_DEGRADE": "SLA/可用率",
    "RISK_RESPONSE_TIME_EXTENDED": "回應/修復時間",
    "RISK_PENALTY_WEAKENED": "違約金/罰則",
    "RISK_LIABILITY_CAP_CHANGED": "賠償上限",
    "RISK_LIABILITY_INCREASE": "賠償上限",
    "RISK_PROTECTION_REMOVED": "保護條款",
    "RISK_PROTECTION_ADDED": "保護條款",
    "RISK_CONFIDENTIALITY_WEAKENED": "保密義務",
    "RISK_DATA_CONTROL_LOST": "資料控制權",
    "RISK_TERMINATION_CHANGED": "終止/解約",
    "RISK_FORCE_MAJEURE_EXPANDED": "不可抗力",
    "RISK_JURISDICTION_CHANGED": "管轄法院",
    "RISK_IP_OWNERSHIP_CHANGED": "智慧財產權",
    "RISK_LIABILITY_DIRECTION_REVERSED": "賠償上限",
    "RISK_CONFIDENTIALITY_SCOPE_CHANGED": "保密義務",
}


def engine_flag_category(risk_code: str) -> str:
    """Category for a Rule Engine flag, on the same taxonomy as categorize_candidate()."""
    return RISK_CODE_CATEGORY.get(risk_code, "新類別候選（未歸類）")


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

def _load_skill_section(skill_path: str, section_header: str) -> str:
    """Extract a named ## section from a skill file. Returns "" on any failure.

    Plain text file read — no Claude Code dependency at runtime. Same
    pattern as mas_service.py's _load_skill_section (kept as a separate
    copy rather than a shared import to avoid cross-module coupling for a
    ~10-line utility).
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
_SKILL_VERIFICATION_AGENT = _load_skill_section(
    str(_SKILLS_DIR / "contract-risk-analysis.md"),
    "Verification Agent 知識庫（語意補漏審查員）",
)

VERIFICATION_SYSTEM_PROMPT = """你是資深甲方法律顧問與合約審查專家。

任務：
審查以下合約條款的修改內容，找出對甲方（買方）不利的實質風險變更。

{skill}

必須輸出 JSON 陣列（不含任何說明文字，直接輸出 JSON）：
[
  {{
    "clause_id": "條文編號或標題",
    "risk_level": "high | medium | low",
    "trigger_reason": "修改差異與不利影響說明（需說明數值換算結果）",
    "evidence_text": "修改版中的關鍵句子"
  }}
]

若無任何風險，輸出空陣列：[]
""".format(skill=_SKILL_VERIFICATION_AGENT or "評估重點：對甲方（買方）不利的實質風險變更，忽略純字詞修正與對甲方有利的修改。（知識庫未載入，依訓練知識判斷）")


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

    Case A: both flagged the same clause AND same risk dimension → keep engine flag (already confirmed)
    Case B: engine only → keep engine flag
    Case C: agent-only risk dimension (new clause, OR same clause but a
        *different* risk than the one the engine already flagged there)
        → append as RISK_AGENT_AUDITED (補漏)

    Matching key is (clause_id, risk category) rather than clause_id alone.
    A single clause can carry more than one distinct risk (e.g. a penalty
    clause where the engine catches the cap change but only the Agent
    catches the rate's Chinese-fraction format) — keying on clause_id alone
    would make the engine's flag "cover" a completely different risk the
    Agent found in the same clause, silently dropping it depending on
    incidental LLM phrasing of clause_id (non-deterministic).
    """
    final_flags = list(engine_flags)
    engine_keys = {
        (normalize_clause_id(str(f.clause_id)), engine_flag_category(f.risk_code))
        for f in engine_flags
    }
    seen_agent_keys = set()

    for af in agent_flags:
        normalized = normalize_clause_id(af.get("clause_id", ""))
        if not normalized:
            continue
        category = categorize_candidate(af.get("trigger_reason", ""))
        key = (normalized, category)
        if key in engine_keys:
            continue  # Case A or B: same clause, same risk dimension
        if key in seen_agent_keys:
            log.info(f"VerificationAgent skipped duplicate Case C flag: {af['clause_id']} ({category})")
            continue  # duplicate agent finding for the same clause + dimension
        seen_agent_keys.add(key)

        # Case C: agent-only finding (new clause, or new risk dimension on a
        # clause the engine already flagged for a different reason)
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
        log.info(f"VerificationAgent added Case C flag: {af['clause_id']} ({category}, {flag.risk_level})")

    return final_flags
