# 脫敏系統規劃（Phase 2，賽後實作）

**文件版本**：3.1（2026-07-10）——v1.0 抗辯 1/3 存活擋回；v2.0 抗辯 1/3 存活再擋回（致命：Ask 回送迴路）；v3.0 第三輪抗辯 red-team 抓到回送契約缺強制機制（REFUTED）、simplifier 存活，本版納入修正後依 User 決定收尾（skeptic 第三輪未執行，見 §9），記錄見 §9
**狀態**：規劃中——依 `next_step_plan.md`「不做（賽前）」原則，全部項目賽後才動工
**對應承諾**：`presenter_script_hackathon.md` Infra 部長段落的「事前遮蔽＋事後恢復」Phase 2 規劃
**工具選型異動**：Presidio 已移除（v2）、LiteLLM Proxy 降級為 SaaS 化選項（v2）、nonce 佔位符已移除（v3）。檔名保留避免斷鏈

---

## 0. 假設與信任邊界

| # | 假設 | 狀態 |
|---|------|------|
| A1 | **需要可逆還原**，且**信任邊界明確化（v3）**：client（法務的瀏覽器）被信任持有真名——原始合約本來就是他上傳的，mapping 交給 client 不新增任何暴露類別 | v3 核心設計依據 |
| A2 | **金額預設不遮**：金額量級是 LLM 端重大性判斷素材 | 嚴格模式已刪（YAGNI，v2） |

**防護對象誠實聲明（v3.1）**：這套脫敏防的是 **LLM 供應商端**（訓練使用、日誌留存、供應商員工存取）——不防傳輸通道（TLS 已處理）、不防 client 端（A1 信任邊界內，法務本來就持有原始合約）。mapping 隨 response 交付與直接送真名在傳輸面資訊等價，這不是漏洞，是設計聲明。

---

## 1. 選擇性脫敏政策：遮「身分」、留「條件」

**架構事實**：遮蔽只發生在 LLM 出口；規則引擎（`risk_engine.py` 14 條規則）全程在本地處理未遮蔽原文，不受影響。「留數字」的理由全在 LLM 端：

- Verifier 語意補漏要算「0.3% → 千分之一 = 降 66.7%」數值換算
- MAS 重大性判斷需要金額與期間量級
- 協商對策要產出可貼入合約的具體條文
- Embedding 檢索的語意向量不被數字遮蔽扭曲

| 類別 | 處理 | 理由 |
|------|------|------|
| 公司名稱（甲乙方全名/簡稱） | **必遮** | 商業關係本身是機密 |
| 自然人姓名 | **必遮** | 個資法 |
| 統一編號、身分證字號 | **必遮** | 可直接反查身分 |
| 電話、Email、地址 | **必遮** | 個資法 |
| 百分比、期間、金額 | **保留** | LLM 端風險判斷必要素材（A2） |

---

## 2. 出口盤點：產品碼 12 個 + 非產品碼側門

### 產品碼出口（12 個，行號依 2026-07-10 代碼查證）

| 模組 | 行號 | 送出內容 | 收方 |
|------|------|----------|------|
| `verifier.py` | 211 / 229 | 全部變動條款原文 | Gemini / Claude |
| `llm_service.py` | 202 / 238 | 單一風險條款原文 + 法條 + 先例 | Gemini / Claude |
| `llm_service.py`（Ask） | 559 / 577 | 報告 key_changes + 使用者問題 | Gemini / Claude |
| `mas_service.py` | 115 / 129 | 單一高風險條款原文 ×2 | Gemini / Claude |
| `negotiate_service.py` | 248 / 267 | 條款新舊原文 | Gemini / Claude |
| `precedent_corpus.py` | 125 / 162 | trigger_reason／case_summary（embedding） | Gemini |

### 回送迴路（v3 新增——v2 兩輪抗辯的致命發現）

`/ask`、`/negotiate`、`/negotiate/matrix` 三個端點的 key_changes/條款文字**由前端送回**（`demo.html:1651,1687` → `contracts.py`）。若前端持有的是真名版，回送後 server 端「重新偵測再遮」**結構性失效**——公司簡稱的唯一偵測機制是「以下簡稱」定義句抽取，定義句只存在於合約開頭原文，**不存在於報告摘要文字**。→ 解法不是修偵測，是**讓回送內容本來就是遮蔽版**（§3/§5）。

### 非產品碼側門

- `docs/planning/exp1_pure_llm_baseline.py:58` 直送合約原文給 Gemini；此類實驗腳本會增生
- **規範**：實驗腳本一律 (a) 只用合成資料，或 (b) 改 import `llm_client`（自動經 sanitizer）；CI 規則（§3）涵蓋 `docs/planning/*.py`

