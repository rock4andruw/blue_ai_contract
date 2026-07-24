# Blue-AI 專案脈絡文件（Claude Code 冷啟動用）

> 讀完這份文件就能立刻進入開發模式，不需要問問題。
> 這份是**滾動更新**的權威脈絡文件——每次架構有實質變動就回來改這裡，不要另開新的日期檔案（見 `docs/harness/G_handover.md` 的腐化預防原則）。
> 最後更新：2026-07-05

---

## 1. 專案一句話說明

企業合約（SLA / NDA / 採購）智能比對助理。上傳兩份合約版本，輸出：重點風險摘要、三層協商對策、MAS 雙重驗證結果、法律依據、報告內問答、協商矩陣。

**Slogan**：「像有一個資深法務顧問幫你審合約」

---

## 2. 競賽背景（最重要的限制條件）

- **場合**：公司內部 AI 實作競賽，6 / 7 / 8 月大P月會向三位部長（AI / AP / Infra）簡報，20 分鐘
- **評分**：技術性 + 實用性 + 商機推廣
- **截止**：2026 年 8 月初
- **關鍵約束**：Lumine AI 是公司**自己的產品**，Blue-AI 必須定位為**互補延伸**，絕不能說是競品或替代品。違反此原則的描述一律拒絕。
- **一句話定位（面對「這是不是自主 Agent」的追問）**：「我們是工程化與 MAS 的結合」——核心風險判斷維持確定性（規則引擎），語意理解/交叉驗證/法律依據檢索交給 LLM/Agent，不是選邊站。

---

## 3. 如何啟動

```bash
# 安裝依賴
pip install fastapi uvicorn python-docx pdfplumber anthropic google-genai

# 設定 API Key（至少選一個，.env 檔會被 orchestrator.py / api/main.py 的 load_dotenv() 讀取）
export GEMINI_API_KEY=...       # 主要（優先）
export ANTHROPIC_API_KEY=...    # 備援
# 兩個都沒有也能跑——自動使用 template fallback

# 啟動 API 伺服器
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Demo UI
open frontend/demo.html          # 直接開本地靜態檔
# 或 http://localhost:8000/demo

# 執行 gold set 驗證
python3 -m src.services.contract.evaluate
```

---

## 4. 核心架構（Parser → ... → Report，含 Layer 1/2/3 + MAS）

```
Parser → Alignment → Diff Engine → Risk Rule Engine（Layer 1）→ Verification Agent（Layer 2）→ LLM Service
                                                                                                    ↓
                                                                          MAS（Agent A/B + Judge，高風險才觸發，LLM 分析後才跑）
                                                                                                    ↓
                                                                                            Report Generator
                                          ↑
                            Layer 3（法條快取 + 先例向量檢索）餵給 LLM Service，協商建議才有法律依據
                                          ↓
                                   Negotiate（按需，點按鈕才呼叫）/ 協商矩陣（批次）/ 報告內問答（按需）
```

**設計原則：Risk Rule Engine 做判斷，LLM 只做解釋，MAS 做驗證。**
LLM 不決定風險等級，規則引擎判定後 LLM 才負責翻成白話並給對策；MAS 只對高風險 flag 做交叉驗證，可能覆蓋規則引擎的風險等級。

**重要**：MAS 觸發順序是 `analyze_flag()`（LLM Service）先跑完，才跑 `run_mas()`——不是直接接在 Risk Rule Engine 後面。架構圖（`docs/architecture/系統架構_mermaid.md`）已依此順序畫。

---

## 5. 每個模組做什麼

