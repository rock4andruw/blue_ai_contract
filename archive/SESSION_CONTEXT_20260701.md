# Session 說明檔：2026-07-01 工作紀錄

> 讀完這份文件，新的 AI session 可以立刻接續工作，不需要重新說明背景。
> 系統完整說明請見 PROJECT_CONTEXT.md。上一份 Session 紀錄見 `SESSION_CONTEXT_20260627.md`。

---

## 本次 Session 完成的工作

### 1. Verification Agent 正式實作（Layer 2）

- 新增 `src/services/contract/verifier.py`：`VerificationAgent` 類別 + `cross_check_risks()` 交叉核對邏輯
- 接入 `orchestrator.py` Step 4b（規則引擎之後、LLM 摘要之前）
- 新增候選規則紀錄機制 `candidate_rules.jsonl`：Case C 補漏旗標不自動生成規則（風險太高），改為累積紀錄＋分類猜測，供人工判斷「哪類該升級成正式規則」
- 詳細設計差異記錄於 `docs/specs/verification_agent_spec.md` 第十一節

### 2. 真實公司合約測試（第一次）

拿到 3 組真實公司合約並完整跑過 pipeline：
- `pic_contract/PIC版-軟體維護服務合約.docx` vs 乙方修改版
- `pic_contract/PIC版-軟體採購合約.docx` vs 乙方修改版
- `pic_contract/PIC版-保密暨智慧財產權協議書(單務).docx` vs 乙方修改版

發現的關鍵案例（可直接用於 Demo 敘事）：

| 案例 | 問題 | 狀態 |
| --- | --- | --- |
| 遲延罰款費率 0.3% → 千分之一 | Regex 看不懂中文分數寫法，規則引擎完全看不到這個變化 | ✅ 已修（`_extract_rate_percentage` 支援千分之/百分之/萬分之） |
| 採購合約 138 段條款被靜默丟棄 | 純新增/刪除條款沒有可辨識條號時被直接跳過，不進入 diffs | ✅ 已修（補上 title fallback） |
| 責任上限 50% → 30% | 原本誤判理由（跟未變的上限混在一起判斷），現在精準抓到真正變化的數字 | ✅ 已修 |
| 全形／半形 % 符號混用（％ vs %） | 合約常混用兩種符號，原本只認半形 | ✅ 已修 |
| 回應/到場/修復三個時限共用一句話 | 只抓到第一個時限，其他改變被忽略（例：修復 2日→5日 完全偵測不到） | ✅ 已修（`_extract_scoped_hours` 三者獨立比對） |
| 付款條款被誤判成回應時間拉長 60 倍 | 上一項修復時自己引入的 fallback 太寬鬆，「發票處理」誤觸發 | ✅ 已修（移除通用 fallback） |

### 3. 已知但決定不修的問題（有紀錄、非遺忘）

- **12/14 條 Risk Engine 規則的風險等級是寫死的**（不看變化幅度），只有 SLA 可用率、回應時間兩條規則有動態門檻。已記錄，優先度低於涵蓋率問題。
- **`rule_sla_degrade` 有沒有跟費率/上限一樣的「一句多個百分比互相干擾」問題**——沒有真實合約可測試（3 份都沒有可用率條款），只能合成測試，暫不處理。
- **Verification Agent 交叉核對邏輯（Case A/B/C）只比對 clause_id，沒比對風險內容**：同一條款有兩個不同風險維度時，Agent 抓到的第二個風險會被誤判成「已審查過」而丟棄。**這是真正的邏輯漏洞**，優先度最高，但這次決定先不修，因為評估後認為黑客松時程不適合繼續深挖規則細節。
- **Case A 直接丟棄 Agent 的判斷**，即使 Agent 講得更準確（今天親眼證實過規則引擎「觸發正確、理由講錯」的案例）。
- **Verification Agent 非決定性**：同一份合約重跑，Case C 補漏數量會浮動（6～8 項間），使用者不會知道這次跑的覆蓋率信心水準。

### 4. Layer 4 路線圖確認（pgvector + Taiwan Law MCP）

討論並確認：**不現場 demo，只用口頭路線圖帶過**。

- 定位：接在協商建議生成（Step 5）之前，補上「LLM 建議完全沒有法律依據」這個今天發現的缺口
- pgvector：語意檢索相似案例（CUAD 標註集 + 未來的內部案例庫）
- MCP Taiwan Law：即時查詢民法條文（例如民法252條違約金酌減），讓協商建議能引用真實法條
- **不用 CUAD 或假資料做 demo**：CUAD 是英文美國合約，跟繁中台灣合約產品定位不符，用了反而降低說服力
- **真實公司合約不能整批放進資料庫**：機密性 + 資料治理問題，這也是不現場建置 Layer 4 的原因之一