### 相鄰風險（另案記錄）

`contracts.py:197-203` `NamedTemporaryFile(delete=False)` 把上傳合約明文寫 /tmp，process kill 時殘留。脫敏管不到 parse 前，另案處理。

---

## 3. 架構（v3）：server 全程只說遮蔽版，呈現邊界移到前端

### Step 1：統一 LLM 呼叫層（純重構，0.5-1 天）

新增 `src/services/contract/llm_client.py`：`chat(model=...)` 與 `embed()` 兩個函式，收斂 12 個出口的 10 份重複雙軌樣板。**必須開放 model 參數**（實驗腳本用非產品預設模型，否則收編不進 CI 規則）。注入點 12 → 2。

### Step 2：sanitizer 掛 chokepoint + 前端呈現邊界（v3 重設計）

```
compare request：
  合約原文 →（本地 parse/rule engine 用原文）→ 組裝 prompt → mask()【整串】→ llm_client → LLM
  API response = 遮蔽版 key_changes + markdown + mapping ──TLS──→ 前端

前端（信任邊界內，A1）：
  顯示時用 mapping 做字串替換（真名呈現）≈20 行 JS
  回送 /ask、/negotiate、/matrix 時送「遮蔽版」key_changes（機器往返永遠是遮蔽版）
  使用者輸入的問題：送出前用 mapping 已知實體做 replaceAll（真名→佔位符）
  下載 Markdown：前端替換後才下載（檔案含真名 = A1 預期行為）
```

- **Server 永不 unmask**：後端從 LLM 回應到 API response 全程持有遮蔽版，「呈現邊界」就是瀏覽器。這一刀同時解決：回送迴路（回送的本來就是遮蔽版，`/ask`/`/matrix` 的 outbound 天然乾淨）、unmask 單一邊界的實作歧義（server 端根本沒有 unmask 這個操作）
- **回送完整性驗證（v3.1，機制不是自律——第三輪 red-team 抓到 server 沒有 mapping、原理上驗不了回送內容是不是遮蔽版）**：compare 時對遮蔽版 key_changes 附 **HMAC 簽章**（key 走環境變數），`/ask`、`/negotiate`、`/matrix` 要求原樣回送並驗簽——內容被改動或無簽即拒。約十行、無狀態、多實例安全。回送內容被機制性釘死為「server 自己產出的遮蔽版」；使用者問題（自由文字）不在簽章範圍，維持 §3 殘餘風險聲明
- **mapping 隨 response 交付 client、server 側即棄**：與真名文字走同一條 TLS 通道，資訊等價、無新暴露類別（見 §0 防護對象聲明）；server 端無狀態、無快取、多實例天然安全。帶 mapping 的 response 一律 `Cache-Control: no-store`（防企業 proxy 快取）
- **前端實作鐵律（v3.1）**：(a) 持有的 `key_changes` 狀態**必須保持遮蔽版**——unmask 只發生在「渲染字串」層或維持雙副本，就地改寫狀態物件 = 之後每次回送都是真名、整個設計靜默失效；(b) 顯示替換用**單一 helper** 統一，渲染路徑實際有**五處**（compare 報告、Ask 回答、協商對策、協商矩陣、Markdown 下載），不是三處；(c) mapping 與 key_changes 綁同一 report 物件（含 report_id），替換時驗 id——防同分頁殘留舊 UI 配新 mapping 顯示「換錯的真名」（完整性事故：法務拿著錯的公司名去談判）；(d) mapping **只存 JS 記憶體變數**，禁止 localStorage/sessionStorage/service-worker cache（法務共用機情境）；(e) 問題預替換用 literal `String.replaceAll`（不用 `new RegExp`——公司名含「（股）」「+」「.」等特殊字元會炸或錯替）、mapping 條目依長度降冪替換（防「⟦ORG_1⟧/⟦ORG_11⟧」型前綴歧義——完整 token 含右括號本無此問題，長名優先是雙保險）、替換失敗 fail-closed 不送出
- **前端安全基線（v3.1 前置條件）**：v3 把 DOM 升格為呈現邊界，但 `demo.html:1372`（missing_fragments 未過 escHtml 直插 innerHTML——該欄位是 parser 吃不掉的**合約原文片段**，合約來自對造=不可信輸入）與 `:1393`（檔名未跳脫）存在 XSS 注入點。實作脫敏前必須先修：全欄位 escHtml + 基本 CSP。此為前置條件，不是選配
- **mask 對象是組裝完成的整串 outbound prompt**（title/clause_id/trigger_reason 都可能含實體）；prompt 模板本身不得含實體樣式的示例文字（如「例：○○股份有限公司」會被誤遮）
- **fail-closed 硬性要求**：`mask()` 拋任何例外 → 拒送並回錯誤，禁止 fallback 照送原文。本 codebase 慣例是 `except → fallback 繼續跑`（`llm_service.py:211-214` 等 4 處），sanitizer 是明確例外，review checklist 必查
- **機制級強制**：CI 檢查禁止 `llm_client.py` 以外呼叫 LLM SDK。**字面規則必須涵蓋 `from google import genai` 形式**——現有 12 處 import 全部是這個寫法，`import google.genai` 的 grep 會 100% 漏接（抗辯第二輪發現）；用 AST 檢查或雙形式 regex

