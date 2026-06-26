"""MAS (Multi-Agent System) Phase 1.5 — dual-agent cross-validation.

Agent A (strict)  : conservative buyer's counsel, worst-case bias
Agent B (balanced): commercial legal advisor, market-standard comparison

Both agents independently verify the Rule Engine's risk level for each
high-risk flag. A Judge decision matrix merges the two verdicts.
"""

import concurrent.futures
import json
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .schemas import RiskFlag, RISK_CODES


def _load_skill_section(skill_path: str, section_header: str) -> str:
    """Extract a named ## section from a skill file. Returns empty string on any failure."""
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

_SKILL_AGENT_A = _load_skill_section(
    str(_SKILLS_DIR / "contract-risk-analysis.md"),
    "MAS Agent A 知識庫（嚴格審查員）",
)
_SKILL_AGENT_B = _load_skill_section(
    str(_SKILLS_DIR / "negotiation-strategy.md"),
    "MAS Agent B 知識庫（平衡審查員）",
)


@dataclass
class AgentVerdict:
    agreed_level: str   # high / medium / low
    reasoning: str      # one-sentence explanation


AGENT_A_SYSTEM = """你是極度保守的甲方法律顧問，專門在合約談判中保護甲方利益。

你的任務：評估規則引擎標記的條款風險，從最壞情況出發判斷風險等級。
原則：寧可高估風險，不可低估——一旦遺漏高風險條款，公司可能承受重大損失。

{skill_a}

輸出格式（JSON，只輸出 JSON，不加其他說明）：
{{
  "agreed_level": "high 或 medium 或 low",
  "reasoning": "一句話說明你的判斷依據，聚焦最壞情況或潛在損失"
}}""".format(skill_a=_SKILL_AGENT_A or "（知識庫未載入，依訓練知識判斷）")

AGENT_B_SYSTEM = """你是促成交易的商務法務顧問，熟悉台灣 SaaS / IT 採購合約業界慣例。

你的任務：評估規則引擎標記的條款風險，與市場行情比較後判斷實際風險等級。
原則：若條款雖有偏差但符合業界常見做法，應如實反映為 medium 或 low，避免過度防守阻礙交易。

{skill_b}

輸出格式（JSON，只輸出 JSON，不加其他說明）：
{{
  "agreed_level": "high 或 medium 或 low",
  "reasoning": "一句話說明你的判斷依據，聚焦業界慣例比較或實際商業影響"
}}""".format(skill_b=_SKILL_AGENT_B or "（知識庫未載入，依訓練知識判斷）")


def _build_agent_prompt(flag: RiskFlag) -> str:
    risk_name = RISK_CODES.get(flag.risk_code, flag.risk_code)
    return f"""請評估以下合約條款變更，判斷對甲方（買方）的風險等級。

變更類型：{risk_name}
觸發原因：{flag.trigger_reason}

原始條款：
{flag.old_text or '（無，為新增條款）'}

修改後條款：
{flag.new_text or '（已刪除）'}

請根據條款實際內容，輸出你的風險等級判斷（JSON）。"""


def _parse_verdict(text: str, fallback_level: str) -> AgentVerdict:
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON found in response")
    data = json.loads(text[start:end])
    level = data.get("agreed_level", fallback_level).lower()
    if level not in ("high", "medium", "low"):
        level = fallback_level
    return AgentVerdict(
        agreed_level=level,
        reasoning=data.get("reasoning", ""),
    )


def _call_agent_gemini(flag: RiskFlag, system_prompt: str, api_key: str) -> AgentVerdict:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=_build_agent_prompt(flag),
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=200,
        ),
    )
    return _parse_verdict(response.text.strip(), flag.risk_level)


def _call_agent_claude(flag: RiskFlag, system_prompt: str, api_key: str) -> AgentVerdict:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        system=system_prompt,
        messages=[{"role": "user", "content": _build_agent_prompt(flag)}],
    )
    return _parse_verdict(msg.content[0].text.strip(), flag.risk_level)


