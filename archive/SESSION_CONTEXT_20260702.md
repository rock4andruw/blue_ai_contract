# Session 說明檔：2026-07-02 工作紀錄

> 讀完這份文件，新的 AI session 可以立刻接續工作，不需要重新說明背景。
> 系統完整說明請見 PROJECT_CONTEXT.md。上一份：`SESSION_CONTEXT_20260701.md`（Verification Agent 實作、真實合約測試）。

**這是本次 session 目前為止資訊量最大的一次**，累計 **14 個 commit**，發現並修復 6 個真實 bug（含 1 個嚴重資料遺失、1 個嚴重並行阻塞），並把 Layer 4（法律依據 + 先例檢索）從路線圖變成真正在跑的功能。

---

## 本次 Session 完成的工作

### 1. 法務溝通

- 收到法務回信：合約金額/日期已虛構化，供內部參考；法務祐銓可以顧問角色參與（競賽規則不能正式加入團隊）；法務主動問「能否往 AI 法務發展」
- 回信已擬定並寄出：說明競賽規則限制、歡迎祐銓以顧問身分協助、AI 法務方向對應到 Layer 4 路線圖

### 2. CLM（合約生命週期管理）定位加入 `PROJECT_PLAN.md`

系統定位在 CLM 七階段的第 3 階段「審閱與協商」，且是其中「乙方回傳修改版後比對判斷」的子步驟。明確排除：起草、核准簽署、履約管理。這個定位加進了「二、解決什麼問題」章節。

### 3. 簡報收斂原則確定

技術亮點只講一個故事（千分之一），其他細節（涵蓋率修復、交叉核對邏輯、CLM、Layer 4）當 Q&A 備援彈藥，不排進主線——避免資訊過載稀釋重點。

### 4. ⚠️ 重大缺口修復：API 完全沒接 Verification Agent

`src/api/contracts.py` 的 `_build_response()` 原本自己兜 Parser→Alignment→Diff→RiskEngine→LLM，完全沒呼叫 `verifier.py`——代表 Demo UI（含上傳模式與範例模式）原本看不到 Verification Agent，只有終端機直接跑 `orchestrator.compare()` 才有這個功能。**如果沒發現，比賽當天的招牌功能等於沒接上。** 已修復：接上 `VerificationAgent`/`cross_check_risks`，`RiskFlagItem` 新增 `source` 欄位，`demo.html` 加「來源」欄顯示 ✓ 規則引擎／⚠ Agent 補漏。Playwright 瀏覽器驗證通過。

### 5. Verification Agent 交叉核對邏輯修正（`/goal 修正clause_id`）

**問題**：`cross_check_risks()` 原本只比對 `clause_id`，同一條款若同時存在規則引擎與 Agent 抓到的不同風險維度，Agent 的發現會被誤判成「已審查過」而丟棄。用 v6 範例實測時發現：這個 bug 觸不觸發取決於 LLM 當次怎麼標 clause_id 字串，**同一份合約重跑結果會不穩定**。

**修法**：比對 key 改成 `(clause_id, 風險類別)`，新增 `RISK_CODE_CATEGORY` 對照表讓規則引擎的 15 種 risk_code 換算成跟 Agent 共用的分類。v6 連跑 3 次結果穩定一致；3 份真實合約 + v2-v5 全數回歸測試通過。**已知殘留限制**：關鍵字分類本身仍有歧義（如「違約金上限」同時命中兩類），最壞情況多一筆無害重複旗標，不會再漏掉真正的發現。

### 6. v6 Demo 範例建立並接進系統

合成的「軟體系統維護服務合約」（假公司：星曜科技／安碩資訊），重現真實合約發現的「千分之一 vs 0.3%」+「50%→30% 上限」兩個模式，安全可公開展示（無機密資料）。已接進 `contracts.py`（新增 `EXAMPLE_BASE_OVERRIDE`，因為 v6 用自己的 base 檔案不沿用 v1）、`demo.html` 新增按鈕。Playwright 驗證正常。

### 7. 邊界測試（`/goal 繼續完成`）——發現 3 個真實 bug

