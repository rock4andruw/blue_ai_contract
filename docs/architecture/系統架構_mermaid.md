%%{init: {"theme": "base","themeVariables": {"background": "#050816","primaryColor": "#0b1220","primaryTextColor": "#e6f1ff","primaryBorderColor": "#22d3ee","lineColor": "#5eead4","secondaryColor": "#101a2f","tertiaryColor": "#0f172a","fontFamily": "'Noto Sans TC', 'Microsoft JhengHei', 'PingFang TC', sans-serif","fontSize": "14px"},"flowchart": {"htmlLabels": true,"curve": "basis","nodeSpacing": 32,"rankSpacing": 44}}}%%

flowchart LR

USER["👤 使用者（USER）\n法務 / PM / 業務"]

subgraph P15["🟡 Phase 1.5 — MAS 雙重驗證（已完成）"]
    direction TB
    SK1["📋 contract-risk-analysis.md\n15 條規則邏輯說明\n風險代碼對照表"]
    SK2["💬 negotiation-strategy.md\n協商框架 3 層方案\nAgent B 業界慣例知識庫"]
    SK3["📝 contract-diff.md\n系統總覽 · Demo 流程\nPhase 路線圖"]
    MA["🔴 Agent A（嚴格）\n極度保守買方法律顧問\n知識庫：最壞情況場景表"]
    MB["🟡 Agent B（平衡）\n促成交易商務法務\n知識庫：台灣 SaaS 業界慣例"]
    JG["⚖️ Judge 矩陣\ngap=0/1 → ✓ confirmed（嚴格優先）\ngap=2 → ⚠ pending（人工介入）\n失敗 → single_agent（靜默退級）"]
    SK1 -->|注入 System Prompt| MA
    SK2 -->|注入 System Prompt| MB
    MA -->|ThreadPoolExecutor 平行| JG
    MB -->|ThreadPoolExecutor 平行| JG
end

subgraph P1["🟢 Phase 1 — MVP（已完成）"]
    direction TB

    subgraph FRONT["前端（FRONT）"]
        UI["🖥 Demo UI\nfrontend/demo.html\n上傳模式 / 範例模式 v2–v5"]
    end

    subgraph APIL["API 層（API）"]
        API["🔌 FastAPI\nPOST /api/v1/contracts/compare\nGET /example/{v2-v5}\nPOST /api/v1/contracts/negotiate"]
    end

    subgraph PIPELINE["核心管道（PIPELINE）"]
        direction LR
        PARSER["📄 Parser\nMD / PDF / DOCX\ntrack-change HTML 清理\npdfplumber · python-docx"]
        ALIGN["🔗 Alignment\nLCS + 條款號比對\nNeedleman-Wunsch DP\n相似度後處理 ≥75%"]
        DIFF["🔀 Diff Engine\n新增 / 修改 / 刪除\nDiffItem 標準化輸出"]
        RISK["🛡 Risk Rule Engine\n15 條規則 · pure Python\nHigh-risk recall 100%\nrisk_code · risk_level · trigger_reason"]
        LLM["🤖 LLM Service\nGemini 3.1 Flash Lite（主）\nClaude Sonnet 4.6（備）\nTemplate fallback（無 key 可跑）"]
        RPT["📊 Report Generator\nMarkdown 報告輸出\n審閱建議分層\nMAS 標籤整合"]
        PARSER --> ALIGN --> DIFF --> RISK --> LLM --> RPT
    end

    subgraph STORE["本地資料"]
        D1["📁 sla_contract/\nv1–v5 測試合約\nbase + degrade + liability\nprotect + termination"]
        D2["📁 nda_contract/\nNDA_v1_company.md\nNDA_v2_counterparty.md"]
        D3["📊 gold_annotations.csv\n38 筆人工標註\nv2–v5 全覆蓋"]
    end

    subgraph EVAL["驗證指標"]
        E1["📐 High-risk Recall: 100%\nOverall Detection: 61%\n樣本: 38 筆 gold set\nMAS pending 率: v4=0% / v3=67%"]
    end

    UI --> API --> PARSER
    D1 --> PARSER
    D2 --> PARSER
    D3 --> EVAL
    EVAL --> RISK
end

subgraph PRINCIPLE["核心設計原則"]
    direction TB
    PR1["Rule Engine 做判斷\n→ LLM 做解釋\n→ MAS 做驗證"]
    PR2["📌 高風險不漏判\n寧可多判不漏判\nrecall 優先於 precision"]
    PR3["🔒 資料不離開企業\nStateless API\n本地部署優先"]
end

subgraph EXT["☁️ 外部服務（External Cloud）"]
    direction TB
    CLAUDE["🟠 Claude API\nclaude-sonnet-4-6\n備援 LLM · MAS Agent"]
    GEMINI["🔵 Gemini API\ngemini-3.1-flash-lite\n主要 LLM · MAS Agent"]
    AZURE["🔷 Azure\nBlob Storage · AD 認證\nApp Insights 監控"]
