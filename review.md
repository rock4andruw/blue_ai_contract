請你以「Claude Code 工作流架構顧問」的角度，升級這台電腦的 Claude Code 開發 Harness（工作流防閉環迭代機制）。
你是 Opus 4.8。你的終極任務只有一個：【將高階判斷力與架構思維，外化為可長期沿用的制度與實體檔案，讓後續的較弱模型（Sonnet、Haiku）能在此框架下穩定自主產出。】
請注意：本 session 的核心是「立制度與防錯機制」，不要拿去執行日常開發任務。

---

### ✅ 前期診斷結果（已由 Fable 5 於 2026-07-03 唯讀掃描逐項驗證）

**以下事實直接引用，不要重新掃描環境、不要重新驗證**——省下的 context 全部用於產出交付項。只有在你要修改某個檔案的當下，才讀取該檔案的現況。

#### 1. 全域 `~/.claude/settings.json`（三大問題確認）
- `model` 釘選在 `"claude-fable-5[1m]"`，不處理則每個新 session 都用最貴模型。
- `permissions.allow` 共 53 條，約 40 條是他專案（ntub 論文、CSV/SLP、supabase/google-genai 評測等）遺留。其中等同「任意程式碼免詢問執行」的危險條目：`Bash(python3)`、`Bash(python3 -)`、`Bash(python3 -c ' *)`、`Bash(pip install *)`。
- 完全沒有 `deny` 規則：`.env`（專案根目錄存在，55 bytes，含 API key）與 `pic_contract/`（真實公司合約 DOCX）無任何讀取保護。
- 沒有任何 hooks；沒有 `~/.claude/settings.local.json`；本專案沒有 `.claude/settings.json`（`.claude/` 下只有 `skills/`）；沒有 `.mcp.json`；`.git/hooks/` 只有 sample 檔。

#### 2. Skills 雙重身分問題（重大、原任務書未列）
- `.claude/skills/` 下有 5 個**平面 `.md` 檔**：`contract-diff.md`、`contract-risk-analysis.md`、`negotiation-strategy.md`、`report-writing.md`、`frontend-design.md`。
- Claude Code 只載入 `<name>/SKILL.md` 目錄格式，因此**這 5 個 skill 全部沒有被載入**，`/contract-diff` 等指令實際上不存在（已在 live session 確認可用 skill 清單中沒有它們）。
- 但 `src/` 有 4 處在 **runtime 讀取這些檔案當 prompt 資產**：`src/services/contract/negotiate_service.py:146`、`mas_service.py:35`、`llm_service.py:91`、`verifier.py:139`（皆為 `_SKILLS_DIR = ... / ".claude" / "skills"`）。任何搬移或改格式，必須同步更新這 4 處並實跑驗證，否則會弄壞產品程式碼。

#### 3. Context 重複（token 漏水主因）
根目錄同時存在：`CLAUDE.md`(415 行) + `PROJECT_CONTEXT.md`(210) + `PROJECT_PLAN.md`(317) + `SESSION_CONTEXT_20260627/0701/0702.md`(共 385) + `next_step_plan.md`(169) + `專案.md`(252) + `README.md`(264)，合計約 2200 行高度重疊的專案脈絡。

#### 4. CLAUDE.md 陳腐內容
- 「目錄結構規範」與現實不符（實際上沒有 `tests/`、`deploy/`、`scripts/`；`frontend/` 只有一個 `demo.html`）。
- 殘留其他專案的錯誤範例（錯誤格式範例寫「音訊檔案格式不支援」）。
- 過時模型名（`claude-sonnet-4-6`、`claude-opus-4-7`）、佔位聯絡資訊（`[PM Name]`）。

---

### ⚙️ 作業規則（請嚴格遵守執行節奏）

1. **開場必問三題，等我回覆一次後進入全自主作業，不再停下來等待回覆**：
   - Q1 全域 `model` 欄位：直接移除（建議，之後用 `/model` 隨切）／釘選 `sonnet`／釘選 `opus`？
   - Q2 他專案的 allow 遺留條目：全部刪除（建議，之後在該專案會重新被詢問一次）／遷移到 `/Users/andruw/Documents/ntub/.claude/settings.json`？
   - Q3 Skills 修復方式：轉成 `<name>/SKILL.md` 正式格式並同步修改上述 4 處 src 路徑＋實跑驗證（建議）／維持現狀只在文件標註「僅為 runtime prompt 資產」／複製一份成正式格式（缺點：兩份會漂移）？
   - 若你發現其他真正需要 User 決定的事項，可追加至多 2 題一起問。其餘不確定之處寫成明確假設列在診斷書開頭。
2. **骨架先行＋隨做隨寫**：此任務極度消耗 context。先將所有交付檔案「建立骨架目錄與結構定義說明」落檔，確保 session 意外中斷時大框架依然完整。隨後依價值排序逐一填實，完成一項立刻 Write to disk，不可堆積在 buffer。
3. **備份與指引原則**：修改既有檔案前必須建立 `.bak` 副本。新規則一律獨立成檔，統一放在 `docs/harness/` 目錄下（交付項 A–G 除 CLAUDE.md 外皆是），CLAUDE.md 僅作為高效的「路由中心」指向各別說明檔。
4. **弱模型面向**：你的讀者是 Sonnet 與 Haiku。請提供「具體、具備明確判準（Rubric）、有輸入輸出範例」的規則。禁止使用「保持高品質」等自由心證的抽象詞彙。所有設計必須在 Sonnet 等級就能流暢執行。
5. **語言**：所有交付文件使用繁體中文（程式碼、設定檔、路徑除外）。
6. 全力運作：請開啟最高 Effort 模式。

---

### 📋 交付清單（按價值與執行優先級排序）

