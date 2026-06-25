# Blue-AI 合約智能比對助理 — 系統架構圖

## 完整架構（含 Phase 分區）

```mermaid
graph TB
    %% ────────────────────────────────────────────────
    %% 使用者入口
    %% ────────────────────────────────────────────────
    USER(["👤 使用者\n法務 / PM / 業務"])

    %% ════════════════════════════════════════════════
    subgraph P1["🟢 Phase 1 — MVP（已完成）"]
        direction TB

        subgraph FRONT["前端層"]
            UI["🖥 Demo UI\nfrontend/demo.html\n上傳模式 ／ 範例模式 v2-v5"]
        end

        subgraph API["API 層"]
            EP1["POST /api/v1/contracts/compare\n（檔案上傳）"]
            EP2["GET /example/{v2~v5}\n（範例模式）"]
            EP3["GET /health"]
        end

        subgraph PIPELINE["核心比對管道"]
            direction LR
            PARSER["📄 Parser\nMD / PDF / DOCX\n→ ClauseElement[]"]
            ALIGN["🔗 Alignment\nLCS + Needleman-Wunsch\n→ MatchBlock[]"]
            DIFF["🔍 Diff Engine\n新增 / 修改 / 刪除\n→ DiffItem[]"]
            RISK["⚠️ Risk Rule Engine\n14 條規則\nSLA + NDA 風險類型\n→ RiskFlag[]"]
            LLM["🤖 LLM Service\nClaude / Gemini\n/ Template Fallback\n→ ReportSection[]"]
            REPORT["📊 Report Generator\n→ JSON + Markdown"]
            PARSER --> ALIGN --> DIFF --> RISK --> LLM --> REPORT
        end

        subgraph STORAGE1["本地儲存"]
            FILES["📁 sla_contract/\nv1~v5 測試合約"]
            GOLD["✅ gold_annotations.csv\n38 筆人工標註"]
            COMPANY["🏢 公司文件/\nNDA 單務 ／ 雙務"]
        end

        EVAL["📐 evaluate.py\nHigh-risk recall: 100%\nOverall: 61%"]
    end

    %% ════════════════════════════════════════════════
    subgraph P15["🔄 Phase 1.5 — Skill Sub-Agent（進行中）"]
        direction LR
        SKILL1["📋 contract-risk-analysis.md\n14 條規則定義\n不依賴 LLM 判斷"]
        SKILL2["💬 negotiation-strategy.md\n各風險類型協商框架\n2-3 個可行方案"]
        SKILL3["📝 report-writing.md\n白話翻譯原則\n輸出格式規範"]
        ORCHESTRATOR["🎯 Orchestrator Sub-Agent\n動態載入 Skill\n協調各 Sub-Agent"]
        SKILL1 & SKILL2 & SKILL3 --> ORCHESTRATOR
    end

    %% ════════════════════════════════════════════════
    subgraph P2["⬜ Phase 2 — 能力擴展（3-6 個月）"]
        direction TB

        subgraph DB["向量資料庫"]
            PG["🗄 PostgreSQL + pgvector\n企業標準條款庫\n語意相似度檢索"]
        end

        subgraph MCP["MCP 整合"]
            LAW["⚖️ Taiwan Law MCP\n個資法 / 民法 條文引用\nwasonisgood/legel-mcp"]
            O365["📧 Office 365 MCP\nTeams 通知\nSharePoint 歸檔\nOutlook email"]
        end

        subgraph CONTRACT_EXT["合約類型擴展"]
            NDA_EXT["📄 NDA 保密協議"]
            PROC["📦 採購合約"]
            LOI["🤝 合作意向書"]
        end
    end

    %% ════════════════════════════════════════════════
    subgraph P3["⬜ Phase 3 — 企業級產品化（6-12 個月）"]
        direction LR

        subgraph MAS["Multi-Agent System"]
            ORC["🎭 Orchestrator Agent"]
            AG1["🔍 Risk Agent"]
            AG2["📚 Retrieval Agent\n查標準條款庫"]
            AG3["✍️ LLM Agent\n摘要 + 協商"]
            AG4["📊 Report Agent"]
            AG5["📬 Notification Agent\nTeams / Email"]
            ORC --> AG1 & AG2 & AG3 & AG4 & AG5
        end

        subgraph ENTERPRISE["企業功能"]
            RBAC["🔐 RBAC 權限分層\n法務 / PM / 高層"]
            HIST["📅 History Agent\n合約修改歷史追蹤\n談判趨勢分析"]
            WEEKLY["📈 週報整併\n多份審查 → 月報"]
        end
    end

    %% ════════════════════════════════════════════════
    %% 外部服務
    %% ════════════════════════════════════════════════
    subgraph EXT["☁️ 外部服務"]
        CLAUDE_API["🟠 Claude API\nclaude-sonnet-4-6"]
        GEMINI_API["🔵 Gemini API\ngemini-flash-lite"]
        AZURE["🔷 Azure\nBlob Storage\nAD 認證\nApp Insights"]
    end

    %% ────────────────────────────────────────────────
    %% 連線
    %% ────────────────────────────────────────────────
    USER --> UI
    UI --> EP1 & EP2
    EP1 & EP2 --> PIPELINE
    STORAGE1 --> PIPELINE
    GOLD --> EVAL
    EVAL --> RISK

    %% Phase 1.5 接管 LLM 層
    P15 -.->|"Phase 1.5 替換\nLLM prompt 來源"| LLM

    %% Phase 2 接入管道
    PG -.->|"Phase 2\n條款語意檢索"| RISK
    LAW -.->|"Phase 2\n法條引用"| LLM
    O365 -.->|"Phase 2\n自動通知"| REPORT

    %% Phase 3 包覆整個系統
    P3 -.->|"Phase 3\n升級為 MAS"| PIPELINE

    %% 外部 API
    LLM --> CLAUDE_API & GEMINI_API
    AZURE -.->|"正式環境"| STORAGE1

    %% ────────────────────────────────────────────────
    %% 樣式
    %% ────────────────────────────────────────────────
    classDef done fill:#d4edda,stroke:#28a745,color:#155724
    classDef inprogress fill:#fff3cd,stroke:#ffc107,color:#856404
    classDef planned fill:#f8f9fa,stroke:#6c757d,color:#495057
    classDef external fill:#cce5ff,stroke:#004085,color:#004085

    class P1 done
    class P15 inprogress
    class P2,P3 planned
    class EXT external
```