| 檔案 | 功能 |
|---|---|
| `schemas.py` | 共用資料型別：Clause / DiffItem / RiskFlag / ReportSection / RISK_CODES（內部資料流程注解用 Stage 1-5 編號，跟外部 Layer 1/2/3 是兩套不同編號，不要混用） |
| `parser.py` | MD / PDF / DOCX 解析。DOCX 依 `doc.element.body` 原始順序交錯讀取段落與表格（`_iter_docx_block_items`），不遺漏原生 Word 表格 |
| `alignment.py` | LCS + Needleman-Wunsch 對齊，difflib ≥ 75% 相似度後處理（處理重新編號條款） |
| `diff_engine.py` | 新增 / 修改 / 刪除差異比對 |
| `risk_engine.py` | 14 條規則（pure Python），high-risk recall 100%（另有 2 個設計類別未實作，見第 6 節） |
| `verifier.py` | **Verification Agent（Layer 2）**：LLM 語意補漏，只讀變動條款不讀全文，與規則引擎交叉核對（key=`(clause_id, 風險類別)`），Case C 發現記錄進 `candidate_rules.jsonl`（不自動生規則） |
| `llm_service.py` | Gemini（主）/ Claude（備）/ template fallback。`generate_sections()` 回傳所有高風險 + top 3 中風險；`answer_report_question()` 是報告內問答 |
| `precedent_corpus.py` | Layer 3 先例向量檢索：10 筆合成案例，`gemini-embedding-2` 真實向量，本地 cosine similarity |
| `legal_citations_cache.json` | Layer 3 法條快取：`mcp-taiwan-legal-db` 離線查回的真實民法/民訴法條文，同步讀檔 |
| `mas_service.py` | Agent A（嚴格）+ Agent B（平衡）ThreadPoolExecutor 平行執行，Judge 矩陣輸出 confirmed / pending |
| `negotiate_service.py` | Static Playbook（從 skill.md 解析）+ LLM 精煉，輸出 tier1 / tier2 / redline + 替換條款文字；`generate_matrix()` 是協商矩陣批次生成 |
| `report_generator.py` | 組裝最終報告 |
| `orchestrator.py` | 全流程串接（CLI 用，含 `load_dotenv()`） |
| `contracts.py` | FastAPI endpoints：compare / example / negotiate / negotiate/matrix / ask |
| `evaluate.py` | Gold set 驗證腳本，跑 v2-v5 vs 人工標註 |

---

## 6. 風險規則設計表（15 個設計類別，13 個已實作）

**2026-07-16 查證**：這張表列的是設計時定義的 15 個風險類別，但 `risk_engine.py` 的 `RULES` 清單只有 **14 個規則函式**，逐一 grep 核實後發現 `RISK_LIABILITY_INCREASE`、`RISK_PROTECTION_ADDED` 這兩個「對甲方有利」的正向類別**從未被任何程式碼實際發出過**——系統目前只偵測不利風險，正向發現這塊是設計了但沒做的空白。下表標註哪些已實作。

| 規則代碼 | 等級 | 說明 | 實作狀態 |
|---|---|---|---|
| RISK_SLA_DEGRADE | 高 | SLA 可用率降低 ≥ 0.5% | ✅ |
| RISK_RESPONSE_TIME_EXTENDED | 高 | 回應 / 修復時間拉長 | ✅ |
| RISK_PENALTY_WEAKENED | 高 | 違約折讓比例降低 | ✅ |
| RISK_LIABILITY_CAP_CHANGED | 高 | 賠償上限縮水 | ✅ |
| RISK_PROTECTION_REMOVED | 高 | 保護性條款刪除 | ✅ |
| RISK_CONFIDENTIALITY_WEAKENED | 高 | 保密期間縮短 | ✅ |
| RISK_DATA_CONTROL_LOST | 高 | 資料控制權降低 | ✅ |
| RISK_IP_OWNERSHIP_CHANGED | 高 | 智財權歸屬改為乙方 | ✅ |
| RISK_LIABILITY_DIRECTION_REVERSED | 高 | 違約賠償責任方向反轉 | ✅ |
| RISK_CONFIDENTIALITY_SCOPE_CHANGED | 高 | 保密從單向→雙向 | ✅ |
| RISK_LIABILITY_INCREASE | 中 | 責任加重（對甲方有利） | ❌ 未實作 |
| RISK_TERMINATION_CHANGED | 中 | 終止條款變更 | ✅ |
| RISK_FORCE_MAJEURE_EXPANDED | 中 | 不可抗力範圍擴大 | ✅ |
| RISK_JURISDICTION_CHANGED | 中 | 管轄法院改變 | ✅ |
| RISK_PROTECTION_ADDED | 低 | 新增保護條款（正向） | ❌ 未實作 |

---

## 7. MAS Phase 1.5 設計

```
高風險 flag（LLM Service 分析後才觸發）→ ThreadPoolExecutor(max_workers=2)
                ├── Agent A（嚴格）：最壞情況視角
                └── Agent B（平衡）：台灣業界慣例視角
                         ↓
                    Judge 矩陣
                    gap=0/1 → confirmed（嚴格優先）
                    gap=2   → pending（真正分歧，需人工判斷）
                    失敗    → single_agent（靜默退級）
```