#### A. Harness 漏水診斷書（`docs/harness/A_diagnosis.md`）

以上方「前期診斷結果」為基礎，精準指出當前工作流中「最浪費 Token、最容易導致模型失焦、最常引發工具/MCP/Skills 調用錯誤」的前三個痛點，並給出**機制級的阻斷方案**——意即用 hooks、permissions（allow/deny 規則）、scripts、git hooks 等系統機制強制執行，而不是寫在文件裡期望模型自覺遵守；每個方案需標明用哪個機制實作。這份先寫，供後面所有產出引用。

診斷書完成落檔後，**立即實際修復全域與專案 settings**（依 Q1/Q2 的回覆執行）：
- 處理 `model` 欄位；清理 allow-list，把本專案需要的權限移至本專案 `.claude/settings.json`；
- 加入 deny 規則保護 `.env`、`.env.*`、`pic_contract/**`、`nda_contract/**`、`sla_contract/**`（後三者為真實合約，先確認再納入）；
- 修改前備份 `~/.claude/settings.json` 為 `.bak`；修改後用 `python3 -m json.tool` 驗證 JSON 合法。

#### B. 重寫 CLAUDE.md

重新梳理專案主入口文件。遵循「弱模型需要明確、強模型需要留白」的原則。收斂重複規則，移除上方列出的過時資訊，將長內容抽離至獨立檔案，CLAUDE.md 只留核心架構與檔案路由。同時處理根目錄 context 重複：過時的 SESSION_CONTEXT、舊計畫檔移入 `archive/`（User 已知偏好 archive 而非刪除）。

#### C. 模型調度與動態升降級守則（`docs/harness/C_model_dispatch.md`）

針對弱模型的指揮官系統（Agent/Subagent）建立調度合約：

- 派工三件套：任何 Subagent 的指派必須包含「明確目標與背景、嚴格的驗收條件、標準回報格式（成果路徑與關鍵行號，禁止噴出大段代碼）」。
- 異常升降級路徑：小模型（Haiku）工具或語法錯誤 1 次直接升級至 Sonnet；中階模型（Sonnet）同一子任務連錯 2 次，必須帶上完整失敗軌跡升級至 Opus 4.8；當高階模型解出固定模式後，降回便宜模型批次套用。同一件事最多重試兩輪。實作機制：以 Agent tool 的 `model` 參數（`haiku`/`sonnet`/`opus`）指定 subagent 模型，升級時在新 Agent 的 prompt 中附上前次的失敗軌跡。
- 隔離驗證：負責實作的 Agent 不得自我驗證。驗收必須指派「Fresh-Context Subagent」，透過 read-back 重新讀檔、實跑測試測資、或引入多樣本評審（Multi-agent debate）選優。

#### D. 判斷力外化矩陣（`docs/harness/D_judgment_matrix.md`）

將高階模型的直覺，量化為弱模型可肉眼比對的檢核表（Checklist）。每條判準必須附帶一個【完美正例】與【典型反例】。至少涵蓋：

- 什麼樣的信號代表「方向完全錯了，應該立刻停下換路徑」，而非在錯誤的代碼上原地重試？
- 滿足何種量化條件，才算任務「真正完成」可交付？
- 何時該觸發熔斷機制，停止自主作業並向 User 提問？

#### E. 標準化派工 Prompt 模板（`docs/harness/E_dispatch_templates.md`）

提供給未來主模型直接套用的委派模板（含 Context 引入語法、驗收條件框架、回報格式填空）。針對常見任務型態各提供一份：搜尋研究、功能實作、代碼重構、代碼審查。

#### F. 知識迭代與反思協議（`docs/harness/F_reflection_protocol.md`）

定義未來的弱模型如何安全地自我更新這套 Harness 檔案。哪些規則文件模型可自行優化更新（如：踩坑後的教訓紀錄），哪些動之前必須先徵得 User 同意？踩坑紀錄的寫入格式為何？累積到多長時必須自動觸發精簡與概念抽象化？

#### G. 給未來 Session 的交接信（`docs/harness/G_handover.md`）

三件 User 沒問、但你認為對這個開發環境與工作流最關鍵的事。並指出這套制度在弱模型長期運作下，最可能出現的「退化/腐化方式」以及如何預防。

---

### 🏁 收尾與合規驗證（強制執行）

1. 對抗審查：文件落檔後，立刻開啟一個 fresh-context subagent 扮演「挑剔的審查員」，全面掃描這套 harness 檔案，揪出規則衝突、路徑錯誤、或是弱模型會誤讀的模糊語句。修正以 2 輪為上限，第 2 輪後仍殘留的問題寫入交接信（交付項 G），不再迭代。
2. 唯讀驗證：使用工具重新 read-back 讀取所有落地檔案，確保沒有截斷、內容完整。若 Q3 選擇修改 src 路徑，必須實跑（如 `python3 -c "from src.services.contract import negotiate_service"` 或既有測試）證明 4 處 loader 仍正常。
3. 執行摘要：在主對話中提供一頁總結：你具體建立/修改了哪些檔案、核心架構邏輯、以及 User 明天開始與弱模型協作時，該如何啟動這套 Harness。
4. 熔斷控 Token：若發現 Context Window 即將耗盡，請立刻停下手上的產出，先完成收尾前三步，把未完成項目寫進「給未來 session 的信」交接。

### ⚖️ 誠實條款

請在診斷書中明確標記這套 Harness 的能力極限。利用拆解與隔離驗證可以逼近高階品質，但遇到「模糊的商業美感、品味決策」時弱模型注定失敗。請寫明當弱模型遇到這類極限時的具體應對標準。不確定的事就查，查不到就標註，不要編造。