### 殘餘風險（誠實標注）

使用者在問題框自行輸入 mapping 沒有的實體變體（自創簡稱、英文縮寫）→ 前端 replaceAll 抓不到，隨問題送出。與「合約內變體簡稱漏抓」同類，靠 DPA 兜底；量級小（問題框是短文字，非整份合約）。

### LiteLLM Proxy：SaaS 化階段選項（非既定路徑）

效益 = 多服務共用閘道、集中 key 管理、spend tracking。前置條件：系統穩定性不受限單次 Demo + **Proxy 自身安全基線**（LiteLLM 歷史 CVE 頻繁；集中持有全部 key + 明文流量，是高價值標的）。

---

## 4. 辨識器（純自寫，估 100-150 行，零新依賴）

| 實體 | 方法 | 可靠度 |
|------|------|--------|
| 統一編號 | regex `\d{8}` + 上下文詞 | 高 |
| 身分證字號 | regex `[A-Z][12]\d{8}` | 高 |
| 電話/Email | regex（台灣格式） | 高 |
| 公司名稱 | 後綴規則 +「以下簡稱」定義句抽取（合約開頭必有甲乙方定義句） | 中高（**自評無量測依據，PoC 必測**） |
| 中文人名 | 獨立 PoC：ckiptagger（TF1 時代專案、模型散佈通道非正規，供應鏈風險計入）或 spacy zh；量測漏抓率後決定 | 低——最大不確定點 |

**未驗證假設**：定義句覆蓋率——正文用未定義變體簡稱、英文縮寫、第三方公司名（無定義句）都抓不到；殘餘靠 DPA 兜底（脫敏是疊加保護，不取代 DPA）。

**佔位符格式（v3：固定格式，nonce 已移除）**：

- 格式：`⟦ORG_1⟧`（罕見 Unicode 括號，**無隨機後綴**）
- 防注入：mask 前**預掃描剝除**輸入中任何 `⟦…⟧` pattern（一行 regex，確定性）——剝除後固定格式即不可偽造，惡意合約預埋佔位符失效
- v2 的 per-request nonce 被第二輪抗辯雙殺：(a) 三個威脅場景（預埋/幻覺編號/跨請求碰撞）在預掃描 + 單一 mapping 不變量下 nonce 皆無增量防護；(b) nonce 與 embedding 語料一致性互斥（corpus 佔位符帶建庫 nonce、query 帶當次 nonce，字面永不相同）；(c) 隨機尾碼增加 token 成本與 LLM 變形殘留率——放大它自己要解的問題
- 不採「parser 入口無差別剝角括號」替代方案：PDF 全文剝 `<[^>]+>` 可能誤傷正文（如「單價<100萬>」）

---

## 5. mapping 生命週期（v3 不變量）

1. **單一 mapping per compare request**：request 內全部 LLM 呼叫共用（同一實體全程同一佔位符，跨呼叫指涉一致）
2. **Server 永不 unmask**：後端全程持有並回傳遮蔽版；mapping 隨 response 交付 client 後 server 側即棄（不寫檔/log/DB/快取）
3. **回送通道只接受遮蔽版**：`/ask`、`/negotiate`、`/matrix` 的輸入契約 = 遮蔽版 key_changes；前端負責顯示替換與問題預替換（§3）
4. **落地面全遮**：`log_candidate_rule`（`verifier.py:98-116`）三個欄位——`evidence_text`、`trigger_reason` 因不變量 2 自然是遮蔽版；`contract_pair`（= 上傳檔名，常含公司名）**不經 prompt 主流程，需單獨過 mask**
5. **殘留處理**：前端替換後掃描 `⟦` **單字元**（LLM 斷詞可能吃掉右括號，掃完整 pattern 會漏）；發現殘留 → 該欄位附警示標記 + 計數告警（log 不含敏感內容），不靜默出貨、不整請求失敗——殘留是「過度遮蔽」方向的品質缺陷（使用者看到佔位符），不是洩漏事件，fail-closed 反而讓 LLM 幻覺編號變成 DoS 面

