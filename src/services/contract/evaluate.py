"""Evaluation script: compare risk_engine output against gold_annotations.csv.

Metrics:
  - High-risk recall: fraction of gold 'high' flags that engine detected
  - Overall accuracy: fraction of gold flags where risk_level matches engine output
"""

import csv
import sys
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parents[4]))

from src.services.contract.parser import ContractParser
from src.services.contract.alignment import ContractAligner
from src.services.contract.diff_engine import DiffEngine
from src.services.contract.risk_engine import RiskEngine


GOLD_CSV = "samples/gold_annotations.csv"
CONTRACT_V1 = "sla_contract/SLA-like Base Contract v1.md"
CONTRACT_FILES = {
    "v2": "sla_contract/sla_v2_degrade.md",
    "v3": "sla_contract/sla_v3_liability.md",
    "v4": "sla_contract/sla_v4_remove_protection.md",
    "v5": "sla_contract/sla_v5_termination.md",
}


def load_gold(path: str) -> Dict[Tuple[str, str], dict]:
    """Load gold annotations keyed by (version, clause_id)."""
    gold = {}
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            key = (row["version"].strip(), row["clause_id"].strip())
            gold[key] = row
    return gold


def run_engine(version: str, path: str, v1_clauses):
    a = ContractAligner()
    d = DiffEngine()
    r = RiskEngine()
    p = ContractParser()
    vx = p.parse_file(path)
    blocks = a.align_documents(v1_clauses, vx.clauses)
    diffs = d.compute_diffs(v1_clauses, vx.clauses, blocks)
    flags = r.analyze(diffs)
    # key: clause_id -> RiskFlag
    return {f.clause_id: f for f in flags}


def evaluate():
    p = ContractParser()
    v1 = p.parse_file(CONTRACT_V1)
    gold = load_gold(GOLD_CSV)

    # Filter gold to only adverse flags (ignore 'favorable' and 'none')
    adverse_gold = {k: v for k, v in gold.items()
                    if v["risk_direction"] == "adverse" and v["risk_level"] != "none"}

    total = len(adverse_gold)
    high_total = sum(1 for v in adverse_gold.values() if v["risk_level"] == "high")

    detected = 0
    high_detected = 0
    misses: List[dict] = []
    hits: List[dict] = []

    for (ver, clause_id), gold_row in adverse_gold.items():
        engine_flags = run_engine(ver, CONTRACT_FILES[ver], v1.clauses)
        flag = engine_flags.get(clause_id)

        gold_level = gold_row["risk_level"]
        is_high = gold_level == "high"

        if flag is not None:
            detected += 1
            if is_high:
                high_detected += 1
            hits.append({
                "version": ver, "clause_id": clause_id,
                "gold_level": gold_level, "engine_level": flag.risk_level,
                "engine_code": flag.risk_code,
            })
        else:
            if is_high:
                misses.append({"version": ver, "clause_id": clause_id,
                               "gold_level": gold_level, "note": gold_row["note"]})

    high_recall = high_detected / high_total if high_total else 0
    overall_accuracy = detected / total if total else 0

    print("=" * 60)
    print("Risk Engine Evaluation")
    print("=" * 60)
    print(f"Gold adverse clauses : {total}")
    print(f"Gold high-risk       : {high_total}")
    print(f"Engine detected      : {detected}")
    print()
    print(f"High-risk recall     : {high_detected}/{high_total} = {high_recall:.0%}")
    print(f"Overall detection    : {detected}/{total} = {overall_accuracy:.0%}")
    print()

    if misses:
        print("MISSED high-risk clauses:")
        for m in misses:
            print(f"  [{m['version']}] {m['clause_id']} — {m['note'][:70]}")
    else:
        print("✅ No high-risk misses")

    print()
    print("Detected hits:")
    for h in hits:
        match = "✅" if h["gold_level"] == h["engine_level"] else "⚠️ "
        print(f"  {match} [{h['version']}] {h['clause_id']:8} gold={h['gold_level']:6} engine={h['engine_level']:6} {h['engine_code']}")

    return high_recall, overall_accuracy


if __name__ == "__main__":
    high_recall, overall = evaluate()
    print()
    print(f"Target: high_recall=100%  overall>80%")
    print(f"Result: high_recall={high_recall:.0%}  overall={overall:.0%}")
    if high_recall < 1.0:
        print("❌ High-risk recall below 100% — add rules to cover misses")
    elif overall < 0.8:
        print("⚠️  Overall accuracy below 80% — tune existing rules")
    else:
        print("✅ Targets met")
