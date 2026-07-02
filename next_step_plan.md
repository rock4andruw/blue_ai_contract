# 下一步規劃（2026-07-02 更新）

**競賽截止**：2026 年 8 月初
**評審組成**：AI / AP / Infra 部長 + 黑客松評審
**當前狀態**：Phase 1.5 完成 + Verification Agent（Layer 2）已實作並用真實公司合約驗證

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
- [x] **法務合約收件並完成上傳測試（2026-07-01）**：拿到 3 組真實公司合約（NDA / 軟體採購 / 軟體維護，PIC 版 vs 乙方修改版），完整跑過 pipeline
- [x] **Verification Agent 實作（`verifier.py`）**：接入 orchestrator.py Step 4b，Layer 1 規則引擎 + Layer 2 LLM 語意補漏交叉核對（Case A/B/C），並新增候選規則紀錄 `candidate_rules.jsonl`（Case C 補漏累積分類，供未來人工升級為正式規則，不自動生成規則）
- [x] **Diff Engine 涵蓋率修復**：發現並修復純新增/刪除條款因缺條號被靜默丟棄的漏洞（採購合約原本 138 段完全消失，現已全數進入 diffs）
- [x] **Risk Engine 數字/格式修復**：中文分數（千分之一/百分之/萬分之）、全形／半形 % 符號、費率與上限百分比互相干擾、回應/到場/修復三時限互相干擾（含修復過程中自己引入又抓到的假警報）

---

## 近期工作（7 月）

### 立即待辦（2026-07-02 新增）

- [x] **修復重大缺口：API 沒有接 Verification Agent**：`src/api/contracts.py` 的 `_build_response()` 原本自己兜 Parser→Alignment→Diff→RiskEngine→LLM，完全沒呼叫 `verifier.py`——代表 Demo UI（`/demo`，含上傳模式與範例模式）原本看不到今天做的核心功能，只有終端機直接跑 `orchestrator.compare()` 才有。已修復：`contracts.py` 接上 `VerificationAgent`/`cross_check_risks`，`schemas_api.py` 的 `RiskFlagItem` 新增 `source` 欄位，`frontend/demo.html` 完整風險旗標表格加「來源」欄顯示 ✓ 規則引擎／⚠ Agent 補漏。用 Playwright 實際開瀏覽器跑過 v4 範例，畫面正確顯示（3 項 Agent 補漏 + 9 項規則引擎，來源標籤清楚區分），無 console 錯誤。**這幾個檔案尚未 commit。**
- [ ] **Commit 所有尚未進版的改動**：`PROJECT_PLAN.md`（CLM 定位、Layer 4 路線圖、簡報收斂原則）、`docs/architecture/系統架構_mermaid.md`（Verification Agent 節點、pgvector 接線修正）、`src/api/contracts.py`、`src/api/schemas_api.py`、`frontend/demo.html`（以上為 API/UI 接上 Verification Agent 的修復）
- [ ] **寄出法務回信**：草稿已完成（祐銓以顧問角色參與、AI 法務方向對應 Layer 4），待使用者確認後手動寄送
- [ ] **決定是否修 Verification Agent Case A/B/C 比對邏輯**：目前只比對 clause_id，同一條款的第二個風險維度會被誤判成「已審查過」而丟棄。評估後不算難修（約 30-60 分鐘，改成比對 `(clause_id, 風險類別)`），但屬於「決定要不要花時間」而非「做不做得到」的問題，尚待使用者拍板

### 週次 1（6/30 前，延續中）

- [ ] Demo 流程預排（確認真實合約案例的敘事切入點：千分之一/0.3%、138 段涵蓋率修復、50%→30% 上限）
- [ ] NDA 保密期縮短規則（5年→2年）尚未用真實合約驗證——手上這份 NDA 沒有保密期變更，只驗證了單向→雙向偵測正常

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
- ❌ **Layer 4：pgvector 語意檢索 + Taiwan Law MCP 法條查詢**（2026-07-01 確認：只做口頭路線圖，不現場 demo。定位是接在協商建議生成之前，補上「建議沒有法律依據、LLM 憑空發揮」這個今天發現的缺口——pgvector 存 CUAD/內部案例做相似案例檢索，MCP 查民法真實條文。不用 CUAD 或假資料湊 demo，真實公司合約資料也不能整批進資料庫，兩者都會讓現場說服力下降，故僅作簡報路線圖，不建置）
- ❌ 資料庫（競賽不需要持久化）

---

## 對每位評審的主攻點

| 評審 | 核心訴求 | 關鍵話術 |
| --- | --- | --- |
| **AI 部長** | 雙軌架構 + MAS + Verification Agent | 「規則引擎保證預定義類別 100% 召回，但『千分之一』這種中文分數寫法 Regex 看不懂——Verification Agent 用 LLM 語意補漏，真實合約測出來規則引擎抓 1 項、Agent 多補 6-7 項」 |
| **AP 部長** | 數字 + 真實案例 | 「用真實公司合約測試：付款方式整段改寫、136 段條款曾經因為沒有條號被系統直接漏看，我們自己抓到並修好」 |
| **Infra 部長** | 資安 + 架構 | 「合約資料不離開企業內網，API key 環境變數，stateless FastAPI」 |
| **黑客松評審** | 誠實與自我修正的敘事 | 「系統會誠實標示『規則引擎 vs Agent 補漏』來源、也發現自己漏檢的地方——這次連我們自己新加的規則都一度誤判，當場抓到修掉，這是一個會自我發現弱點的系統，不是號稱零瑕疵」 |

---

## MAS 現況補充

**Phase 1.5 誠實定位**：對立 Persona 驅動的雙視角評估，非嚴格獨立驗證。相同模型 + 不同 Persona，Echo Chamber 限制存在，但 Persona 差異仍能提供有意義的觀點分歧（文獻支撐：論文 1-3）。

**實測 pending 率**：

- v4（明確高風險）：0%（兩個 Agent 均同意）
- v3（責任條款有爭議）：67%（11.1 / 11.3 真正分歧，符合預期）

**Phase 2 改善方向**：Gemini Agent A + Claude Agent B 異質模型，解決 Echo Chamber。
