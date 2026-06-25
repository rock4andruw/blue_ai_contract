# 下一步規劃（2026-06-25 更新）

**競賽截止**：2026 年 8 月初  
**評審組成**：AI / AP / Infra 部長 + 黑客松評審  
**當前狀態**：Phase 1 完整完成，正在 Phase 1.5

---

## 已完成（Phase 1）

- [x] 核心管道：Parser → Alignment（LCS + Needleman-Wunsch）→ Diff → Risk Rule Engine → LLM Summary → Report
- [x] FastAPI：`POST /api/v1/contracts/compare`、`GET /api/v1/contracts/compare/example/{id}`
- [x] Demo UI：Hero 指標條、4 段橫向 Loading 動畫、結果卡片
- [x] 風險歸因標籤（乙方新增／修改／刪除條款）
- [x] 原文對照（before/after 可展開對比）
- [x] 三層協商對策（`POST /api/v1/contracts/negotiate`，按需呼叫）
  - Static Playbook（13 種 SLA 風險類型）+ LLM 精煉
  - 🟢 首選立場 / 🟡 可接受妥協 / 🔴 絕對底線 + 替換條款文字
- [x] HTML 追蹤修改清理（Word 匯出的 `<del>/<ins>` 自動剝除）
- [x] Gemini 3.1 Flash Lite 為主要 LLM，Claude Sonnet 4.6 備援

---

## 近期工作（7 月）

### 週次 1（6/30 前）

- [ ] Phase 1.5 MAS：雙 Agent 交叉驗證高風險條款
  - Agent A（嚴格判定）+ Agent B（寬鬆判定）→ 取交集為確定風險，差異為 Pending
  - 目標：AI 部長的技術亮點，強化「防幻覺」敘事
  - 實作方式：async parallel 呼叫，同一 API key

### 週次 2（7/7 前）

- [ ] DOCX 格式支援改善（考慮 markitdown / mammoth）
- [ ] 邊界測試：空條款、超長條款、純表格條款

### 週次 3（7/14 前）

- [ ] Demo 壓測（確保當天服務穩定不崩）
- [ ] 針對三位部長各自的 30 秒切入點準備說詞

### 週次 4-5（7/21-7/28）

- [ ] 簡報製作（含架構圖更新）
- [ ] Demo 流程預演 + 修 Bug
- [ ] README 補齊啟動說明

---

## 不做的（競賽前）

- ❌ RAG / 歷史合約庫（Phase 2）
- ❌ GraphRAG 跨條款依賴（Phase 2-3）
- ❌ M365 Teams / SharePoint 整合（Phase 3）
- ❌ Taiwan Law MCP（Phase 2）
- ❌ Normalizer Agent（風險高、收益低）
- ❌ 資料庫（競賽不需要持久化）

---

## 對每位評審的主攻點

| 評審 | 核心訴求 | 關鍵話術 |
| --- | --- | --- |
| **AI 部長** | 雙軌架構 + MAS + 100% recall | 「規則引擎保證不漏判，LLM 只解釋——MAS 讓兩個 Agent 互相驗證」 |
| **AP 部長** | 數字 + Demo 流暢度 | 「26 秒初審，100% 高風險召回，三層對策直接給替換條款文字」 |
| **Infra 部長** | 資安 + 架構 | 「合約資料不離開企業內網，API key 環境變數，stateless FastAPI」 |
| **黑客松評審** | Demo 衝擊力 | v4 範例：6 高風險 → 三層對策 → 替換文字，一次展示完整價值 |
