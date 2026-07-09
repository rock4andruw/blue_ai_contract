"""Exp1: pure-LLM baseline vs the hybrid (Rule Engine + Verification Agent) system.

Reuses the exact same modules/data evaluate.py already uses (ContractParser,
ContractAligner, DiffEngine, gold_annotations.csv) so this is an apples-to-apples
comparison against the already-published hybrid numbers (100% high-risk recall,
67% overall). Only difference: instead of RiskEngine.analyze(), each diff is
classified by a bare Gemini call with zero rules, zero taxonomy, zero reference
framework -- simulating "what if we'd just used a generic LLM classifier."

Detected-metric definition matches evaluate.py exactly: a gold-high clause counts
as "recalled" if the classifier flagged it as ANY non-none risk level (not
necessarily matching the exact severity) -- same semantics as evaluate.py's
`if flag is not None: ... if is_high: high_detected += 1`.
"""
import sys
import os
import json

sys.path.insert(0, "/Users/andruw/Documents/bule-ai-team")
os.chdir("/Users/andruw/Documents/bule-ai-team")

from dotenv import load_dotenv
load_dotenv(dotenv_path="/Users/andruw/Documents/bule-ai-team/.env")

from src.services.contract.parser import ContractParser
from src.services.contract.alignment import ContractAligner
from src.services.contract.diff_engine import DiffEngine
from src.services.contract.evaluate import load_gold, CONTRACT_V1, CONTRACT_FILES, GOLD_CSV

PURE_LLM_PROMPT = """你是合約風險審查員。請判斷以下合約條款修改的風險等級。

原始條款：
{old_text}

修改後條款：
{new_text}

只回傳一個詞：high、medium、low、或 none。不要有其他文字。"""


def run_align_diff(path, v1_clauses):
    a = ContractAligner()
    d = DiffEngine()
    p = ContractParser()
    vx = p.parse_file(path)
    blocks = a.align_documents(v1_clauses, vx.clauses)
    diffs = d.compute_diffs(v1_clauses, vx.clauses, blocks)
    return {item.clause_id: item for item in diffs}


def classify_pure_llm(old_text, new_text, gemini_key):
    from google import genai
    client = genai.Client(api_key=gemini_key)
    prompt = PURE_LLM_PROMPT.format(
        old_text=old_text or "（無，為新增條款）",
        new_text=new_text or "（已刪除）",
    )
    resp = client.models.generate_content(model="gemini-3.1-flash-lite", contents=prompt)
    text = resp.text.strip().lower()
    for level in ["high", "medium", "low", "none"]:
        if level in text:
            return level
    return "none"


def main():
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_key:
        print("ERROR: GEMINI_API_KEY not set")
        return

    p = ContractParser()
    v1 = p.parse_file(CONTRACT_V1)
    gold = load_gold(GOLD_CSV)
    adverse_gold = {
        k: v for k, v in gold.items()
        if v["risk_direction"] == "adverse" and v["risk_level"] != "none"
    }

    total = len(adverse_gold)
    high_total = sum(1 for v in adverse_gold.values() if v["risk_level"] == "high")

    pure_detected = 0
    pure_high_detected = 0
    results = []
    diff_cache = {}

    for (ver, clause_id), gold_row in adverse_gold.items():
        if ver not in diff_cache:
            diff_cache[ver] = run_align_diff(CONTRACT_FILES[ver], v1.clauses)
        diff = diff_cache[ver].get(clause_id)

        if diff is None:
            results.append({"ver": ver, "clause_id": clause_id, "gold": gold_row["risk_level"], "pure_llm": "NOT_ALIGNED"})
            continue

        pred = classify_pure_llm(diff.old_text, diff.new_text, gemini_key)
        is_high = gold_row["risk_level"] == "high"
        detected = pred != "none"

        if detected:
            pure_detected += 1
            if is_high:
                pure_high_detected += 1

        results.append({"ver": ver, "clause_id": clause_id, "gold": gold_row["risk_level"], "pure_llm": pred})

    print("=" * 60)
    print("Exp1: Pure-LLM Baseline (no rule engine, no verification agent)")
    print("=" * 60)
    print(f"Gold adverse clauses : {total}")
    print(f"Gold high-risk       : {high_total}")
    print(f"Pure-LLM detected    : {pure_detected}")
    print()
    print(f"High-risk recall     : {pure_high_detected}/{high_total} = {pure_high_detected/high_total:.0%}")
    print(f"Overall detection    : {pure_detected}/{total} = {pure_detected/total:.0%}")
    print()
    for r in results:
        match = "OK " if r["gold"] == r["pure_llm"] else "?? "
        print(f"{match}[{r['ver']}] {r['clause_id']:10} gold={r['gold']:6} pure_llm={r['pure_llm']}")

    out_path = "/private/tmp/claude-501/-Users-andruw-Documents-bule-ai-team/18f547bf-4da8-41cb-8cd7-594bd0f68116/scratchpad/exp1_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "total": total, "high_total": high_total,
            "pure_detected": pure_detected, "pure_high_detected": pure_high_detected,
            "results": results,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n結果已存: {out_path}")


if __name__ == "__main__":
    main()
