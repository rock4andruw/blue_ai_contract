# 下一步規劃（2026-06-25 更新）

**競賽截止**：2026 年 8 月初
**評審組成**：AI / AP / Infra 部長 + 黑客松評審
**當前狀態**：Phase 1 完整完成，Phase 1.5 MAS 規劃確定、實作中

---

## 已完成（Phase 1 + 本週）

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
- [x] **Alignment 誤判修正**：相似度後處理（difflib ≥ 75%）合併重新編號條款，修正「原版本無此條款」誤判
- [x] **Hero strip 可收合**：三個指標可點擊展開詳細說明（方法論、驗證數字、架構設計）

---

## Phase 1.5 MAS 設計規格

### 架構

Rule Engine 完全不動。MAS 只加在 LLM 解釋層：

```text
[高風險 flag] → async parallel → Agent A + Agent B → Judge → mas_status + mas_confidence
```

### Agent Persona（防同質化關鍵）

**Agent A（嚴格）**：極度保守的買方法律顧問，任務是找出所有隱藏惡意條款與最壞情況（Worst-case scenario）

**Agent B（平衡）**：促成交易的商務法務調解人，評估條款是否符合業界慣例（Market standard）及拒絕是否導致交易破裂

### Judge 決策矩陣

| Rule Engine | Agent A | Agent B | mas_status | 最終風險級別 |
| --- | --- | --- | --- | --- |
| High | High | High | `confirmed` | High |
| High | High | Medium/Low | `pending` | High（待確認） |
| High | Medium | High | `pending` | High（待確認） |
| High | Medium | Medium | `confirmed`（降級） | Medium |
| High | Low | Low | `confirmed`（降級） | Low |

### Graceful Degradation

- `asyncio.wait_for` 每個 Agent 超時設定 4 秒
- 任一 Agent 失敗 → 退級為 `mas_status: "single_agent"`，`mas_confidence: "low"`
- 兩個都失敗 → fallback 到 template，API 不中斷

### UI 呈現

- `confirmed` → `✓ 雙重驗證` 標籤
- `pending` → `⚠ 待確認` 標籤 + **展示兩者觀點衝突點**（例：「嚴格審查員認為...；平衡審查員指出...」）
- `single_agent` → 不顯示 MAS 標籤，靜默降級

### 驗收條件

- gold set 跑完後 Pending 率目標：**10%–20%**
- 低於 5% → Agent persona 差異不夠，需調整 prompt
- 超過 30% → 使用者負擔過重，需放寬 Judge 邏輯

---

## 近期工作（7 月）

### 週次 1（6/30 前）

- [ ] MAS 實作：Agent A/B prompt persona + asyncio.gather + Judge 邏輯
- [ ] Graceful Degradation：`asyncio.wait_for` 超時退級 + fallback 機制
- [ ] API 新增 `mas_status` / `mas_confidence` 欄位
- [ ] UI：雙重驗證標籤 + Pending 衝突點展示
- [ ] 拿到法務合約（NDA + IT 採購，甲方版 vs 乙方修改版）

### 週次 2（7/7 前）

- [ ] gold set 跑分：驗證 Pending 率在 10–20% 區間
- [ ] DOCX 格式支援改善（考慮 markitdown / mammoth）
- [ ] 邊界測試：空條款、超長條款、純表格條款

### 週次 3（7/14 前）

- [ ] 法務合約測試（NDA + IT 採購，甲方版 vs 乙方修改版）
- [ ] Demo 壓測（確保當天服務穩定不崩）
- [ ] 針對三位部長各自的 30 秒切入點準備說詞

### 週次 4-5（7/21-7/28）

- [ ] 簡報製作（含 MAS 架構圖）
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