---

## Phase 說明

| Phase | 狀態 | 時間 | 核心目標 |
|---|---|---|---|
| **Phase 1** | 🟢 已完成 | 2026-06 | SLA/NDA 比對 + FastAPI + Demo UI |
| **Phase 1.5** | 🔄 進行中 | 2026-06~07 | Skill Sub-Agent 架構，Prompt 與程式碼分離 |
| **Phase 2** | ⬜ 規劃中 | 2026-07~09 | pgvector 條款庫 + Taiwan Law MCP + Teams |
| **Phase 3** | ⬜ 規劃中 | 2026-10~12 | 完整 MAS + RBAC + 歷史追蹤 + 企業級 |

---

## 核心設計原則

```
Rule Engine 做判斷  →  LLM 做解釋
（不讓 AI 猜風險等級，防止幻覺漏判）
```

| 層級 | 職責 | 實作 |
|---|---|---|
| **Rule Engine** | 判斷 / 標記風險等級 | 14 條 Python 規則，pure logic |
| **LLM Service** | 白話解釋 + 協商對策 | Claude / Gemini / Template fallback |
| **Skill Sub-Agent** | Prompt 定義（Phase 1.5） | `.claude/skills/*.md` |
| **MAS Orchestrator** | 多 Agent 協調（Phase 3） | 動態路由，支援並行處理 |

---

## 驗證指標

| 指標 | 數值 | 說明 |
|---|---|---|
| High-risk recall | **100%** | 高風險條款一筆不漏（38 筆 gold set） |
| Overall detection | **61%** | 保守設計，寧可高判不漏判 |
| 支援格式 | MD / PDF / DOCX | Phase 2 加入掃描 PDF（OCR） |
| 支援合約類型 | SLA / NDA | Phase 2 加入採購 / 意向書 |