- **盲評**：Agent 不知道 Rule Engine 答案，也不知道對方答案
- **知識庫**：從 `.claude/skills/contract-risk-analysis.md`（Agent A）和 `.claude/skills/negotiation-strategy.md`（Agent B）動態載入
- **限制**：Phase 1.5 兩個 Agent 使用同一模型（Gemini），Phase 2 才改用異質模型
- **學術支撐**：*Judging with Many Minds (2025)*、*When Truth Is Overridden (2025)*

---

## 8. 已驗證數字（2026-07-07 釐清，取代 07-03 舊版）

- 38 筆是人工標註**總筆數**（v2~v5，含無風險改動）；篩選出真正有商業風險的 adverse conditions 只有 **22 筆**（v2: 11 + v4: 11）
- 這 22 筆中，**高風險只有 5 筆**（v4: 11.1/11.2/11.3 責任上限縮小；v2: 5.2/5.3 回應時間延長）——Rule Engine **100% 找到（5/5）**
- **整體偵測率 54%**（12/22，涵蓋高中低風險）——不是「67%」，那是舊版誤用分母（12/18）算出來的錯誤數字
- MAS pending 率：v4 = 0%（明確案例），v3 = **100%**（2 個高風險條款皆分歧，非常適合展示「誠實承認分歧」的敘事）

⚠️ **demo.html 上 v4 顯示「9 筆高風險」不是矛盾**：那是規則引擎 + Verification Agent 補漏後的**完整系統輸出**（規則找 5-6 筆確定性高風險 + Agent 補漏約 4 筆邊界案例）。gold set 的「5/5」驗證的是規則引擎的正確性基準，demo 的「9」是完整系統的實際產出，簡報時兩個數字要分層說明，不能混講。

---

## 9. 測試合約與敏感資料保護

| 目錄 | 內容 | 保護狀態 |
|---|---|---|
| `sla_contract/` | v1（基準）、v2 降級、v3 責任加重、v4 保護刪減、v5 終止偏甲方、v6 獨立軟體維護合約（違約金費率格式問題） | Read/Edit/Write deny（`.claude/settings.json`） |
| `nda_contract/` | v1（甲方版）、v2（乙方修改版） | 同上 |
| `pic_contract/` | 真實公司合約樣本（NDA / 軟體採購 / 軟體維護），已去識別化，**不進 git、不在 Demo 公開展示** | 同上 |

這三個目錄受 deny + `guard_sensitive.py` hook 雙重保護：列舉/搜尋（`ls`/`grep`/`git`）放行，讀取內容的動詞（`cat`/`python` 開檔等）會被擋。看到 hook 擋下是刻意的，不要重試。

Demo 建議流程：
1. 範例 v6（Verification Agent 補漏「千分之一」+ Layer 3 真實法條引用）→ 旗艦故事
2. 範例 v4（多筆高風險全 confirmed）→ 展示效率與精準
3. 範例 v3（100% pending）→ 展示 AI 誠實承認分歧
4. 點「生成協商對策」/「匯出協商矩陣」/ 報告內問答 → 展示按需功能

---

## 10. 已知問題（待修正）

見 `next_step_plan.md`（滾動更新的待辦清單，開發前先看這份，不要看這裡的舊清單）。

---

## 11. 已修過的重要 Bug（不要改回去）

| Bug | 修法 |
|---|---|
| DOCX 被解析成 1 個 clause | `parser.py` 用 `"\n\n".join()` 而非 `"\n".join()` |
| DOCX 原生表格內容完全遺失 | `_iter_docx_block_items()` 依文件原始順序交錯讀取段落與表格 |
| 純新增/刪除條款因缺條號被靜默丟棄 | Diff Engine 涵蓋率修復（採購合約 138 段一度消失） |
| Risk Engine 跳過所有 NDA 條款 | `risk_engine.py` 移除 `if diff.clause_id == "?": continue` |
| clause_id 顯示為 "?" | `diff_engine.py` 用 `title[:15]` 作為 fallback |
| Verification Agent Case A/B/C 比對不穩定 | 比對 key 改成 `(clause_id, 風險類別)`，不是單獨 clause_id |
| 並行請求排隊阻塞（5 個並行請求 60 秒、v4 逾時） | `compare_contracts` 用 `run_in_threadpool`，`compare_example` 改 plain `def` |
| MD 文件 H1 標題污染比對（每份文件標題不同產生假差異） | `_split_md_clauses()` 排除標題行，只比對序言本文 |

---

## 12. 前端（demo.html）重點