- **空條款誤判**：`_split_md_clauses()` 對「有無子條款」content 組成方式不一致，導致假差異。已修復。
- **文件標題污染（正在影響全部 v2-v6 範例）**：MD 文件 H1 標題（含版本字樣）跟序言綁在一起當條款，標題不同就產生假差異——每份 demo 文件標題都不同，這個問題正在污染全部範例。已修復：只比對序言本文，標題不列入比對。
- **⚠️ 嚴重：DOCX 原生表格內容完全遺失**：`_parse_docx()` 原本只讀 `doc.paragraphs`，完全沒讀 `doc.tables`——付款排程表、簽名欄等表格內容 100% 不進 raw_text，不產生 diffs，Verification Agent 也救不了（比之前的 138 段涵蓋率問題更嚴重，那個至少內容還在）。已修復：依文件原始順序（XML body 走訪）交錯讀取段落與表格。真實採購合約重新測試：總變動從 177 增加到 179 處（之前看不到的簽名欄表格現在正確顯示，同時驗證了乙方版確實已遮蔽）。
- 超長條款測試（18,447 字）：無問題，7.5 秒處理完畢。

### 8. 壓測（`/goal 繼續完成`）——發現嚴重並行阻塞問題

**問題**：`compare_contracts`/`compare_example` 宣告成 `async def`，但內部呼叫的 `_build_response()` 完全同步阻塞（含 Gemini/Claude API 呼叫）。FastAPI 事件迴圈單執行緒，同步阻塞呼叫沒丟進線程池會讓並行請求排隊。實測：5 個並行請求原本 60 秒且逾時失敗；修復後（`run_in_threadpool` + 把 `compare_example` 改成 plain `def`）32 秒全部成功。**這是最貼近「Demo 當天多人同時測試會卡死」的具體風險。**

### 9. DOCX 格式改善評估：不需要換函式庫

原本考慮 markitdown/mammoth，主要動機是舊有的「50200mm」文字黏合 artifact——今天的表格解析修復順帶解決了這個問題，重新掃描三份真實合約已無異常。維持現有 `pdfplumber` + `python-docx` 方案。

**至此 `next_step_plan.md` 週次 2 清單（邊界測試／壓測／DOCX 改善）全數完成。**

### 10. MCP 技術驗證：找到真實可用套件

用戶提供 GitHub 連結，找到 `mcp-taiwan-legal-db`（MIT 授權、免 API key、接法務部全國法規資料庫）。實測用真正的 MCP client（`ClientSession`+`stdio_client`）查詢「民法252條」，即時打到 `law.moj.gov.tw` 拿到真實條文。授權確認：程式碼 MIT 可商用，法條/判決書內容依著作權法第9條不受著作權保護；**唯一要注意**：套件用 Playwright 繞過政府網站 WAF，是存取條款層面的風險（跟授權無關），現在低頻查詢風險低，未來高頻商用建議改走官方 API。

### 11. 架構定位釐清：AI 協作，不是自主 Agent

系統裡每次 LLM 呼叫都是結構化單次任務，由程式碼決定執行順序，不需要 LangGraph 等 agentic 框架。「協作」體現在兩層：系統內部（規則引擎/Verification Agent/MAS 各自貢獻判斷角度）與人機之間（AI 產出分析、人做最終決策）。已加進 `PROJECT_PLAN.md` 核心原則段落，並準備好完整的「為什麼這樣設計」評審問答稿（`next_step_plan.md`）。

### 12. Layer 4 完整落地：從路線圖變成真正在跑的功能

- **法條依據**：`legal_citations_cache.json`，用 `mcp-taiwan-legal-db` 真實查回 4 類風險（責任上限、保護條款、不可抗力、管轄法院）對應的民法/民事訴訟法條文，離線快取，Demo 執行時純同步讀檔
- **相似先例**：`precedent_corpus.py` + `precedent_corpus.json`，10 筆手寫合成先例（緊扣 v2-v6 涵蓋的風險類型），用 **`gemini-embedding-2`**（3072 維，正式發行版，注意不是舊版 `gemini-embedding-001`）算真實向量，本地 cosine similarity 檢索——真正的語意向量搜尋，不是關鍵字比對，也不用架 PostgreSQL
- **接進 `llm_service.py`**：`analyze_flag()` 生成協商建議前會查法條快取 + 查相似先例；System Prompt 明確禁止編造未提供的法條（避免 RAG 反而誘發看似權威的幻覺）；`ReportSection`/API/前端新增 `legal_basis` 欄位，有依據才顯示
- **實測驗證**：v6 報告的協商對策真的引用了「民法第216條」真實條文，Playwright 瀏覽器截圖確認「⚖ 法律依據」正確顯示；3 份真實合約 + v4 + v6 全數回歸測試通過
- **已知缺口**：Verification Agent 補漏（Case C）統一標成 `RISK_AGENT_AUDITED`，查不到對應法條（快取用原始 15 種 risk_code 索引），欄位留空是安全預設值，非顯示錯誤