def _call_agent(
    flag: RiskFlag,
    persona: str,
    gemini_key: str,
    claude_key: str,
) -> Optional[AgentVerdict]:
    system_prompt = AGENT_A_SYSTEM if persona == "strict" else AGENT_B_SYSTEM
    try:
        if gemini_key:
            return _call_agent_gemini(flag, system_prompt, gemini_key)
        elif claude_key:
            return _call_agent_claude(flag, system_prompt, claude_key)
        return None
    except Exception as e:
        logging.warning(f"MAS Agent {persona} error ({type(e).__name__}): {e}")
        return None


def _judge(
    rule_level: str,
    verdict_a: Optional[AgentVerdict],
    verdict_b: Optional[AgentVerdict],
) -> dict:
    """Apply Judge decision matrix and return MAS result dict."""
    # Both failed → silent fallback
    if verdict_a is None and verdict_b is None:
        return {
            "mas_status": "single_agent",
            "mas_confidence": "low",
            "final_risk_level": rule_level,
            "agent_a_view": "",
            "agent_b_view": "",
        }

    # One failed → single_agent with surviving verdict
    if verdict_a is None or verdict_b is None:
        surviving = verdict_a or verdict_b
        return {
            "mas_status": "single_agent",
            "mas_confidence": "low",
            "final_risk_level": rule_level,
            "agent_a_view": verdict_a.reasoning if verdict_a else "",
            "agent_b_view": verdict_b.reasoning if verdict_b else "",
        }

    level_a = verdict_a.agreed_level
    level_b = verdict_b.agreed_level
    _rank = {"high": 2, "medium": 1, "low": 0}

    # Both agree → confirmed, adopt their level
    if level_a == level_b:
        return {
            "mas_status": "confirmed",
            "mas_confidence": "high",
            "final_risk_level": level_a,
            "agent_a_view": verdict_a.reasoning,
            "agent_b_view": verdict_b.reasoning,
        }

    gap = abs(_rank.get(level_a, 1) - _rank.get(level_b, 1))

    # Gap of 1 level (high vs medium, or medium vs low) → strict wins, confirmed
    if gap == 1:
        final = level_a if _rank.get(level_a, 1) > _rank.get(level_b, 1) else level_b
        return {
            "mas_status": "confirmed",
            "mas_confidence": "medium",
            "final_risk_level": final,
            "agent_a_view": verdict_a.reasoning,
            "agent_b_view": verdict_b.reasoning,
        }

    # Gap of 2 levels (high vs low) → genuine disagreement, pending
    return {
        "mas_status": "pending",
        "mas_confidence": "low",
        "final_risk_level": rule_level,
        "agent_a_view": verdict_a.reasoning,
        "agent_b_view": verdict_b.reasoning,
    }


def run_mas(
    flag: RiskFlag,
    gemini_key: str = "",
    claude_key: str = "",
    timeout: int = 8,
) -> dict:
    """Run Agent A (strict) and Agent B (balanced) in parallel threads.

    Returns a dict with keys:
        mas_status       : "confirmed" | "pending" | "single_agent"
        mas_confidence   : "high" | "low"
        final_risk_level : "high" | "medium" | "low"
        agent_a_view     : reasoning from strict agent
        agent_b_view     : reasoning from balanced agent
    """
    if not gemini_key and not claude_key:
        return _judge(flag.risk_level, None, None)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_a = executor.submit(_call_agent, flag, "strict", gemini_key, claude_key)
        future_b = executor.submit(_call_agent, flag, "balanced", gemini_key, claude_key)

        try:
            verdict_a = future_a.result(timeout=timeout)
        except (concurrent.futures.TimeoutError, Exception) as e:
            logging.warning(f"MAS Agent A timeout/error: {e}")
            verdict_a = None

        try:
            verdict_b = future_b.result(timeout=timeout)
        except (concurrent.futures.TimeoutError, Exception) as e:
            logging.warning(f"MAS Agent B timeout/error: {e}")
            verdict_b = None

    return _judge(flag.risk_level, verdict_a, verdict_b)