- 靜態單頁 HTML，直接開啟即可（不需要 server），視覺語言是法律文件 editorial 風格（EB Garamond 襯線標題 + IBM Plex Mono 等寬大寫標籤 + 左邊框色塊表語意），不是聊天軟體風格
- 兩個 tab：上傳模式 / 範例模式（v2-v6）
- 高風險自動展開，中風險預設收合
- 風險旗標表格有「來源」欄：`✓ 規則引擎` / `⚠ Agent 補漏`
- 三層協商對策、報告內問答、協商矩陣皆按需呼叫（點按鈕才觸發）
- MAS 標籤：`✓ 雙重驗證`（綠）/ `⚠ 待確認`（黃）
- 報告內問答的答案依「有依據／查無資料」呈現不同視覺樣式（金色實線 vs 灰色虛線）
- 協商矩陣支援 `@media print`，可直接列印/存 PDF

---

## 13. Skills 目錄（`.claude/skills/`）——雙重身分，動之前必讀

`docs/harness/skills_runtime_assets.md` 有完整說明，這裡只講重點：

- **2 個平面 `.md` 檔是 runtime prompt 資產，不是 Claude Code skill**：`contract-risk-analysis.md`（Agent A + Verification Agent 知識庫）、`negotiation-strategy.md`（Agent B + 協商框架 + 三層 Playbook 知識庫）。被 `mas_service.py`/`verifier.py`/`llm_service.py`/`negotiate_service.py` 用 `_load_skill_section()` 精確讀取檔內特定 `##` 段落（非整份檔案），**絕不可搬移/改格式/改名**，settings.json deny + hook 精確保護這 2 個檔名。編輯內容可以。
- **`frontend-design/SKILL.md` 是正式的 Claude Code skill**（2026-07-05 轉正），可以正常呼叫，不受上述限制。
- **`contract-diff.md`、`report-writing.md` 已封存**（2026-07-16，`archive/skills_dead_assets/`）：逐段落 grep 核實後證實從未被任何 loader 引用，原本誤算進保護範圍，詳見 `docs/harness/skills_runtime_assets.md` 第 4 節。

---

## 14. 已經做完的事（不是「不做」清單）

以下項目**已經實作並在 Demo 中運作**，不是規劃中：
- ✅ Verification Agent（Layer 2，語意補漏 + 交叉核對）
- ✅ Layer 3 法律依據檢索：真實法條快取（`mcp-taiwan-legal-db`）+ 先例向量檢索（`gemini-embedding-2`，本地 cosine similarity，非 PostgreSQL/pgvector）
- ✅ 報告內問答（`POST /ask`）+ 協商矩陣（`POST /negotiate/matrix`），含前端 UI

真正還沒做、且賽前不做的（見 `next_step_plan.md`「不做」清單與 `docs/planning/agent_db_mcp_roadmap.md`）：
- ❌ 真實 PostgreSQL + pgvector（現用本地 JSON + cosine 替代）
- ❌ Gemini + Claude 異質 MAS（Phase 2）
- ❌ MCP 即時判決查詢（`search_judgments`，現只離線用 `query_regulation`）
- ❌ Teams / SharePoint 整合
- ❌ 企業資本額 Insight 分析（需外部資料源）

---

## 15. 對三位部長的切入點（2026-07-07 修正：AP≠財務，Infra≠部署複雜度）

| 評審 | 主攻 |
|---|---|
| AI 部長 | 可信 AI 治理：規則可解釋 + Agent 補漏標籤透明 + 不確定時誠實 pending、MAS 學術支撐、高風險 5/5 recall（非「67%」） |
| **AP 部長**（**Application 應用部門**，不是財務）| 系統怎麼嵌入既有業務流程（SharePoint/Teams 工作流無縫整合）、SaaS 產品化路徑；ROI 數字是次要佐證，不是主軸 |
| **Infra 部長** | 優先講**機敏資料全生命週期防護**（進/處理/出/故障時的資料安全），不是部署複雜度或效能數字。現況已實裝：加密、自動刪除、零資料庫、DPA；Purview DLP 標記與 LiteLLM 事前過濾是 **Phase 2 規劃**，講的時候要標示清楚，不能講成已完成 |
| 黑客松評審 | 誠實揭露敘事：來源標籤、查無依據就留白、MAS 誠實承認分歧（v3 100% pending） |

詳細話術見 `champion_pitch_hackathon.md` / `presenter_script_hackathon.md`（黑客松簡報版，取代舊版 `PROJECT_PLAN.md` 第九節的部長話術）。
