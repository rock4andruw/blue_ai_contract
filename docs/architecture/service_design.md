# 服務設計：Risk Rule Engine vs LLM Summary Service

**狀態**: 定案，已實作  
**最後更新**: 2026-06-17

---

## 核心原則

> **Risk Rule Engine 做判斷與標記，LLM Summary Service 做解釋與表達。**

LLM 不回答「這算不算高風險？」，只回答「這個高風險代表什麼？怎麼談？」

---

## 資料流

```text
Diff Engine
  ↓
Risk Rule Engine
  → risk_flag / risk_level / trigger_reason / evidence_clause_ids
  ↓
Retrieval Service (tool_rag)
  → 相似條款 / 公司標準條款 / 參考依據
  ↓
LLM Summary & Negotiation Service
  → 白話摘要 / 重點變更（3-5 個）/ 協商對策
```

LLM 收到的永遠是**已結構化資料**，不是原始全量文件。

---

## Risk Rule Engine

**輸入**：Diff Engine 的條款差異結果  
**輸出**：風險旗標列表

### Rule Engine 負責三件事

1. **辨識條款變化模式**

   | 模式 | 說明 |
   | --- | --- |
   | SLA 百分比下降 | 如 99.9% → 99.5% |
   | 回應/修復時間拉長 | 如 4h → 8h |
   | 新增賠償上限 | 原本無上限 → 新增月費 20% 上限 |
   | 刪除保護條款 | 如移除技術支援、教育訓練、備份義務 |
   | 終止條件變差 | 通知期縮短、終止事由擴大 |
   | 費用結構調整 | 基本費或超量費上漲 |

2. **套用風險規則**，輸出結構化旗標

3. **輸出可驗證的初步結果**，例如：
   - `RISK_SLA_DEGRADE / High / SLA 由 99.9% 降為 99.5%`
   - `RISK_LIABILITY_CAP_ADDED / High / 新增賠償上限為月費 20%`

### Rule Engine 輸出格式

```json
{
  "clause_id": "new_5_2",
  "risk_code": "RISK_SLA_DEGRADE",
  "risk_level": "high",
  "trigger_reason": "SLA 可用性由 99.9% 降為 99.5%",
  "evidence": {
    "old_text": "系統可用性不低於 99.9%",
    "new_text": "系統可用性不低於 99.5%"
  }
}
```

### 優點

- 可寫單元測試，結果可重現
- 新增風險類型只需補規則，不動 prompt
- 比賽簡報時展示規則清單，技術性加分

---

## LLM Summary & Negotiation Service

**輸入**：Risk Rule Engine 輸出 + Retrieval Service 補充資料  
**輸出**：給人看的報告內容

### LLM 負責三件事

1. **白話摘要**：把 risk_code + trigger_reason 翻成非技術語言
2. **重點收斂**：20 個差異、8 個風險 → 濃縮成 3-5 個最重要變更
3. **協商對策生成**：根據 risk_code + 條款內容 + 公司標準條款，給出 2-3 個可行方案

### LLM 輸入格式

```json
{
  "risk_code": "RISK_SLA_DEGRADE",
  "risk_level": "high",
  "trigger_reason": "SLA 可用性由 99.9% 降為 99.5%",
  "old_text": "系統可用性不低於 99.9%",
  "new_text": "系統可用性不低於 99.5%",
  "reference_clause": "（公司標準 SLA 條款內容）"
}
```

### LLM 輸出格式

```json
{
  "plain_summary": "新版合約將服務可用性從 99.9% 降至 99.5%，允許停機時間增加 3.5 倍。",
  "business_impact": "每月允許停機從 43 分鐘增至 3.6 小時，對業務關鍵系統影響顯著。",
  "negotiation_options": [
    "要求維持 99.9%，以業務關鍵性為談判依據",
    "接受 99.5%，但要求賠償比例從 5% 提高至 15%",
    "要求加入即時監控與停機通知義務作為補償"
  ]
}
```

---

## 模組對照表

| 模組 | 檔案 | 輸入 | 輸出 | 狀態 |
| --- | --- | --- | --- | --- |
| 共用型別 | `schemas.py` | — | Clause / DiffItem / RiskFlag / ReportSection | ✅ |
| Parser | `parser.py` | MD / PDF / DOCX | `List[ClauseElement]` | ✅ |
| Alignment | `alignment.py` | 舊版 + 新版條款 | `List[MatchBlock]` | ✅ |
| Diff Engine | `diff_engine.py` | MatchBlock 列表 | `List[DiffItem]` | ✅ |
| Risk Rule Engine | `risk_engine.py` | `List[DiffItem]` | `List[RiskFlag]` | ✅ 11 條規則 |
| LLM Summary Service | `llm_service.py` | `List[RiskFlag]` | `List[ReportSection]` | ✅ API + fallback |
| Report Generator | `report_generator.py` | 所有模組輸出 | `ComparisonReport` + Markdown | ✅ |
| Orchestrator | `orchestrator.py` | 兩個檔案路徑 | Markdown 報告字串 | ✅ |
| 評估腳本 | `evaluate.py` | gold_annotations.csv | 準確率數字 | ✅ high-recall 100% |
| Retrieval Service | `retrieval.py` | 風險條款 | 相似條款、標準條款 | ⬜ Phase 1.5 |
| FastAPI endpoint | `api/contracts.py` | HTTP 上傳 | JSON 報告 | ⬜ 待開發 |
| Demo UI | `frontend/` | — | HTML 頁面 | ⬜ 待開發 |

---

## 為什麼這樣切

**技術性**：有獨立規則層，不是純 prompt 工具，可展示規則清單與測試結果

**穩定性**：LLM 只處理已結構化輸入，幻覺機率大幅降低

**可維護性**：新增風險類型 → 只補規則；優化說明語氣 → 只改 prompt；互不影響

**可解釋性**：每個風險旗標都有 trigger_reason + evidence，法務可追溯判斷依據
