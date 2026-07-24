# Blue-AI 合約文件比對助理

> 「像有一個資深法務顧問幫你審合約」

## 專案簡介

Blue-AI 合約智能比對助理，讓法務與 PM 在 30 分鐘內完成過去需要 2 小時的合約審查。不只找出差異，更給出重點摘要、風險等級與可直接用於協商的對策建議。

**專案規劃**: 詳見 [PROJECT_PLAN.md](PROJECT_PLAN.md)  
**架構設計**: 詳見 [docs/architecture/service_design.md](docs/architecture/service_design.md)、[docs/architecture/系統架構_mermaid.md](docs/architecture/系統架構_mermaid.md)（Mermaid 完整架構圖）  
**當前狀態**: 🟢 Phase 1.5 + Verification Agent（Layer 2）+ Layer 3（法律依據檢索）完成，2026-07-02

---

## 核心功能

### 差異比對

- 逐條比對合約條款變更（新增、修改、刪除）
- 條款對齊演算法（LCS + 條款號比對 + Needleman-Wunsch）
- 支援 MD、PDF、DOCX 格式

### 智能風險分析（Layer 1：規則引擎）

- Rule-based 風險引擎，14 條規則，預定義類別內 high-risk recall 100%
- 風險等級：高 / 中 / 低，含觸發原因與條款證據
- 不依賴 LLM 做風險判斷，結果穩定可重現、免費、瞬間

### Verification Agent 語意補漏（Layer 2）

- LLM 讀取差異內容（不讀全文，控制 context window），找出規則引擎看不懂的語意變化——例如中文分數寫法「千分之一」（=0.1%）vs 阿拉伯數字「0.3%」，Regex 無法比較但語意上明顯不同
- 與規則引擎交叉核對，比對 key 為 `(clause_id, 風險類別)`，避免同一條款有多個風險維度時互相誤判
- 補漏結果標記為 `⚠ Agent 補漏`，與規則引擎的 `✓ 規則觸發` 明確區分來源，不混淆兩種確信程度
- Case C（Agent-only）補漏會累積寫入 `candidate_rules.jsonl`，供人工判斷是否該升級成正式規則（不自動生成規則）

### MAS 雙重驗證（Phase 1.5）

- 高風險條款自動觸發 Agent A（嚴格）+ Agent B（平衡）平行評估
- `✓ 雙重驗證`：兩個 Agent 同意或嚴格優先；`⚠ 待確認`：高/低 2 級真正分歧
- Agent A 知識庫（最壞情況）+ Agent B 知識庫（台灣業界慣例）從 skill md 動態載入

### 摘要與協商建議

- 100 個差異 → 3-5 個主要變更
- 三層協商對策：🟢 首選 / 🟡 折衷 / 🔴 底線 + 替換條款文字
- 支援 Gemini 3.1 Flash Lite（主）/ Claude Sonnet 4.6（備）/ template fallback

### 協商建議法律依據檢索（Layer 3）

- **真實法條**：離線用 `mcp-taiwan-legal-db`（MIT 授權、免 API key，接法務部全國法規資料庫）查回民法／民事訴訟法條文，快取於 `legal_citations_cache.json`，執行時純同步讀檔，無即時網路依賴
- **相似先例**：用 `gemini-embedding-2` 對合成先例語料庫（`precedent_corpus.py`）做真實向量檢索（cosine similarity），不是關鍵字比對，也不需要 PostgreSQL
- 協商建議只在真的檢索到依據時才顯示「⚖ 法律依據」，System Prompt 明確禁止 LLM 自行編造法條——查無依據時欄位留空，是誠實揭露而非顯示錯誤

### 結構化報告

- Markdown 報告輸出
- 審閱建議分層：必須協商 / 建議協商 / 可接受
- 完整風險旗標表格供稽核追蹤

---

## 快速開始

### Demo UI（推薦）

```bash
# Terminal 1 — 啟動後端
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Terminal 2 — 開啟 UI
open frontend/demo.html
```

點「範例模式」選 v2–v6，或上傳自己的 PDF/DOCX/MD 合約。v6 是獨立的軟體維護合約範例（重現真實合約發現的中文分數費率問題），不是 v1 的修訂版。

### API

```bash
# 上傳兩份合約
curl -X POST http://localhost:8000/api/v1/contracts/compare \
  -F "original_file=@original.md" \
  -F "revised_file=@revised.md"

# 範例模式（不需上傳，v2-v6 皆可）
curl http://localhost:8000/api/v1/contracts/compare/example/v6
```

互動式 API 文件：`http://localhost:8000/docs`

### 命令列

