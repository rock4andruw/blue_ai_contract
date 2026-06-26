# Blue-AI 合約文件比對助理

> 「像有一個資深法務顧問幫你審合約」

## 專案簡介

Blue-AI 合約智能比對助理，讓法務與 PM 在 30 分鐘內完成過去需要 2 小時的合約審查。不只找出差異，更給出重點摘要、風險等級與可直接用於協商的對策建議。

**專案規劃**: 詳見 [PROJECT_PLAN.md](PROJECT_PLAN.md)  
**架構設計**: 詳見 [docs/architecture/service_design.md](docs/architecture/service_design.md)  
**當前狀態**: 🟢 Phase 1.5 完成（API + UI + MAS 雙重驗證 + 三層協商對策），2026-06-26

---

## 核心功能

### 差異比對

- 逐條比對合約條款變更（新增、修改、刪除）
- 條款對齊演算法（LCS + 條款號比對 + Needleman-Wunsch）
- 支援 MD、PDF、DOCX 格式

### 智能風險分析

- Rule-based 風險引擎，15 條規則，high-risk recall 100%
- 風險等級：高 / 中 / 低，含觸發原因與條款證據
- 不依賴 LLM 做風險判斷，結果穩定可重現

### MAS 雙重驗證（Phase 1.5）

- 高風險條款自動觸發 Agent A（嚴格）+ Agent B（平衡）平行評估
- `✓ 雙重驗證`：兩個 Agent 同意或嚴格優先；`⚠ 待確認`：高/低 2 級真正分歧
- Agent A 知識庫（最壞情況）+ Agent B 知識庫（台灣業界慣例）從 skill md 動態載入

### 摘要與協商建議

- 100 個差異 → 3-5 個主要變更
- 三層協商對策：🟢 首選 / 🟡 折衷 / 🔴 底線 + 替換條款文字
- 支援 Gemini 3.1 Flash Lite（主）/ Claude Sonnet 4.6（備）/ template fallback

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

點「範例模式」選 v2–v5，或上傳自己的 PDF/DOCX/MD 合約。

### API

```bash
# 上傳兩份合約
curl -X POST http://localhost:8000/api/v1/contracts/compare \
  -F "original_file=@original.md" \
  -F "revised_file=@revised.md"

# 範例模式（不需上傳）
curl http://localhost:8000/api/v1/contracts/compare/example/v4
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
```

不設定 `ANTHROPIC_API_KEY` 時，系統自動使用 template fallback，仍可產出完整報告。

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
│       ├── parser.py                  # 文件解析（MD/PDF/DOCX）
│       ├── alignment.py               # 條款對齊
│       ├── diff_engine.py             # 差異比對
│       ├── risk_engine.py             # 規則引擎（15 條規則）
│       ├── llm_service.py             # LLM 摘要與協商建議
│       ├── mas_service.py             # MAS 雙重驗證（Agent A/B + Judge）
│       ├── report_generator.py        # 報告輸出
│       ├── orchestrator.py            # 全流程串接
│       └── evaluate.py                # gold set 評估腳本
├── docs/
│   ├── 專案藍圖摘要.md                # 決策文件
│   ├── architecture/
│   │   ├── diagrams.md               # 系統架構圖（Mermaid）
│   │   └── service_design.md         # 模組設計與 I/O 格式
│   └── planning/
│       └── blueaitem_quest.md        # 原始題目
├── sla_contract/
│   ├── SLA-like Base Contract v1.md  # 基準版（v1）
│   ├── sla_v2_degrade.md             # 服務水準放寬版
│   ├── sla_v3_liability.md           # 責任加重版
│   ├── sla_v4_remove_protection.md   # 保護條款刪減版
│   ├── sla_v5_termination.md         # 終止條款偏甲方版
│   └── annotations_v*.csv            # 人工標註（v2-v5）
├── nda_contract/
│   ├── NDA_v1_company.md             # NDA 甲方版（單向保密、5年、無上限）
│   └── NDA_v2_counterparty.md        # NDA 乙方修改版（雙向、2年、賠償上限）
└── samples/
    ├── gold_annotations.csv           # 黃金標註集（38 筆）
    └── report_v1_vs_v4.md             # 範例輸出報告
```

---

## 技術架構

### 處理管道

```text
[上傳兩份合約]
      ↓
[Parser]        → 條款切分（clause_id + title + content）
      ↓
[Alignment]     → 條款對齊（LCS + 條款號 + Needleman-Wunsch）
      ↓
[Diff Engine]   → 新增 / 修改 / 刪除清單
      ↓
[Risk Engine]   → risk_flag / risk_level / trigger_reason（15 條規則）
      ↓
[LLM Service]   → 白話摘要 / 重點收斂 / 協商對策
      ↓
[MAS]           → 高風險條款 → Agent A（嚴格）‖ Agent B（平衡）→ Judge
      ↓
[Report]        → Markdown 報告 + MAS 雙重驗證標籤
```

### 核心設計原則

> **Risk Rule Engine 做判斷與標記，LLM 做解釋與表達。**

LLM 不決定風險等級，只把已標記的風險翻成白話並給出協商對策。這讓輸出穩定、可解釋、可測試。

### 技術選型

| 元件 | 選擇 |
| --- | --- |
| LLM | Gemini 3.1 Flash Lite（主）/ Claude Sonnet 4.6（備）/ template fallback |
| 文件解析 | pdfplumber + python-docx + 原生 MD parser |
| 差異演算法 | difflib SequenceMatcher + Needleman-Wunsch DP |
| 風險分類 | Rule-based（15 條規則，純 Python） |
| MAS | ThreadPoolExecutor + Judge 矩陣（gap-based） |
| 後端 | FastAPI（`src/api/`） |

---

## 驗證數字

| 指標 | 結果 | 目標 |
| --- | --- | --- |
| High-risk recall | **100%** | 100% |
| Overall detection | 61% | >80% |
| 測試樣本 | 38 筆（v1 vs v2-v5） | — |

> Overall 61% 為設計選擇：rule engine 寧可高判不漏判，高風險一筆不漏是最重要的保證。

---

## 下一步

- [x] FastAPI endpoint（`POST /api/v1/contracts/compare`）
- [x] Demo UI（靜態 HTML，上傳 / 範例模式）
- [x] 三層協商對策（`POST /api/v1/contracts/negotiate`）
- [x] MAS Phase 1.5（Agent A/B 雙重驗證 + Judge 矩陣）
- [x] NDA 測試合約（v1 甲方版 + v2 乙方修改版）
- [ ] 異質模型 MAS（Phase 2：Gemini Agent A + Claude Agent B）
- [ ] RAG / 歷史合約庫（Phase 2）

---

*所有 AI 分析僅供輔助參考，最終決策需由法務人員確認。*
