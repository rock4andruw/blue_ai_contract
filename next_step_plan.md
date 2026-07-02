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
- [x] **Layer 4 落地（2026-07-02）**：法條依據 + 相似先例真的接進協商建議生成，不再只是路線圖：
  - `legal_citations_cache.json`：用 `mcp-taiwan-legal-db` 真實查回 4 類風險對應的民法/民事訴訟法條文（責任上限、保護條款、不可抗力、管轄法院），離線快取、Demo 執行時純同步讀檔，無即時網路依賴
  - `precedent_corpus.py` + `precedent_corpus.json`：10 筆手寫合成先例案例（緊扣 v2-v6 demo 涵蓋的風險類型），用 `gemini-embedding-2`（3072 維）算真實向量，本地 cosine similarity 檢索，不是關鍵字比對、也不用架 PostgreSQL
  - `llm_service.py`：`_build_user_prompt()` 新增「檢索到的法條」「相似先例」區塊；System Prompt 明確規定「只能引用提供的法條原文，不可自行編造」防止 RAG 反而誘發幻覺；`ReportSection`/API/前端新增 `legal_basis` 欄位，有依據才顯示（比照「來源」欄的誠實揭露邏輯）
  - 實測 v6：協商對策正確引用「民法第216條」真實條文；3 份真實合約 + v4 + v6 全數回歸測試通過
  - **已知缺口**：Verification Agent 補漏（Case C）的 `risk_code` 統一標成 `RISK_AGENT_AUDITED`，查不到對應法條快取（快取用原始 15 種 risk_code 索引）——欄位留空是安全預設值，非顯示錯誤，暫不修復

---

## 近期工作（7 月）

### 立即待辦（2026-07-02 新增）

- [x] **修復重大缺口：API 沒有接 Verification Agent**：`src/api/contracts.py` 的 `_build_response()` 原本自己兜 Parser→Alignment→Diff→RiskEngine→LLM，完全沒呼叫 `verifier.py`——代表 Demo UI（`/demo`，含上傳模式與範例模式）原本看不到今天做的核心功能，只有終端機直接跑 `orchestrator.compare()` 才有。已修復：`contracts.py` 接上 `VerificationAgent`/`cross_check_risks`，`schemas_api.py` 的 `RiskFlagItem` 新增 `source` 欄位，`frontend/demo.html` 完整風險旗標表格加「來源」欄顯示 ✓ 規則引擎／⚠ Agent 補漏。用 Playwright 實際開瀏覽器跑過 v4 範例，畫面正確顯示（3 項 Agent 補漏 + 9 項規則引擎，來源標籤清楚區分），無 console 錯誤。**這幾個檔案尚未 commit。**
- [x] **Commit 所有尚未進版的改動**：`PROJECT_PLAN.md`、`docs/architecture/系統架構_mermaid.md`、`src/api/contracts.py`、`src/api/schemas_api.py`、`frontend/demo.html`（commit `bf73892`）
- [x] **寄出法務回信**：已寄出（2026-07-02）
- [x] **修復 Verification Agent Case A/B/C 比對邏輯（2026-07-02）**：原本只比對 clause_id，同一條款的第二個風險維度會被誤判成「已審查過」而丟棄——用 v6 Demo 範例實測時發現這個 bug 是否觸發取決於 LLM 當次怎麼標 clause_id 字串，同一份合約重跑會不穩定。已修復：比對 key 改成 `(clause_id, 風險類別)`，規則引擎透過新增的 `RISK_CODE_CATEGORY` 對照表換算類別、Agent 沿用既有的 `categorize_candidate()`。v6 重跑 3 次結果穩定一致，3 份真實合約 + v2-v5 全數回歸測試通過。詳見 `docs/specs/verification_agent_spec.md` 第十一節。
- [ ] **不做 Layer 4（pgvector + Taiwan Law MCP）建置**：2026-07-02 再次確認維持原決定，理由見「不做的（競賽前）」清單

### 週次 1（6/30 前，延續中）

- [ ] Demo 流程預排（確認真實合約案例的敘事切入點：千分之一/0.3%、138 段涵蓋率修復、50%→30% 上限）
- [ ] NDA 保密期縮短規則（5年→2年）尚未用真實合約驗證——手上這份 NDA 沒有保密期變更，只驗證了單向→雙向偵測正常

