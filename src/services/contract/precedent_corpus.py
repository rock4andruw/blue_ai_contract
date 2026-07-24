"""Precedent case corpus for Layer 3 negotiation grounding.

Synthetic "we've reviewed a case like this before" entries, hand-written to
mirror the exact risk patterns in our own v2-v6 Demo examples (not generic
filler — every entry should sound like it could plausibly have produced one
of our real demo findings). Not real client history: no confidential data,
safe to embed and ship with the demo.

Retrieval is genuine vector similarity (Gemini embedding-2, 3072-dim,
cosine similarity) over this fixed corpus — not keyword matching. No
PostgreSQL: embeddings are precomputed once by build_corpus_embeddings()
and cached to precedent_corpus.json, read back synchronously at runtime
(same "offline-build, synchronous-read" pattern as legal_citations_cache.json).
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

CORPUS_PATH = Path(__file__).resolve().parent / "precedent_corpus.json"
EMBED_MODEL = "gemini-embedding-2"

# Each entry mirrors a risk pattern actually present in sla_contract/v2-v6.
PRECEDENT_CASES: List[Dict[str, str]] = [
    {
        "risk_code": "RISK_SLA_DEGRADE",
        "case_summary": "過去審查一份 IT 委外服務合約，乙方將核心系統月可用率標準從 99.9% 下修為 99.5%，並縮小可用率計算基礎中排除項目的認定範圍，使乙方更容易達標。",
        "negotiation_stance": "要求維持原可用率標準；若接受下修，需搭配提高服務折讓比例作為補償，並明確定義排除項目範圍。",
    },
    {
        "risk_code": "RISK_RESPONSE_TIME_EXTENDED",
        "case_summary": "過去審查一份系統維護合約，乙方將 P1 重大故障的初始回應時間從 30 分鐘延長為 2 小時，修復時間從 4 小時延長為 8 小時，大幅放寬事件處理時效。",
        "negotiation_stance": "要求維持原回應與修復時間標準；若接受放寬，需加計超時罰則或建立升級機制。",
    },
    {
        "risk_code": "RISK_LIABILITY_CAP_CHANGED",
        "case_summary": "過去審查一份採購合約，乙方將損害賠償計算基礎從「最近 12 個月已支付服務費」調整為「當月服務費」，大幅限縮甲方可求償的上限金額。",
        "negotiation_stance": "要求恢復原賠償計算基礎；若無法恢復，需明列不適用上限的例外情形（如重大過失、資安事件、故意行為）。",
    },
    {
        "risk_code": "RISK_LIABILITY_CAP_CHANGED",
        "case_summary": "過去審查一份軟體維護合約，乙方將遲延懲罰性違約金的計算比例，從阿拉伯數字（如 0.3%）改用中文分數寫法（如千分之一）表示，數值上實質降低但條文表面不易察覺差異；同時逾期違約金累計上限也一併調降。",
        "negotiation_stance": "要求以阿拉伯數字明確標示費率，並比對換算後的實際數值是否與原條款一致；上限金額若同時調降，需分別針對費率與上限兩項單獨談判。",
    },
    {
        "risk_code": "RISK_PROTECTION_REMOVED",
        "case_summary": "過去審查一份服務合約，乙方刪除了原本保障甲方資料保護、服務配合義務的保護性條款，且未提供任何替代條款彌補甲方喪失的保障。",
        "negotiation_stance": "要求恢復被刪除的條款；若乙方堅持刪除，需以其他條款補償對應的保護效果，或將刪除內容改列為附件維持約束力。",
    },
    {
        "risk_code": "RISK_FORCE_MAJEURE_EXPANDED",
        "case_summary": "過去審查一份合約，乙方將不可抗力事由的範圍擴大，納入第三方平台故障、供應商延誤等原屬乙方應合理管控的情形，使乙方更容易主張免責。",
        "negotiation_stance": "要求限縮不可抗力定義，排除乙方可合理預見或控制的情形；不可抗力期間過長時，賦予甲方終止合約的權利。",
    },
    {
        "risk_code": "RISK_JURISDICTION_CHANGED",
        "case_summary": "過去審查一份合約，乙方將第一審管轄法院從甲方所在地地方法院，改為乙方所在地地方法院，增加甲方未來爭訟的時間與交通成本。",
        "negotiation_stance": "要求維持甲方所在地為第一審管轄法院；若乙方堅持，可提出改採線上仲裁或雙方協議地點作為替代方案。",
    },
    {
        "risk_code": "RISK_DATA_CONTROL_LOST",
        "case_summary": "過去審查一份合約，乙方新增條款使其可自行決定履約過程中取得資料的保留或刪除時機，降低甲方對自身資料處置流向的控制權。",
        "negotiation_stance": "要求合約終止後乙方須於限期內完成資料刪除並提供書面證明；履約期間亦應賦予甲方資料稽核權。",
    },
    {
        "risk_code": "RISK_TERMINATION_CHANGED",
        "case_summary": "過去審查一份合約，乙方將終止通知期從 30 天大幅縮短，並新增乙方得無條件單方解約的權利，甲方在合約穩定性上的保障因此減弱。",
        "negotiation_stance": "要求終止通知期恢復至少 30 天；單方解約權若無法移除，需明確列出可終止事由，避免乙方可任意解約。",
    },
    {
        "risk_code": "RISK_CONFIDENTIALITY_WEAKENED",
        "case_summary": "過去審查一份合約，乙方將保密義務存續期間從合約終止後 5 年縮短為 2 年，降低甲方機密資訊的長期保護程度。",
        "negotiation_stance": "要求保密期間維持至少 3-5 年；針對客戶名單、定價等特定敏感資料，可另行約定更長的保密期間。",
    },
]


_CORPUS_CACHE: Optional[List[Dict[str, Any]]] = None


def _load_corpus() -> List[Dict[str, Any]]:
    global _CORPUS_CACHE
    if _CORPUS_CACHE is None:
        if not CORPUS_PATH.exists():
            _CORPUS_CACHE = []
        else:
            with open(CORPUS_PATH, encoding="utf-8") as f:
                _CORPUS_CACHE = json.load(f)
    return _CORPUS_CACHE


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def find_similar_precedent(
    query_text: str,
    gemini_key: Optional[str] = None,
    min_similarity: float = 0.5,
) -> Optional[Dict[str, str]]:
    """Embed query_text and return the most similar cached precedent case.

    Genuine vector similarity against the offline-built corpus (see
    build_corpus_embeddings) -- not keyword matching. Returns None if the
    corpus is empty, the embedding call fails, or nothing clears
    min_similarity (a weak/irrelevant "top match" is worse than no match).
    """
    corpus = _load_corpus()
    if not corpus:
        return None

    api_key = gemini_key or os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return None

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        resp = client.models.embed_content(model=EMBED_MODEL, contents=query_text)
        query_vec = resp.embeddings[0].values
    except Exception:
        return None

    best, best_score = None, min_similarity
    for entry in corpus:
        score = _cosine_similarity(query_vec, entry["embedding"])
        if score > best_score:
            best, best_score = entry, score

    if best is None:
        return None
    return {
        "risk_code": best["risk_code"],
        "case_summary": best["case_summary"],
        "negotiation_stance": best["negotiation_stance"],
        "similarity": round(best_score, 3),
    }


def build_corpus_embeddings(gemini_key: Optional[str] = None) -> None:
    """One-off offline build step: embed every case_summary and cache to disk.

    Not called at request time -- run manually when the corpus changes.
    Mirrors how legal_citations_cache.json was built: query once, cache
    the real result, read synchronously at runtime.
    """
    from google import genai

    api_key = gemini_key or os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY required to build the corpus")

    client = genai.Client(api_key=api_key)
    entries = []
    for case in PRECEDENT_CASES:
        resp = client.models.embed_content(model=EMBED_MODEL, contents=case["case_summary"])
        entries.append({
            **case,
            "embedding": resp.embeddings[0].values,
        })
        print(f"embedded: {case['risk_code']} — {case['case_summary'][:30]}...")

    with open(CORPUS_PATH, "w", encoding="utf-8") as f:
        # No indent: each entry's embedding is a 3072-float array, and
        # pretty-printing puts one float per line -- indent=2 bloats this
        # file to ~600KB for no benefit (nobody reads embeddings visually).
        json.dump(entries, f, ensure_ascii=False)
    print(f"\nSaved {len(entries)} entries to {CORPUS_PATH}")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    build_corpus_embeddings()
