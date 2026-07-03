# Session 說明檔：2026-06-27 工作紀錄

> 讀完這份文件，新的 AI session 可以立刻接續工作，不需要重新說明背景。
> 系統完整說明請見 PROJECT_CONTEXT.md。

---

## 本次 Session 完成的工作

### 1. 工程審查回應
外部工程師提出四大架構疑問，已整理為正式回應：
- 文件：`docs/specs/engineering_review_response.md`
- 核心立場：效能瓶頸、表格解析、無狀態架構屬刻意取捨；Regex 語意彈性是真正待改善問題

### 2. 國際架構模組研究
研究四個進階模組，評估可借鑑部分：

| 模組 | 建議 |
| --- | --- |
| Legal Linter（生成條款反向驗證） | 可立即實作，改 `llm_service.py` 的 negotiate 函式 |
| AST 語意正規化（LLM 先解析→Rule Engine 再判定） | 近期可做，解決 Regex 脆弱性 |
| 條款異動熱度摘要 | Report Generator 加統計，半天可完成 |
| Nash Equilibrium Sandbox | 遠程研究方向，目前無 payoff 資料 |

### 3. Verification Agent 設計規格（重要）
整合兩個來源的設計，已完整記錄：
- 文件：`docs/specs/verification_agent_spec.md`
- 架構：Rule Engine（Layer 1）+ Verification Agent（Layer 2）平行跑，交叉核對 A/B/C 三類
- 關鍵修正：clause_id 正規化、Agent 讀 Diff 不讀全文、C 類旗標強制進 MAS 加強驗證
- **尚未實作**，是下一步重要工作

### 4. 文獻整合
- `相關文獻與來源/合約審查與管理文獻來源.md` 補入：
  - 第四節：6 篇 MAS 論文（含 arXiv 連結）
  - 第六節：研究缺口新增 MAS + Pending 機制兩列
  - 第七節：競品表加入 LawGeex/LegalOn 比較欄

### 5. 論文計畫與指導教授提案書
- `docs/planning/research_paper_plan.md`（v3.0，在職碩士畢業論文版）
- `docs/planning/advisor_proposal.md`（v2.0，給指導教授看）
- 主目標：在職碩士畢業論文；遠程目標：ICAIL Short Paper

---

## 重要架構決策（這次 session 確認的）

### LLM 與 Rule Engine 的正確定位

**現況**（串聯，非協作）：
```
Rule Engine（Regex 偵測）→ LLM（白話解釋 + 協商對策）
```
LLM 不參與偵測，不影響風險等級判定。

**100% 召回率的正確說法**：
> 「在預定義的 15 類風險類別中達到 100% 召回率」
> 不是「對所有合約風險保證 100% 召回」

**未來方向（Phase 2，未實作）**：
```
自然語言條款 → LLM 解析 → {value: 99.5, unit: "%"} → Rule Engine 比對
```
這個「LLM 語意解析 → Rule Engine 邏輯判定」的協作模式是解決 Regex 脆弱性的根本解法，列為論文未來研究方向。

---

## 核心架構現況（Phase 1.5 已完成）

```
合約 Diff
    ├──→ [L1] Rule Engine（15 條規則）→ 預定義類別內 100% 召回
    └──→ [L2] Verification Agent（LLM 補漏）→ 設計完成，尚未實作
              ↓
         交叉核對（A 雙軌確認 / B 規則觸發 / C 補漏警示）
              ↓
         MAS 盲評（Agent A 嚴格 ‖ Agent B 平衡）
         → 互不知答案（防 Sycophancy）
              ↓
         Judge 矩陣 → confirmed / pending
              ↓
         Report + FastAPI + Demo UI
```

---

## 論文核心貢獻（確認版本）

**C1 — 防禦性三層設計**
- 已知風險：Rule Engine 在 15 類範圍內 100% 召回（可驗證）
- 未知風險：Verification Agent（LLM）補漏
- 限制誠實說明：100% 召回有範圍限定；LLM 補漏有幻覺風險

**C2 — 盲評 MAS（法律領域首次實作驗證）**
- 文獻依據：When Truth Is Overridden (2025, arXiv:2508.02087)
- 實驗：盲評 vs 非盲評，量化 Sycophancy 率

**C3 — Pending 機制（AI 主動揭露不確定性）**
- 現有工具皆強制輸出確定答案
- 本系統在 MAS 分歧時標記 pending，讓人工介入

---

## 待完成工作（優先順序）

| 優先度 | 工作 | 文件 |
| --- | --- | --- |
| 🔴 高 | Verification Agent 實作（`verifier.py`） | `docs/specs/verification_agent_spec.md` |
| 🔴 高 | NDA 規則補強（保密期縮短、單向→雙向未偵測） | `next_step_plan.md` |
| 🔴 高 | Demo 流程彩排（v4 confirmed + v3 pending 敘事） | `next_step_plan.md` |
| 🟡 中 | Legal Linter（生成條款反向驗證迴圈） | 討論紀錄 |
| 🟡 中 | CUAD 資料集整理（論文用，80 筆目標） | `docs/planning/research_paper_plan.md` |
| 🟡 中 | 非盲評路徑加入 `mas_service.py`（Exp 2 實驗用） | 論文計畫 |

---

## 重要文件索引

| 文件 | 用途 |
| --- | --- |
| `PROJECT_CONTEXT.md` | 系統冷啟動，工程師看這份 |
| `docs/specs/verification_agent_spec.md` | Verification Agent 完整設計規格 |
| `docs/specs/engineering_review_response.md` | 外部工程師審查的正式回應 |
| `docs/planning/advisor_proposal.md` | 給指導教授的論文提案書 |
| `docs/planning/research_paper_plan.md` | 完整論文計畫（在職碩士版） |
| `相關文獻與來源/合約審查與管理文獻來源.md` | 完整文獻庫（含 MAS 6 篇） |
| `相關文獻與來源/MAS_literature_index.md` | MAS 論文詳細摘要 |
| `docs/週報與簡報_2026-06-26.md` | 本週白話週報（含 6/27 工作） |

---

## 競賽 Demo 數字（可直接引用）

| 指標 | 數字 |
| --- | --- |
| High-risk Recall | 100%（38 筆 gold set） |
| Overall Detection | 61%（保守設計） |
| 處理時間 | 26 秒（v4，10 頁 SLA） |
| MAS pending 率 v4 | 0%（明確高風險） |
| MAS pending 率 v3 | 67%（條款有爭議，符合預期） |

---

*Session 日期：2026-06-27 ｜ Blue-AI Team*