```bash
python3 -m src.services.contract.orchestrator \
  "sla_contract/SLA-like Base Contract v1.md" \
  sla_contract/sla_v4_remove_protection.md \
  --output samples/report.md
```

### 安裝依賴

```bash
pip install -r requirements.txt
cp .env.example .env   # 填入實際的 API key
```

`.env` 需要的環境變數：

```env
GEMINI_API_KEY=...       # 主要 LLM，優先使用
ANTHROPIC_API_KEY=...    # 備援 LLM，Gemini 沒設定或呼叫失敗時使用
```

**LLM 優先順序**：Gemini（主）→ Claude（備）→ template fallback（兩者都沒設定時，仍可產出完整報告，只是協商建議是預先寫好的樣板，不是即時生成）。

**Layer 3 法條快取（選用，已內建現成快取，通常不需重新產生）**：`legal_citations_cache.json`、`precedent_corpus.json` 已經是離線建置好的真實資料，直接使用即可。如需重新產生先例語料庫的向量（例如修改了 `precedent_corpus.py` 裡的案例內容），執行：

```bash
python -m src.services.contract.precedent_corpus   # 需要 GEMINI_API_KEY
```

若要重新查詢法條快取，需另外 `pip install mcp-taiwan-legal-db`（僅離線建置時需要，Demo 執行時不依賴此套件）。

---

## 專案結構

```text
bule-ai-team/
├── requirements.txt                   # 依賴清單
├── PROJECT_PLAN.md                    # 專案說明與 Demo 展示
├── CLAUDE.md                          # Claude Code 開發規範
├── README.md                          # 本文件
├── frontend/
│   └── demo.html                      # Demo UI（靜態單頁）
├── src/
│   ├── api/
│   │   ├── main.py                    # FastAPI app 進入點
│   │   ├── contracts.py               # /api/v1/contracts/* endpoints
│   │   └── schemas_api.py             # Pydantic request/response models
│   └── services/contract/
│       ├── schemas.py                 # 共用資料型別
│       ├── parser.py                  # 文件解析（MD/PDF/DOCX，含表格交錯讀取）
│       ├── alignment.py               # 條款對齊
│       ├── diff_engine.py             # 差異比對
│       ├── risk_engine.py             # 規則引擎（Layer 1，14 條規則）
│       ├── verifier.py                # Verification Agent（Layer 2，LLM 語意補漏）
│       ├── llm_service.py             # LLM 摘要與協商建議 + Layer 3 依據檢索
│       ├── precedent_corpus.py        # Layer 3：先例語料庫 + 向量檢索邏輯
│       ├── precedent_corpus.json      # Layer 3：離線建置好的先例向量快取
│       ├── legal_citations_cache.json # Layer 3：離線查回的真實法條快取
│       ├── mas_service.py             # MAS 雙重驗證（Agent A/B + Judge）
│       ├── report_generator.py        # 報告輸出
│       ├── orchestrator.py            # 全流程串接
│       └── evaluate.py                # gold set 評估腳本
├── docs/
│   ├── 專案藍圖摘要.md                # 決策文件
│   ├── architecture/
│   │   ├── 系統架構_mermaid.md        # 系統架構圖（Mermaid，持續更新中）
│   │   ├── diagrams.md               # 早期架構圖
│   │   └── service_design.md         # 模組設計與 I/O 格式
│   ├── specs/
│   │   └── verification_agent_spec.md # Verification Agent 設計規格 + 實作紀錄
│   └── planning/
│       └── blueaitem_quest.md        # 原始題目
├── sla_contract/
│   ├── SLA-like Base Contract v1.md  # 基準版（v1）
│   ├── sla_v2_degrade.md             # 服務水準放寬版
│   ├── sla_v3_liability.md           # 責任加重版
│   ├── sla_v4_remove_protection.md   # 保護條款刪減版
│   ├── sla_v5_termination.md         # 終止條款偏甲方版
│   ├── maintenance_v6_base.md        # v6 基準版（獨立範例，不沿用 v1）
│   ├── maintenance_v6_penalty_rate.md # v6 修訂版（中文分數費率變化）
│   └── annotations_v*.csv            # 人工標註（v2-v5）
├── nda_contract/
│   ├── NDA_v1_company.md             # NDA 甲方版（單向保密、5年、無上限）
│   └── NDA_v2_counterparty.md        # NDA 乙方修改版（雙向、2年、賠償上限）
├── next_step_plan.md                  # 任務清單 + 評審 Q&A 準備 + 技術探索備忘
└── samples/
    ├── gold_annotations.csv           # 黃金標註集（38 筆）
    └── report_v1_vs_v4.md             # 範例輸出報告
```