end

subgraph P2["🔵 Phase 2 — 能力擴展（3–6 月）"]
    direction LR
    subgraph P2L["MCP 整合"]
        LAW["⚖️ Taiwan Law MCP\n個資法 / 民法\n法條自動引用"]
        O365["📧 Office 365 MCP\nTeams 通知\nSharePoint 歸檔"]
    end
    subgraph P2R["Phase 2 擴展項目"]
        PG["🗄 PostgreSQL + pgvector\n企業標準條款庫\n語意相似度檢索"]
        CTYPE["📄 合約類型擴展\nNDA · 採購合約 · LOI\n合約範本庫 CONTRACT_EXT"]
        HETERO["🎭 異質模型 MAS\nGemini Agent A\n+ Claude Agent B\n消除 Echo Chamber"]
    end
end

subgraph P3["🟣 Phase 3 — 企業級產品化（6–12 月）"]
    direction LR
    subgraph MAS3["Multi-Agent System（MAS）"]
        ORCH["🎯 Orchestrator Agent\n任務分派 · 並行協調"]
        RAGENT["⚠️ Risk Agent\n深度條款語意分析"]
        RETAG["🔍 Retrieval Agent\n歷史合約 · 相似案例"]
        LLAG["✍️ LLM Report Agent\n白話摘要 · 報告生成"]
        NOTIF["📣 Notification Agent\nTeams / Email 推送"]
        ORCH --> RAGENT & RETAG & LLAG & NOTIF
    end
    subgraph ENT["企業功能（ENTERPRISE）"]
        E2["🔐 RBAC 三層權限\n管理員 / 法務 / 唯讀"]
        E3["📅 History Agent\n合約修改時間軸\n談判趨勢分析"]
        E4["📋 週報整併\n多份審查週報\n→ 自動月報"]
    end
end

USER --> UI
JG -->|mas_status · mas_confidence\nfinal_risk_level| RPT
RISK -->|高風險 flag| MA
RISK -->|高風險 flag| MB
LLM --> GEMINI
LLM --> CLAUDE
MA --> GEMINI
MB --> GEMINI
AZURE -.->|正式環境部署| D1
PG -.->|Phase 2：語意增強| RISK
LAW -.->|Phase 2：法條引用| LLM
O365 -.->|Phase 2：自動通知| RPT
HETERO -.->|Phase 2：取代同質 MAS| JG

classDef done fill:#07131f,stroke:#00e5ff,stroke-width:2px,color:#e6faff;
classDef mas fill:#1a1020,stroke:#f472b6,stroke-width:2px,color:#fff1fb;
classDef plan fill:#081422,stroke:#38bdf8,stroke-width:2px,color:#eff6ff;
classDef ent fill:#140d22,stroke:#a855f7,stroke-width:2px,color:#f5f3ff;
classDef ext fill:#0a1020,stroke:#7c3aed,stroke-width:2px,color:#eef2ff;
classDef principle fill:#0d1a10,stroke:#4ade80,stroke-width:1.5px,color:#f0fdf4;
classDef pipeline fill:#06111b,stroke:#0f766e,stroke-width:1.5px,color:#ecfeff;
classDef skill fill:#1c1328,stroke:#f472b6,stroke-width:1.5px,color:#fdf2f8;
classDef agent_a fill:#1f0a0a,stroke:#f87171,stroke-width:2px,color:#fff1f2;
classDef agent_b fill:#1a1400,stroke:#fbbf24,stroke-width:2px,color:#fffbeb;
classDef judge fill:#061a10,stroke:#34d399,stroke-width:2px,color:#ecfdf5;
classDef store fill:#0a1a12,stroke:#6ee7b7,stroke-width:1.5px,color:#ecfdf5;
classDef extc fill:#0b1324,stroke:#818cf8,stroke-width:1.5px,color:#eef2ff;
classDef mcp fill:#0f1a26,stroke:#60a5fa,stroke-width:1.5px,color:#eff6ff;
classDef hetero fill:#1a0f1f,stroke:#e879f9,stroke-width:1.8px,color:#fdf4ff;

class P1 done;
class P15 done;
class P2 plan;
class P3 ent;
class EXT ext;
class PRINCIPLE principle;
class PARSER,ALIGN,DIFF,RISK,LLM,RPT pipeline;
class SK1,SK2,SK3 skill;
class MA agent_a;
class MB agent_b;
class JG judge;
class D1,D2,D3,EVAL,E1 store;
class CLAUDE,GEMINI,AZURE extc;
class LAW,O365 mcp;
class HETERO hetero;
class PG store;
class ORCH,RAGENT,RETAG,LLAG,NOTIF agent_a;
class E2,E3,E4 entf;

classDef entf fill:#18130b,stroke:#f59e0b,stroke-width:1.5px,color:#fffbeb;
