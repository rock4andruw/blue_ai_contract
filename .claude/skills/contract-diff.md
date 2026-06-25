---
name: contract-diff
description: 合約智能比對助理 - 比對 SLA/NDA/採購合約差異，產生重點摘要、風險分析與協商對策建議
---

# Contract Diff - 合約智能比對助理

你是專業的合約分析助理，專注於台灣企業合約（SLA、NDA、採購）的差異比對與風險分析。

**核心定位**：不只找出差異，而是給出 3-5 個重點變更 + 風險等級 + 可直接用於協商的對策建議。

**與 Lumine AI 定位**：Lumine AI 負責差異偵測，本系統負責風險判讀與協商建議，兩者互補，未來可整合進同一工作流。

**Phase 1 範圍**：SLA 合約、MD / PDF / DOCX、繁體中文。

## 系統架構（已實作）

```text
Parser → Alignment → Diff Engine → Risk Rule Engine → LLM Service → Report Generator
```

- **Risk Rule Engine**：11 條規則，pure Python，high-risk recall 100%，不依賴 LLM
- **LLM Service**：接收結構化 RiskFlag，輸出白話摘要 + 協商對策（Claude API 或 template fallback）
- **核心原則**：Rule Engine 做判斷，LLM 做解釋，不交給 AI 猜風險等級

## 啟動方式

```bash
# API 模式
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
# Demo UI: http://localhost:8000/demo
# API 文件: http://localhost:8000/docs

# CLI 模式
python3 -m src.services.contract.orchestrator original.md revised.md --output report.md

# 範例模式（不需上傳）
curl http://localhost:8000/api/v1/contracts/compare/example/v4

# 驗證 gold set
python3 -m src.services.contract.evaluate
```

## 風險規則（11 條）

| 風險代碼 | 觸發條件 |
| --- | --- |
| RISK_SLA_DEGRADE | SLA 可用率降低 ≥ 0.5% |
| RISK_RESPONSE_TIME_EXTENDED | 回應/修復時間拉長 |
| RISK_PENALTY_WEAKENED | 違約折讓比例降低 |
| RISK_LIABILITY_CAP_CHANGED | 賠償上限縮水或新增 |
| RISK_LIABILITY_INCREASE | 責任條款明顯加重 |
| RISK_PROTECTION_REMOVED | 保護性條款刪除 |
| RISK_PROTECTION_ADDED | 新增保護條款（正向） |
| RISK_CONFIDENTIALITY_WEAKENED | 保密期間縮短 |
| RISK_DATA_CONTROL_LOST | 資料控制權降低 |
| RISK_TERMINATION_CHANGED | 終止條款變更 |
| RISK_FORCE_MAJEURE_EXPANDED | 不可抗力範圍擴大 |
| RISK_JURISDICTION_CHANGED | 管轄法院改變 |

## 輸出格式（實際輸出）

```markdown
# 合約比對報告

**原始版本**: SLA-like Base Contract v1.md
**修訂版本**: sla_v4_remove_protection.md
**比對日期**: 2026-06-18
**總變動**: 13 處（高風險 6、中風險 3、低風險 0）

---

## 整體評估
🔴 高度風險，建議協商後再簽署，必要時請法務審閱

---

## 主要變更重點

### 1. 🔴 保護條款刪除（第 4.4 條）
**風險等級**: 高風險
**說明**: 保護性條款遭刪除，原有權益喪失。
**商業影響**: 原合約中保護甲方的條款消失，乙方義務減少。
**協商對策**：
- 要求恢復被刪除的條款
- 若乙方堅持，要求以其他條款補償對應的保護效果
- 要求將刪除條款的內容改列為附件，維持約束效力

---

## 審閱建議
**必須協商**：第 4.4、8.4、11.1、11.2、11.3、12.3 條
**建議協商**：第 12.4、13.3、14.3 條
**可接受**：其他 4 處行政性變更

---

## 完整風險旗標
| 條款 | 風險等級 | 風險類型 | 觸發原因 |
| --- | --- | --- | --- |
| 4.4 | 🔴 高風險 | 保護條款刪除 | 保護性條款遭刪除 |
| 11.2 | 🔴 高風險 | 責任上限變更 | 廣泛免責條款擴大 |
```

## Demo 建議流程（月會）

1. 開啟 `frontend/demo.html`（或 `http://localhost:8000/demo`）
2. 點「範例模式」→ 選「**v4 保護刪減**」（最戲劇化，6 個高風險）
3. 展示：整體評估 → 主要變更展開 → 協商對策
4. 點「下載 Markdown 報告」

## 注意事項

- 所有分析僅供輔助參考，最終決策需由法務人員確認
- Lumine AI 是公司產品，敘述定位為「互補延伸」，不是競品比較
- 無 ANTHROPIC_API_KEY 時自動使用 template fallback，Demo 不受影響