---

## 6. 驗收條件（v3，全 fail-then-pass）

> v1 的「gold set recall 不退化」驗收是恆真測試已廢棄（`evaluate.py` 只跑本地規則引擎，零 LLM 呼叫，遮蔽影響不到它）。

1. **零外洩 + fail-closed + 回送完整性（v3.1 擴充）**：植入實體合成合約（公司名×2 含簡稱、統編、人名、電話、email、含公司名檔名），在 `llm_client` chokepoint 攔截全部 outbound payload 斷言 0 實體；**必須涵蓋回送流程**（compare → 取遮蔽版 key_changes → 打 /ask 與 /matrix → 斷言這兩個出口的 outbound 也 0 實體）；強制 sanitizer 拋錯，斷言請求被拒、無 payload 送出；**篡改回送測試**——竄改 key_changes 內容或拔掉簽章後打回送端點，斷言被拒（HMAC 機制生效）
2. **LLM 端品質不退化（v3.1 修訂基線來源）**：
   - 基線：**以現行程式碼重跑 v2-v6 各 1 次**（5 趟，經 `/compare/example` 取 JSON）——v3.0 原寫「沿用既有 demo 產出」，但 repo 內無機器可讀的 JSON 基線工件，沿用需寫 markdown 反解析工具且基線混入程式碼演進雜訊，重跑反而總複雜度更低（simplifier 第三輪查證）；遮蔽側跑 3 次、只跑受影響的 LLM 階段（verifier/MAS/摘要）——共約 20 趟
   - **比對單位**：`(clause_id, 風險類別, risk_level)` 三元組
   - **判定規則（寫死，不留人工裁量）**：遮蔽側 3 次中 ≥2 次出現的高風險發現集合，必須 ⊇ 基線高風險發現集合；違反即 FAIL
   - Embedding：先例語料庫是合成資料（無敏感實體，無需重建），量測「遮蔽 query 的 top-1 先例一致率」，< 80% 即檢討佔位符對 query 向量的影響
3. **前端還原正確**：報告/UI/下載 Markdown 顯示真名；`⟦` 殘留掃描 = 0
4. **mapping 不落地（範圍限定）**：測試期間對**專案目錄 + /tmp** 做檔案系統快照 diff，新增/修改檔案 grep 斷言不含 mapping 與真實實體；code review 確認 sanitizer 無 log 輸出
5. **延遲**：單請求額外開銷 < 2 秒（純 regex 預期 < 100ms）

---

## 7. 風險與對策（v3）

| 風險 | 等級 | 對策 |
|------|------|------|
| fail-open 實作慣性（codebase 慣例 except→fallback） | **高** | §3 硬性 fail-closed + 驗收 1 強制拋錯 + review checklist |
| 前端就地 unmask 使回送靜默失效（v3.1） | **高** | §3 前端鐵律 (a) 雙副本 + HMAC 驗簽兜底（就地改寫後簽章即失效，驗收 1 篡改測試可抓） |
| demo.html 既有 XSS（DOM 升格為呈現邊界的前置缺陷，v3.1） | 高 | §3 前端安全基線列為實作前置條件 |
| 常見詞公司簡稱誤替換使用者問題（如簡稱恰為普通名詞，v3.1） | 低 | 品質問題非洩漏（過度遮蔽方向）；殘留掃描與警示涵蓋 |
| 中文人名 NER 漏抓 | 高 | 規則優先；PoC 量測；殘餘 DPA 兜底 |
| 簡稱/第三方公司名漏抓（定義句覆蓋率無量測依據） | 高 | PoC 必測；量測後更新本表 |
| 使用者問題含 mapping 外變體實體（v3 新增） | 中 | 前端已知實體 replaceAll；殘餘量級小（短文字），DPA 兜底 |
| 佔位符變形殘留 | 中 | §5 `⟦` 單字元掃描 + 警示；驗收 2 順帶量測殘留率 |
| Embedding query 漂移 | 中 | 驗收 2 專測（語料庫為合成資料無需重建） |
| 實驗腳本側門增生 | 中 | §2 規範 + CI 規則（AST/雙形式，涵蓋 `from google import genai`） |
| /tmp 明文殘留 | 相鄰另案 | §2 記錄，與脫敏解耦 |
| LiteLLM Proxy 供應鏈（僅選項成立時） | 低 | §3 安全基線前置條件 |

---