### 5. 文件更新

- `docs/specs/verification_agent_spec.md`：狀態改為「已實作」，新增第十一節「實作差異與待辦」
- `next_step_plan.md`：更新已完成項目、修正「不做的」清單中 Taiwan Law MCP 的說明、更新評審主攻話術

---

## 三大問題框架（這次 Session 建立的思考方式）

跟使用者討論出的優先順序框架，適用於評估任何一個新發現的問題該不該修：

1. **合約差異有沒有辦法找到**（Step 1-3：解析/對齊/差異）——不可逆的核心風險，系統沒看到 = 法務根本沒機會人工複核。**今天投入最多，處理得最完整。**
2. **風險怎麼判定，標準在哪裡**（Step 4 規則引擎 + Step 4b Verification Agent）——精準度問題，就算判錯還是會出現在報告裡，法務仍看得到。**今天處理了具體 bug，但嚴重度分級、Agent 交叉核對邏輯還有已知缺口未修。**
3. **建議怎麼判定，標準在哪裡**（Step 5 協商建議生成）——**整場完全沒審查過內容本身**，只知道架構，不知道 LLM 生成的協商建議品質好不好、有沒有幻覺。這是下次該優先看的空白。

**黑客松現實考量**：評審看的是 Demo 說不說得動人，不是規則引擎有沒有 100% 正確。今天這整個「發現漏洞→修復→驗證→又發現自己修復引入新漏洞→再修」的過程，本身就是很強的敘事素材（誠實 + 自我修正的系統），比追求零瑕疵更有價值。

---

## 待完成工作（優先順序，更新版）

| 優先度 | 工作 | 備註 |
| --- | --- | --- |
| 🔴 高 | Demo 敘事整理（千分之一、138 段修復、50%→30%、自我修正假警報） | 素材已備齊，需要整理成講稿 |
| 🔴 高 | 讀一遍已產生的協商建議文字，確認沒有明顯幻覺 | 問題 3 的最低限度把關，不用系統性稽核 |
| 🟡 中 | NDA 保密期縮短規則（5年→2年）用真實合約驗證 | 手上這份 NDA 沒有這個變化，無法驗證 |
| 🟡 中 | DOCX 格式支援改善、邊界測試、壓測 | 沿用 next_step_plan.md 週次 2 排程 |
| 🟢 低 | Verification Agent Case A/B/C 比對邏輯改成看風險維度而非只看 clause_id | 已知邏輯漏洞，暫緩 |
| 🟢 低 | 12 條規則的風險等級動態化 | 已發現，暫緩 |
| ⚪ 路線圖 | pgvector + Taiwan Law MCP（Layer 4） | 只做口頭簡報，不建置 |

---

## 重要文件索引（更新）

| 文件 | 用途 |
| --- | --- |
| `SESSION_CONTEXT_20260701.md` | 本文件，今天的完整紀錄 |
| `SESSION_CONTEXT_20260627.md` | 上次 Session 紀錄（Verification Agent 設計、論文計畫） |
| `docs/specs/verification_agent_spec.md` | Verification Agent 設計規格 + 實作紀錄（第十一節） |
| `next_step_plan.md` | 任務清單，已更新至 2026-07-01 |
| `PROJECT_PLAN.md` | 對外簡報用的專案說明（尚未反映今天的 Verification Agent 進度，可視需要更新） |
| `pic_contract/` | 3 組真實公司合約（PIC 版 + 乙方修改版），今天的測試資料 |
| `candidate_rules.jsonl` | Case C 補漏候選規則紀錄（今天新增的機制產出） |

---

## 程式碼改動清單（本次 Session）

- **新增**：`src/services/contract/verifier.py`
- **修改**：`src/services/contract/orchestrator.py`（Step 4b 插入、既有 `max_sections` bug 順便修掉）
- **修改**：`src/services/contract/schemas.py`（新增 `RISK_AGENT_AUDITED` 風險代碼）
- **修改**：`src/services/contract/report_generator.py`（完整旗標表格加「來源」欄）
- **修改**：`src/services/contract/diff_engine.py`（純新增/刪除條款補上 title fallback）
- **修改**：`src/services/contract/risk_engine.py`（中文分數解析、情境限定的費率/上限/時限抽取、移除誤觸發的 fallback）

三份真實合約回歸測試皆通過，尚未 commit（等使用者確認後執行）。

---

*Session 日期：2026-07-01 ｜ Blue-AI Team*