### 週次 2（7/7 前）

- [x] **邊界測試（2026-07-02，完成，發現並修復兩個真實 bug）**：
  - **空條款誤判修復**：`_split_md_clauses()` 對「有子條款」跟「無子條款」兩種情況，content 組成方式不一致（一個去除 `##` 標記、一個保留），導致同一條款若跨版本「有沒有子條款」改變，會產生假差異。已修復為統一用乾淨的 heading+body 組成 content。
  - **文件標題污染修復**：MD 文件的 H1 標題（含版本字樣如 v1/v4）跟序言文字被綁在一起當成一條「條款」，只要標題文字不同（幾乎每份文件都不同）就會產生假差異——**這個問題正在影響現有全部 v2-v6 Demo 範例**，已修復，改成只比對序言本文，標題本身不列入比對。修復後 v2-v6 的「總變動」數字各減少 1 筆假差異，規則引擎偵測數量不受影響（驗證修復只清掉雜訊，沒有動到真實發現）。
  - **⚠️ 嚴重發現並修復：DOCX 原生表格內容完全遺失**：`_parse_docx()` 原本只讀 `doc.paragraphs`，完全沒讀 `doc.tables`——合約裡如果用 Word 原生表格（付款排程表、價格表、簽名欄等），內容 100% 不會進入 raw_text，不會產生 diffs，Verification Agent 也救不了（比 138 段涵蓋率問題更嚴重，那個至少內容還在只是沒條號）。已修復：改成依照文件原始順序（`doc.element.body` XML 走訪）交錯讀取段落與表格，表格轉成逐列文字接入既有流程。用合成 DOCX 驗證：表格內金額 200萬→500萬 的變化現在能正確偵測到。**真實採購合約重新測試後，總變動從 177 增加到 179 處**——之前完全看不到的甲乙雙方簽名欄表格（公司名稱、統編、代表人）現在正確顯示，同時證實乙方版確實已做遮蔽處理（統編、代表人姓名皆為假資料），與法務信件說明一致。
  - **超長條款測試（無問題）**：合成測試從 ~1500 字到 18,447 字單一條款，違約金費率變化埋在大量填充文字前後，規則引擎（情境限定 regex）跟 Verification Agent 皆正確抓到，18K 字案例處理時間 7.5 秒，無崩潰無逾時。difflib 對齊與 LLM prompt 長度皆無問題。
  - 三個邊界類別（空條款／超長條款／純表格條款）皆已測試完成