## 8. 分期時程（賽後啟動，v3 依抗辯上修）

| 階段 | 內容 | 估時 |
|------|------|------|
| 重構 | `llm_client.py`（12 出口 → 2 chokepoint，開 model 參數）+ 回歸測試 | 0.5-1 天 |
| 脫敏 | `sanitizer.py` + chokepoint 接入 + 前端呈現邊界（顯示替換/回送遮蔽版/問題預替換 ≈20-40 行 JS）+ CI 規則 | 1.5-2 天 |
| 驗收 | §6 全部 5 條（含回送流程攔截、等價比對工具、快照 harness）+ `candidate_rules` 檔名遮蔽 | 2-3 天 |
| 人名 PoC | ckiptagger vs spacy 漏抓率量測（可並行） | 1 天 |
| **合計** | | **5-7 天**（v1 估 3-5 天，經兩輪抗辯補需求後上修） |
| 2b（選項） | LiteLLM Proxy（SaaS 化多團隊時，含安全基線評估） | 另計 |

---

## 9. 抗辯記錄（loop-until-dry，資料安全類重大結論）

### 第一輪（v1.0 → 擋回，1/3 存活）

| 鏡頭 | 裁決 | 採納的修正 |
|------|------|-----------|
| skeptic | REFUTED | 驗收恆真測試廢棄重設計；§1 論證改純 LLM 端理由；補實驗腳本側門 |
| red-team | SURVIVED（4 必修） | fail-closed 硬性化；candidate_rules 三欄位+檔名；佔位符防注入；mask 整串 prompt |
| simplifier | REFUTED | Presidio 移除；先重構 chokepoint；LiteLLM 降級；嚴格模式刪除 |

### 第二輪（v2.0 → 擋回，1/3 存活）

| 鏡頭 | 裁決 | 採納的修正 |
|------|------|-----------|
| skeptic | REFUTED | **Ask/matrix 回送迴路致命洞**（簡稱偵測前提在回送路徑不成立）→ v3 §3/§5 呈現邊界移前端、回送只走遮蔽版；nonce 與 embedding 補救互斥 → nonce 移除；驗收 2 判定規則寫死；時程上修 5-7 天 |
| red-team | REFUTED | 同上回送迴路（獨立發現，路徑實查 demo.html:1651,1687）；CI 規則字面漏接 `from google import genai`（現有 12 處全用此形式）→ AST/雙形式；殘留掃描改 `⟦` 單字元；殘留「警示不擋」方向確認正確 |
| simplifier | SURVIVED | nonce 冗餘 → v3 採納移除；驗收 2 精簡至 ~15 趟；`llm_client.chat()` 開 model 參數；驗收 4 範圍限定；prompt 模板禁實體樣式示例 |

### 第三輪（v3.0 → v3.1 收尾，2026-07-10）

| 鏡頭 | 裁決 | 處置 |
|------|------|------|
| skeptic | **未執行**（User 中止該子代理）——其預定審查角度（前綴碰撞、常見詞簡稱誤替換、基線有效性、防護對象誠實聲明）已由主迴圈自查納入 v3.1（§0 聲明、§3 鐵律 (e)、§6 基線修訂、§7 風險表），但**未經獨立鏡頭驗證**，如實標注 | 誠實記錄 |
| red-team | REFUTED——「回送只接受遮蔽版」是自律不是機制（server 即棄 mapping 後原理上驗不了回送內容）；前端就地 unmask 單一 bug 即靜默全潰；demo.html 既有 XSS 而 DOM 被升格為安全邊界；mapping 前端存放未規範 | v3.1 全部採納：HMAC 回送驗簽（§3/§6）、前端鐵律五條（§3）、XSS 修復列前置條件（§3）、no-store（§3） |
| simplifier | SURVIVED——v3 架構選擇正確（前端呈現邊界優於 server 快取方案，經 contracts.py 無狀態現況查證）；驗收 2 基線「沿用舊產出」反而更複雜應改重跑；渲染路徑實為五處非三處 | v3.1 採納：基線重跑（§6）、五處替換 + 單一 helper（§3） |

**收尾裁決（User 決定，2026-07-10）**：三輪抗辯後採選項 2 收尾——v3.1 納入全部已知修正，不再送審。依 loop-until-dry 嚴格標準（資料安全類需連續兩輪無新發現），本文件**尚未達到 confirmed**；殘餘狀態如實標注：(1) skeptic 第三輪未獨立執行；(2) v3.1 的修正（HMAC、前端鐵律）未經任何鏡頭審過。**賽後實作前建議對 v3.1 補跑一輪三鏡頭**，屆時連同實作代碼一起審。
