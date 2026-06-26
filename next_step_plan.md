# 下一步規劃（2026-06-26 更新）

**競賽截止**：2026 年 8 月初
**評審組成**：AI / AP / Infra 部長 + 黑客松評審
**當前狀態**：Phase 1.5 完成（MAS 雙重驗證 + 三層協商對策 + NDA 測試合約）

---

## 已完成（Phase 1 + Phase 1.5）

- [x] 核心管道：Parser → Alignment（LCS + Needleman-Wunsch）→ Diff → Risk Rule Engine → LLM Summary → Report
- [x] FastAPI：`POST /api/v1/contracts/compare`、`GET /api/v1/contracts/compare/example/{id}`
- [x] Demo UI：Hero 指標條（可點擊展開說明）、4 段橫向 Loading 動畫、結果卡片
- [x] 風險歸因標籤（乙方新增／修改／刪除條款）
- [x] 原文對照（before/after 可展開對比）
- [x] 三層協商對策（`POST /api/v1/contracts/negotiate`，按需呼叫）
  - Static Playbook（13 種 SLA 風險類型）+ LLM 精煉
  - 🟢 首選立場 / 🟡 可接受妥協 / 🔴 絕對底線 + 替換條款文字
- [x] HTML 追蹤修改清理（Word 匯出的 `<del>/<ins>` 自動剝除）
- [x] Gemini 3.1 Flash Lite 為主要 LLM，Claude Sonnet 4.6 備援
- [x] **Alignment 誤判修正**：相似度後處理（difflib ≥ 75%）合併重新編號條款
- [x] **Hero strip 可收合**：三個指標可點擊展開詳細說明
- [x] **風險規則擴充**：11 → 15 條規則（新增 IP 歸屬、責任反轉、保密範圍、保密單雙向）
- [x] **MAS Phase 1.5**：
  - Agent A（嚴格）+ Agent B（平衡）ThreadPoolExecutor 平行執行
  - Judge 矩陣：gap=1→confirmed（嚴格優先），gap=2→pending（真正分歧）
  - 移除 Prompt 錨定（盲評，不預告 Rule Engine 答案）
  - Skill 知識庫從 `.md` 動態載入注入 System Prompt
  - UI：`✓ 雙重驗證` / `⚠ 待確認` 標籤 + pending 展示兩個 Agent 觀點
- [x] **NDA 測試合約**：`nda_contract/` v1（甲方版）+ v2（乙方修改版），pipeline 驗證通過
- [x] **法務申請信**：已寄出（申請 NDA + IT 採購合約真實樣本）
- [x] **6 篇 MAS 文獻**：Echo Chamber / Sycophancy / Anchoring Bias（`相關文獻與來源/`）

---

## 近期工作（7 月）

### 週次 1（6/30 前）

- [ ] Demo 流程預排（確認 v3 pending + v4 confirmed 的敘事切入點）
- [ ] NDA 規則補強：偵測保密期縮短（5年→2年）、單向→雙向轉變（現在只抓到 3/7 風險）
- [ ] 法務合約收件後上傳測試（若有）

### 週次 2（7/7 前）

- [ ] DOCX 格式支援改善（考慮 markitdown / mammoth）
- [ ] 邊界測試：空條款、超長條款、純表格條款
- [ ] 壓測：確保當天服務穩定不崩

### 週次 3（7/14 前）

- [ ] 簡報製作（含 MAS 架構圖）
- [ ] 針對三位部長各自的 30 秒切入點準備說詞
- [ ] Demo 流程預演

### 週次 4-5（7/21-7/28）

- [ ] 最終 Bug 修復
- [ ] README 補齊所有啟動說明
- [ ] 備用簡報與 Demo 備援方案

---

## 不做的（競賽前）

- ❌ RAG / 歷史合約庫（Phase 2）
- ❌ 異質模型 MAS（Phase 2：Gemini + Claude 異質設計）
- ❌ GraphRAG 跨條款依賴（Phase 2-3）
- ❌ M365 Teams / SharePoint 整合（Phase 3）
- ❌ Taiwan Law MCP（Phase 2）
- ❌ 資料庫（競賽不需要持久化）

---

## 對每位評審的主攻點

| 評審 | 核心訴求 | 關鍵話術 |
| --- | --- | --- |
| **AI 部長** | 雙軌架構 + MAS + 100% recall | 「規則引擎保證不漏判，LLM 只解釋——MAS 讓兩個 Agent 用不同視角互相驗證」 |
| **AP 部長** | 數字 + Demo 流暢度 | 「26 秒初審，100% 高風險召回，三層對策直接給替換條款文字」 |
| **Infra 部長** | 資安 + 架構 | 「合約資料不離開企業內網，API key 環境變數，stateless FastAPI」 |
| **黑客松評審** | Demo 衝擊力 | v4（6 高風險全 confirmed）→ v3（pending 展示 AI 誠實說不確定）→ 三層對策 |

---

## MAS 現況補充

**Phase 1.5 誠實定位**：對立 Persona 驅動的雙視角評估，非嚴格獨立驗證。相同模型 + 不同 Persona，Echo Chamber 限制存在，但 Persona 差異仍能提供有意義的觀點分歧（文獻支撐：論文 1-3）。

**實測 pending 率**：

- v4（明確高風險）：0%（兩個 Agent 均同意）
- v3（責任條款有爭議）：67%（11.1 / 11.3 真正分歧，符合預期）

**Phase 2 改善方向**：Gemini Agent A + Claude Agent B 異質模型，解決 Echo Chamber。