### 13. 架構圖更新

`docs/architecture/系統架構_mermaid.md`：Layer 4（法條快取 + 先例檢索）從「Phase 2 未來規劃」移到「Phase 1 已完成」區塊，正確畫出資料流向（接在 Verification Agent 之後、LLM Service 之前）。Phase 2 現在只剩真正未做的項目（真實 PostgreSQL、Office 365 MCP、合約類型擴展、異質模型 MAS）。

---

## 這次 Session 的方法論

延續 07-01 建立的模式：**每個聲稱都要有真實測試或真實查詢佐證**，不用猜的。這次特別值得記錄的兩次「被使用者糾正」：
1. 猜測 `gemini-embedding-001` 作為 embedding 模型，被糾正為正式發行的 `gemini-embedding-2`（3072 維，2026-04-22 發布）——教訓：不要用訓練知識猜模型名稱，要用真實 API 查詢或請使用者確認
2. 提議在 Demo 現場秀真實公司合約（v6 構想的初版），被自己攔下並跟使用者確認——最終方向是用合成範例重現真實發現的模式，不直接展示機密資料

---

## 待完成工作（優先順序，2026-07-02 更新）

| 優先度 | 工作 | 備註 |
|---|---|---|
| 🟡 中 | 週次 3：簡報製作（含更新後的架構圖）、部長話術、Demo 預演 | 尚未開始，是接下來的主線 |
| 🟢 低 | Verification Agent Case C 查不到法條快取的問題 | 已知缺口，risk_code 統一標籤導致，不影響安全性 |
| 🟢 低 | 12 條規則風險等級寫死不看幅度 | 07-01 已發現，暫緩 |
| ⚪ 路線圖 | 真實 PostgreSQL + pgvector、Office 365 MCP、合約類型擴展、異質模型 MAS | Phase 2/3，競賽後才考慮 |

---

## 重要文件索引（更新）

| 文件 | 用途 |
|---|---|
| `SESSION_CONTEXT_20260702.md` | 本文件 |
| `SESSION_CONTEXT_20260701.md` | 前一份（Verification Agent 實作、真實合約測試） |
| `next_step_plan.md` | 任務清單 + Q&A 準備 + 技術探索備忘，已更新至 2026-07-02，內容量最大的參考文件 |
| `PROJECT_PLAN.md` | 對外簡報文件，已同步 Layer 4 完成狀態、CLM 定位、AI 協作定位 |
| `docs/architecture/系統架構_mermaid.md` | 架構圖，已反映 Layer 4 完成狀態 |
| `docs/specs/verification_agent_spec.md` | 第十一節記錄 clause_id/風險類別比對修復 |
| `src/services/contract/legal_citations_cache.json` | 真實法條快取（4 類風險） |
| `src/services/contract/precedent_corpus.py` / `.json` | 先例語料庫 + 向量檢索邏輯 |
| `sla_contract/maintenance_v6_*.md` | v6 合成範例（安全展示用） |

---

## 程式碼改動清單（本次 Session，14 個 commit）

1. `fix(api)`: 接上 Verification Agent 到 `contracts.py`（含 `source` 欄位）
2. `fix(verifier)`: Case A/B/C 比對改成 `(clause_id, 風險類別)`
3. `feat(demo)`: v6 範例接進 API/UI
4. `docs`: 多次更新 `next_step_plan.md`／`PROJECT_PLAN.md`
5. `fix(parser)`: DOCX 表格解析 + MD 標題/序言假差異修復
6. `fix(api)`: `run_in_threadpool` 並行阻塞修復
7. `feat(layer4)`: 法條快取 + 先例語料庫 + 接進 `llm_service.py`
8. `chore`: 語料庫檔案精簡格式
9. `docs(diagram)`: 架構圖 Layer 4 狀態更新

全部經真實資料或合成測試驗證，皆已 commit，尚未 push 到 origin。

---

*Session 日期：2026-07-02 ｜ Blue-AI Team*