- [x] **DOCX 格式支援改善（2026-07-02，評估後暫不換函式庫）**：原本考慮換成 markitdown/mammoth，主要動機是 6/27 曾發現的「50200mm」黏合文字 artifact。今天的表格解析修復（依文件原始順序交錯讀取段落與表格）順帶解決了這個問題——重新檢查三份真實合約，該 artifact 已消失，且用 regex 掃描全文找不到其他可疑黏合文字（242／174／166 條款皆乾淨）。**結論**：目前 `pdfplumber` + `python-docx` + 今天的修復已足夠應付現有真實合約，換函式庫會引入新依賴風險但沒有已證實的需求，暫不執行，除非之後遇到新的真實案例證明現有方案不夠用。
- [x] **壓測（2026-07-02，發現並修復嚴重問題）**：**⚠️ 嚴重發現**：`compare_contracts`／`compare_example` 兩個 endpoint 宣告成 `async def`，但內部呼叫的 `_build_response()` 是完全同步、會阻塞的函式（含 Gemini/Claude API 呼叫）。FastAPI 的事件迴圈是單執行緒，同步阻塞呼叫沒有丟進線程池的話，會讓所有並行請求排隊、不是真正並行。實測：5 個並行請求（v2-v6）總耗時 60 秒且 v4 逾時失敗；修復後（`compare_contracts` 用 `run_in_threadpool` 包住呼叫、`compare_example` 改成 plain `def` 讓 FastAPI 自動丟線程池）同樣 5 個並行請求總耗時降到 32 秒、全部成功無逾時。另測 3 人同時點同一個範例（v4，比賽現場常見情境）：32.5 秒內全部成功，無崩潰無逾時。**這個問題如果沒抓到，Demo 當天只要有第二個人同時測試系統，正在展示的請求就可能被排到後面逾時失敗。**

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
- ✅ **Layer 4：pgvector 語意檢索 + Taiwan Law MCP 法條查詢**（2026-07-02 已建置並接進系統，見下方備忘與「已完成」清單）

  > **2026-07-02 技術探索備忘**（若之後要做，直接從這裡接續，不用重新調查）：
  > - **MCP 已找到現成、真實可用的套件**：`pip install mcp-taiwan-legal-db`（[github.com/lawchat-oss/mcp-taiwan-legal-db](https://github.com/lawchat-oss/mcp-taiwan-legal-db)，MIT 授權、免 API key、接法務部全國法規資料庫）。實際測試過用 MCP client 查詢「民法 252 條」，即時打到 `law.moj.gov.tw` 拿到真實條文「約定之違約金額過高者，法院得減至相當之數額。」——不是模擬，是真的查得到。
  > - **架構限制**：`llm_service.py` 現有函式全部是同步（`def`），MCP client SDK 是 async-only，兩者不相容；且 FastAPI request handler 本身已在 event loop 中，不能再呼叫 `asyncio.run()`。此外 MAS 用的並行模式是 `ThreadPoolExecutor`（執行緒），不是 asyncio，硬接會變成兩套並行典範並存。
  > - **建議做法（若要做）**：不要在 Demo 執行路徑裡即時呼叫 MCP。改成離線階段用 MCP 查好用得到的法條（約 10-15 條，對應現有風險類別），存成靜態 JSON 快取，Demo 執行時同步讀取本地檔案即可——完全不用碰 async，也不會讓 Demo 依賴政府網站即時回應（避免新增一個會斷線的風險點）。pgvector 語料庫比照辦理：LLM 生成 20-30 筆合成合約條款範例（涵蓋 15 類風險），本地相似度比對，不用真的架 PostgreSQL。
  > - **Prompt 設計已定案**：`_build_user_prompt()` 已有現成但從未使用的 `reference_clause` 擴充點，可直接沿用同樣模式加「檢索到的法條」「相似先例」兩個區塊；System Prompt 需明確規定「只能引用提供的法條原文，不可自行引用或編造」，避免加了 RAG 反而更容易產生看似權威的幻覺；`ReportSection` 新增 `legal_basis` 欄位，比照「來源」欄的邏輯，有依據才顯示。
  > - **定位確認**：不是自主 agent，是 AI 協作的 workflow——不需要 LangGraph 或任何 agentic 框架，純粹是「程式碼決定順序，LLM 只在固定的點被呼叫填空」。
  > - **授權確認（2026-07-02）**：套件本身 MIT 授權，可商用（僅需保留版權聲明）。查到的法條/判決書內容依《著作權法》第9條屬公文性質，不受著作權保護，商業使用也沒有內容授權問題（大法官解釋資料另標示 CC0）。**唯一要注意的是存取方式**：套件用 Playwright 繞過政府網站的 WAF（log 顯示 `WAF bypass: running Playwright warmup...`），這跟授權無關，是存取條款層面的風險——現在低頻離線查詢（個位數次）風險極低，但若之後正式商業化、高頻呼叫，建議改查 law.moj.gov.tw 有無官方開放資料 API，不要長期依賴繞過 WAF 的爬蟲方式。
  > - **8 個可用工具**：`query_regulation`（查法條）、`search_regulations`、`get_pcode`、`search_judgments`（查真實判決，可用 `main_text` 關鍵字篩選勝敗訴結果）、`get_judgment`、`get_interpretation`（大法官解釋）、`search_interpretations`、`get_citations`。目前只測試過 `query_regulation`；`search_judgments` 可查真實判決先例，比單純法條引用更有份量，時間夠可以考慮加。
  > - **v6 Demo 範例（2026-07-02 完工）**：`sla_contract/maintenance_v6_base.md` + `maintenance_v6_penalty_rate.md`，合成軟體維護合約（假公司名：星曜科技／安碩資訊），重現「千分之一 vs 0.3%」+「50%→30% 上限」兩個真實發現的模式。已接進 `contracts.py`（`EXAMPLE_CONTRACTS` + 新增 `EXAMPLE_BASE_OVERRIDE`，因為 v6 用自己的 base 檔案，不沿用 v1）、`demo.html` 新增 v6 範例按鈕。用 Playwright 實際開瀏覽器驗證：畫面正確顯示規則引擎（責任上限 50%→30%）+ Agent 補漏（違約金費率 0.3%→千分之一）兩層來源標籤，無 console 錯誤。**尚未做**：民法252條快取資料（`legal_citations_cache.json`）還沒接進 `llm_service.py` 協商建議生成流程，目前只是存著沒被使用——這是加分項，非必要，核心「千分之一」故事光靠 Verification Agent 的來源標籤已經夠強。
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

## 常見追問與回答（Q&A 準備）

### 「為什麼這樣設計？」（架構核心提問，優先準備）

> 因為合約風險審查其實包含兩種完全不同性質的問題。一種是規律性的——像違約金比例下降、責任上限縮水，這種資深法務看到不會每次重新思考，是內化的判斷準則；另一種是需要真正語意理解的——像沒看過的寫法、條文之間的關聯。我們刻意把這兩種問題分給最適合處理的機制：規則引擎負責前者，100% 可重現、免費、瞬間；LLM 負責後者，需要語意彈性的部分。
>
> 如果只用 LLM 做全部判斷，我們就會失去「這個類別保證抓得到」這個承諾——這對法務工具是最關鍵的，因為你要的是可證明的信任，不是單次判斷可能比較聰明。同樣的理由，我們也沒有把系統做成自主 agent——法務審查需要可預測、可測試，不需要模型自己決定下一步要做什麼，所以是刻意設計成 AI 協作的 workflow，不是自主決策的系統。
>
> 這不是憑空講的理論。我們拿了三組真實公司合約實測，過程中真的發現規則引擎有漏洞——像「千分之一」這種中文分數寫法，Regex 完全看不懂，而語意補漏這層真的把它抓回來了。這證明了這個架構的必要性，是被真實資料驗證過的，不是紙上談兵。

**這段話涵蓋的五個層次**（追問任何一句都有真實案例可以撐）：

1. 問題本質：規律性風險 vs 需語意理解的風險，兩種性質不同
2. 設計原則：規則負責前者（確定性）、LLM 負責後者（彈性）
3. 為什麼不只用 LLM：會失去「可證明的召回保證」，法務工具的信任基礎
4. 為什麼不是自主 agent：法務審查需要可預測、可測試，不需要模型自己決策——這是刻意的 AI 協作 workflow 設計，不是自主決策系統
5. 真實驗證證據：三組真實合約測試中，規則引擎的漏洞是真的存在、真的被 Verification Agent 補上（千分之一案例）

### 「這是真的 Agent 嗎？有沒有用 LangChain/AutoGPT 那種工具自主呼叫？」

> 我們用「Agent」是指它扮演獨立審查者的角色（跟規則引擎的判斷分開驗證），不是指有工具自主呼叫的能力——目前是結構化的單次 LLM 呼叫嵌在固定流程裡，不是會自己決策的 agentic loop。這是刻意的選擇：我們的每一步都需要可預測、可測試，不需要模型自己決定要不要重試或換方向。

### 「為什麼不乾脆全部用 LLM，省掉維護規則引擎的麻煩？」

> 兩種問題性質不同，混在一起用同一種方法解，效率跟穩定性都受損。規則負責的部分是有確定解的（可用率下降多少算高風險，這是可以窮舉的），LLM 負責的部分才是真正需要語意判斷的。如果全部都用 LLM，等於把原本零成本、瞬間、100% 一致的判斷，降級成要花錢、要等、還可能每次結果不一樣的機率性判斷——這不是更聰明，是把簡單問題複雜化，也會讓「100% 高風險召回」這個核心賣點站不住腳。

---

## MAS 現況補充

**Phase 1.5 誠實定位**：對立 Persona 驅動的雙視角評估，非嚴格獨立驗證。相同模型 + 不同 Persona，Echo Chamber 限制存在，但 Persona 差異仍能提供有意義的觀點分歧（文獻支撐：論文 1-3）。

**實測 pending 率**：

- v4（明確高風險）：0%（兩個 Agent 均同意）
- v3（責任條款有爭議）：67%（11.1 / 11.3 真正分歧，符合預期）

**Phase 2 改善方向**：Gemini Agent A + Claude Agent B 異質模型，解決 Echo Chamber。
