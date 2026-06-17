# Blue-AI 合約文件比對助理

> 「像有一個資深法務顧問幫你審合約」

## 專案簡介

Blue-AI 合約智能比對助理，讓法務與 PM 在 30 分鐘內完成過去需要 2 小時的合約審查。不只找出差異，更給出重點摘要、風險等級與可直接用於協商的對策建議。

**專案規劃**: 詳見 [PROJECT_PLAN.md](PROJECT_PLAN.md)  
**架構設計**: 詳見 [docs/architecture/service_design.md](docs/architecture/service_design.md)  
**當前狀態**: 🟢 核心管道完成，進入 Demo 介面階段（2026-06-17）

---

## 核心功能

### 差異比對

- 逐條比對合約條款變更（新增、修改、刪除）
- 條款對齊演算法（LCS + 條款號比對 + Needleman-Wunsch）
- 支援 MD、PDF、DOCX 格式

### 智能風險分析

- Rule-based 風險引擎，11 條規則，high-risk recall 100%
- 風險等級：高 / 中 / 低，含觸發原因與條款證據
- 不依賴 LLM 做風險判斷，結果穩定可重現

### 摘要與協商建議

- 100 個差異 → 3-5 個主要變更
- 每個高風險項目給出 2-3 個可直接用於協商的方案
- 支援 Claude API（有 key 時）或 template fallback（無 key 時皆可運行）

### 結構化報告

- Markdown 報告輸出
- 審閱建議分層：必須協商 / 建議協商 / 可接受
- 完整風險旗標表格供稽核追蹤

---

## 快速開始

### 執行比對（命令列）

```bash
python3 -m src.services.contract.orchestrator \
  "sla_contract/SLA-like Base Contract v1.md" \
  sla_contract/sla_v4_remove_protection.md \
  --output samples/report.md
```

### 執行評估（驗證 gold set）

```bash
python3 -m src.services.contract.evaluate
```

### 使用 Claude API

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python3 -m src.services.contract.orchestrator original.md revised.md
```

不設定 API key 時，系統自動使用 template fallback，仍可產出完整報告。

---

## 專案結構

```text
bule-ai-team/
├── PROJECT_PLAN.md                    # 專案說明與 Demo 展示
├── CLAUDE.md                          # Claude Code 開發規範
├── README.md                          # 本文件
├── .claude/
│   └── skills/contract-diff.md       # Skill 定義
├── docs/
│   ├── 專案藍圖摘要.md                # 決策文件
│   ├── architecture/
│   │   ├── diagrams.md               # 系統架構圖（Mermaid）
│   │   └── service_design.md         # 模組設計與 I/O 格式
│   ├── planning/
│   │   ├── blueaitem_quest.md        # 原始題目
│   │   └── 專案重新定位_部長回饋版.md
│   └── reports/
│       └── 週報_合約比對專案困難分析.md
├── src/services/contract/
│   ├── schemas.py                    # 共用資料型別
│   ├── parser.py                     # 文件解析（MD/PDF/DOCX）
│   ├── alignment.py                  # 條款對齊
│   ├── diff_engine.py                # 差異比對
│   ├── risk_engine.py                # 規則引擎（11 條規則）
│   ├── llm_service.py                # LLM 摘要與協商建議
│   ├── report_generator.py           # 報告輸出
│   ├── orchestrator.py               # 全流程串接
│   └── evaluate.py                   # gold set 評估腳本
├── sla_contract/
│   ├── SLA-like Base Contract v1.md  # 基準版（v1）
│   ├── sla_v2_degrade.md             # 服務水準放寬版
│   ├── sla_v3_liability.md           # 責任加重版
│   ├── sla_v4_remove_protection.md   # 保護條款刪減版
│   ├── sla_v5_termination.md         # 終止條款偏甲方版
│   ├── annotations_v2_degrade.csv    # 人工標註（v2）
│   ├── annotations_v3_liability.csv  # 人工標註（v3）
│   ├── annotations_v4_protection.csv # 人工標註（v4）
│   └── annotations_v5_termination.csv# 人工標註（v5）
├── samples/
│   ├── gold_annotations.csv          # 黃金標註集（38 筆）
│   └── report_v1_vs_v4.md            # 範例輸出報告
└── archive/                          # 舊版文件封存
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
[Risk Engine]   → risk_flag / risk_level / trigger_reason
      ↓
[LLM Service]   → 白話摘要 / 重點收斂 / 協商對策
      ↓
[Report]        → Markdown 報告
```

### 核心設計原則

> **Risk Rule Engine 做判斷與標記，LLM 做解釋與表達。**

LLM 不決定風險等級，只把已標記的風險翻成白話並給出協商對策。這讓輸出穩定、可解釋、可測試。

### 技術選型

| 元件 | 選擇 |
| --- | --- |
| LLM | Claude Sonnet 4.6（有 API key 時啟用） |
| 文件解析 | pdfplumber + python-docx + 原生 MD parser |
| 差異演算法 | difflib SequenceMatcher + Needleman-Wunsch DP |
| 風險分類 | Rule-based（11 條規則，純 Python） |
| 後端 | FastAPI（待開發） |
| 資料庫 | PostgreSQL + pgvector（待開發） |

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

- [ ] FastAPI endpoint（`POST /api/v1/contracts/compare`）
- [ ] Demo UI（靜態 HTML，上傳兩份合約 → 顯示報告）
- [ ] pgvector 整合（Retrieval Service，Phase 1.5）

---

*所有 AI 分析僅供輔助參考，最終決策需由法務人員確認。*