> `pic_contract/`（真實公司合約）與 `candidate_rules.jsonl`（含條款文字擷取）已加入 `.gitignore`，不會出現在版本控制中，僅供本機內部測試使用。

---

## 技術架構

### 處理管道

```text
[上傳兩份合約]
      ↓
[Parser]        → 條款切分（clause_id + title + content，含表格交錯讀取）
      ↓
[Alignment]     → 條款對齊（LCS + 條款號 + Needleman-Wunsch）
      ↓
[Diff Engine]   → 新增 / 修改 / 刪除清單
      ↓
[Risk Engine]   → risk_flag / risk_level / trigger_reason（Layer 1，14 條規則）
      ↓
[Verification Agent] → LLM 語意補漏（Layer 2），與 Layer 1 交叉核對
      ↓
[Layer 3]       → 查真實法條快取 + 查相似先例（向量檢索）
      ↓
[LLM Service]   → 白話摘要 / 重點收斂 / 協商對策（含法律依據）
      ↓
[MAS]           → 高風險條款 → Agent A（嚴格）‖ Agent B（平衡）→ Judge
      ↓
[Report]        → Markdown 報告 + MAS 雙重驗證標籤
```

### 核心設計原則

> **Risk Rule Engine 做判斷與標記，LLM 做解釋與表達。這是 AI 協作架構，不是自主 Agent。**

規則負責有確定解的部分（免費、瞬間、100% 一致），LLM 負責真正需要語意理解的部分。系統裡每次 LLM 呼叫都是結構化的單次任務，由程式碼決定執行順序，不會自己決定下一步要做什麼——這是刻意的選擇，因為法務審查需要可預測、可測試的行為。

### 技術選型

| 元件 | 選擇 |
| --- | --- |
| LLM | Gemini 3.1 Flash Lite（主）/ Claude Sonnet 4.6 · Haiku 4.5（備）/ template fallback |
| 文件解析 | pdfplumber + python-docx（含表格交錯讀取）+ 原生 MD parser |
| 差異演算法 | difflib SequenceMatcher + Needleman-Wunsch DP |
| 風險分類 | Rule-based（Layer 1，14 條規則，純 Python）+ LLM 語意補漏（Layer 2） |
| 協商依據檢索 | `mcp-taiwan-legal-db` 離線法條快取 + `gemini-embedding-2` 本地向量檢索（Layer 3） |
| MAS | ThreadPoolExecutor + Judge 矩陣（gap-based） |
| 後端 | FastAPI（`src/api/`，`run_in_threadpool` 確保並行請求不互相阻塞） |

---

## 驗證數字

| 指標 | 結果 | 目標 |
| --- | --- | --- |
| High-risk recall | **100%** | 100%（預定義類別內） |
| Overall detection | 67%（12/18） | >80% |
| 測試樣本 | 38 筆（v1 vs v2-v5 gold set） | — |

> Overall 67%（12/18）為設計選擇：rule engine 寧可高判不漏判，高風險一筆不漏是最重要的保證。

**真實公司合約驗證（2026-07-01/02，NDA / 軟體採購 / 軟體維護三組）**：拿真實合約測試時發現並修復多個規則引擎看不懂的真實案例，例如中文分數費率寫法「千分之一」（Regex 無法辨識，Verification Agent 語意層補上）、純新增/刪除條款因缺條號被靜默丟棄（採購合約一度有 138 段消失）、DOCX 原生表格內容完全遺失（付款排程、簽名欄）。詳見 `next_step_plan.md`、`docs/specs/verification_agent_spec.md`。

---

## 下一步

- [x] FastAPI endpoint（`POST /api/v1/contracts/compare`，`run_in_threadpool` 化）
- [x] Demo UI（靜態 HTML，上傳 / 範例模式 v2-v6）
- [x] 三層協商對策（`POST /api/v1/contracts/negotiate`）
- [x] MAS Phase 1.5（Agent A/B 雙重驗證 + Judge 矩陣）
- [x] NDA 測試合約（v1 甲方版 + v2 乙方修改版）
- [x] Verification Agent（Layer 2，語意補漏 + 交叉核對）
- [x] Layer 3 法律依據檢索（真實法條快取 + 先例向量檢索）
- [x] 真實公司合約驗證（NDA / 軟體採購 / 軟體維護）
- [x] 邊界測試（空條款 / 超長條款 / 表格條款）+ 壓測（並行請求）
- [ ] 週次 3：簡報製作、Demo 流程預演
- [ ] 異質模型 MAS（Phase 2：Gemini Agent A + Claude Agent B）
- [ ] 真實 PostgreSQL + pgvector（Phase 2，目前用本地 JSON + cosine similarity）

---

*所有 AI 分析僅供輔助參考，最終決策需由法務人員確認。*
