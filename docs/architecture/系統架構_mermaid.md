%%{init: {"theme": "base","themeVariables": {"background": "#050816","primaryColor": "#0b1220","primaryTextColor": "#e6f1ff","primaryBorderColor": "#22d3ee","lineColor": "#5eead4","secondaryColor": "#101a2f","tertiaryColor": "#0f172a","fontFamily": "'Noto Sans TC', 'Microsoft JhengHei', 'PingFang TC', sans-serif","fontSize": "14px"},"flowchart": {"htmlLabels": true,"curve": "basis","nodeSpacing": 32,"rankSpacing": 44}}}%%

flowchart LR

USER["👤 使用者（USER）\n法務 / PM / 業務"]

subgraph P1["🟢 Phase 1 — MVP（已完成）"]
    direction TB

    subgraph FRONT["前端（FRONT）"]
        UI["🖥 Demo UI\n上傳模式 / 範例模式 v2–v6"]
    end

    subgraph APIL["API 層（API）"]
        API["🔌 FastAPI（threadpool 化）\nPOST /api/v1/contracts/compare\nGET /example/{v2-v6}\nPOST /api/v1/contracts/negotiate\nPOST /ask · POST /negotiate/matrix"]
    end

    subgraph PIPELINE["核心管道（PIPELINE）"]
        direction LR
        PARSER["📄 Parser\nMD / PDF / DOCX（含原生表格解析）\nWord 追蹤修改標記自動清理"]
        ALIGN["🔗 Alignment\nLCS + 條款號比對\nNeedleman-Wunsch DP\n相似度後處理 ≥75%"]
        DIFF["🔀 Diff Engine\n新增 / 修改 / 刪除\nDiffItem 標準化輸出"]
        COV["🛡️ Coverage Guard（2026-07-07 已上線）\n字元層級文字守恆檢查，97% 閾值\n防解析階段內容靜默遺漏"]
        RISK["🛡 Risk Rule Engine（Layer 1）\n14 條規則 · 純程式判斷，無 LLM\n預定義風險類別 100% 召回"]
        VA["🔍 Verification Agent（Layer 2）\nLLM 語意補漏，只讀變動條款、不讀全文\n與規則引擎交叉核對，避免重複判斷\n疑似漏判案例自動記錄，供人工複核（不自動生規則）"]
        LLM["🤖 LLM Service\nGemini 3.1 Flash Lite（主）\nClaude Sonnet 4.6 / Haiku 4.5（備）\n無 API Key 時自動降級為內建模板\n統整摘要與原始檢索資料分開呈現，不混淆"]

    subgraph MAS["🟡 Phase 1.5 — MAS 雙重驗證（已完成，只跑高風險 flag）"]
            direction LR
            MA["🔴 Agent A（嚴格）\n極度保守買方法律顧問\n知識庫：最壞情況場景表"]
            MB["🟡 Agent B（平衡）\n促成交易商務法務\n知識庫：台灣 SaaS 業界慣例"]
            JG["⚖️ Judge 矩陣\ngap=0/1 → ✓ confirmed（嚴格優先）\ngap=2 → ⚠ pending（人工介入）\n失敗 → single_agent（靜默退級）"]
            MA -->|ThreadPoolExecutor 平行| JG
            MB -->|ThreadPoolExecutor 平行| JG
        end

    RPT["📊 Report Generator\n報告輸出 · 審閱建議分層 · 雙重驗證標籤整合\nUI：法律依據摘要 + 原始檢索資料原文\n（法條原文框 / 相似先例框，分開顯示）"]
        PARSER --> ALIGN --> DIFF --> RISK --> VA --> LLM
        DIFF -.->|原始文字 vs 解析後文字| COV
        COV -.->|覆蓋率 < 97%| RPT
        LLM -->|高風險 flag，交叉驗證\n（LLM 分析後才觸發）| MA
        LLM -->|高風險 flag，交叉驗證| MB
        JG --> RPT
        PLAYBOOK["📋 三層協商對策（按需，非主流程）\n13 種風險類型 × 首選／折衷／底線立場\n知識庫可編輯，格式錯誤自動退回內建版本\n按鈕觸發，不佔用初次比對時間"]
    end

    subgraph ASKMATRIX["💬 對話式功能（2026-07-05 新增，按需，非主流程）"]
            direction LR
            ASK["💬 報告問答（Ask）\n只根據 key_changes 回答，查無資訊誠實拒答\n含法條原文＋先例相似度（2026-07-06 補上原始欄位）"]
            MATRIX["📋 協商矩陣（Matrix）\n多筆高風險條款批次生成\n訴求／立場／折衷／底線／法律依據 對照表\n可直接列印帶去談判"]
        end
        RPT -->|key_changes| ASK
        RPT -->|key_changes| MATRIX

    subgraph L3["⚖️ Layer 3：協商建議依據檢索（已接入，2026-07-02；原始資料 UI 揭露 2026-07-03）"]
        direction LR
        LAWCACHE["📖 法條快取\n離線查回真實民法／民訴法條文\n同步讀檔，Demo 現場無網路依賴"]
        PRECEDENT["🧭 先例向量檢索\n10 筆先例案例，真實向量嵌入\n本地相似度計算，非關鍵字比對"]
        LAWCACHE -->|法條原文| LLM
        PRECEDENT -->|相似案例＋相似度%| LLM
    end

    subgraph STORE["本地資料"]
        D1["📁 SLA 測試合約組\nv1–v5：可用率／賠償上限\n保護條款／終止條件變更"]
        D2["📁 NDA 測試合約組\n甲方版 vs 乙方修改版"]
        D3["📊 人工標註 Gold Set\n38 筆標註，v2–v5 全覆蓋"]
    end

    subgraph EVAL["驗證指標"]
        E1["📐 High-risk Recall: 100%（5/5）\nOverall Detection: 54%（12/22，2026-07-11 修正）\n樣本: 38 筆標註中 22 筆為 adverse\nMAS pending 率: v4=0% / v3=100%（實測重跑確認）"]
    end

    UI --> API --> PARSER
    D1 --> PARSER
    D2 --> PARSER
    D3 --> EVAL
    EVAL --> RISK
end

subgraph SKILLS["📚 知識庫（法務可編輯，注入各角色 System Prompt）"]
    direction TB
    SK1["📋 風險判斷知識庫\nAgent A + Verification Agent\n共用同一份可編輯知識文件"]
    SK2["💬 協商策略知識庫\nAgent B + 協商摘要 + 三層對策\n三個角色共用，法務可直接編輯調整"]
    SK3["📝 系統總覽文件\nDemo 流程 · 產品路線圖"]
end

subgraph PRINCIPLE["核心設計原則"]
    direction TB
    PR1["Rule Engine 做判斷\n→ LLM 做解釋\n→ MAS 做驗證"]
    PR2["📌 高風險不漏判\n寧可多判不漏判\nrecall 優先於 precision"]
    PR3["🔒 資料不離開企業\nStateless API\n本地部署優先"]
end

SANITIZE["🔒 脫敏中間層（Phase 2 規劃中，非現況）\n自寫 sanitizer + 統一 llm_client chokepoint\n遮身分實體，留數字條件；server 不還原真名"]

subgraph EXT["☁️ 外部服務（External Cloud）"]
    direction TB
    CLAUDE["🟠 Claude API\nclaude-sonnet-4-6\n備援 LLM · MAS Agent"]
    GEMINI["🔵 Gemini API\ngemini-3.1-flash-lite\n主要 LLM · MAS Agent"]
    AZURE["🔷 Azure\nBlob Storage · AD 認證\nApp Insights 監控"]
end

LLM -.->|Phase 2：規劃中，見脫敏規劃文件| SANITIZE
SANITIZE -.->|Phase 2：規劃中| GEMINI

USER --> UI
API -.->|服務啟動時讀取| SK1
API -.->|服務啟動時讀取| SK2
SK1 -->|注入知識| MA
SK1 -->|注入知識| VA
SK2 -->|注入知識| MB
SK2 -->|注入知識| LLM
SK2 -->|注入知識| PLAYBOOK
API -->|按需觸發| PLAYBOOK
API -->|按需觸發| ASK
API -->|按需觸發| MATRIX
ASK -.->|呼叫 LLM Service 內建函式| LLM
MATRIX -.->|呼叫 LLM Service 內建函式| LLM
LLM --> GEMINI
LLM --> CLAUDE
MA --> GEMINI
MB --> GEMINI
AZURE -.->|正式環境部署| D1

classDef done fill:#07131f,stroke:#00e5ff,stroke-width:2px,color:#e6faff;
classDef ext fill:#0a1020,stroke:#7c3aed,stroke-width:2px,color:#eef2ff;
classDef principle fill:#0d1a10,stroke:#4ade80,stroke-width:1.5px,color:#f0fdf4;
classDef pipeline fill:#06111b,stroke:#0f766e,stroke-width:1.5px,color:#ecfeff;
classDef skill fill:#1c1328,stroke:#f472b6,stroke-width:1.5px,color:#fdf2f8;
classDef agent_a fill:#1f0a0a,stroke:#f87171,stroke-width:2px,color:#fff1f2;
classDef agent_b fill:#1a1400,stroke:#fbbf24,stroke-width:2px,color:#fffbeb;
classDef judge fill:#061a10,stroke:#34d399,stroke-width:2px,color:#ecfdf5;
classDef store fill:#0a1a12,stroke:#6ee7b7,stroke-width:1.5px,color:#ecfdf5;
classDef extc fill:#0b1324,stroke:#818cf8,stroke-width:1.5px,color:#eef2ff;
classDef verify fill:#06111b,stroke:#facc15,stroke-width:2px,color:#fefce8;
classDef planned fill:#1a0f0f,stroke:#fb923c,stroke-width:2px,stroke-dasharray: 5 5,color:#fff7ed;

class P1 done;
class MAS done;
class SKILLS skill;
class L3 done;
class ASKMATRIX done;
class EXT ext;
class PRINCIPLE principle;
class PARSER,ALIGN,DIFF,RISK,LLM,RPT pipeline;
class COV verify;
class VA verify;
class PLAYBOOK,ASK,MATRIX pipeline;
class LAWCACHE,PRECEDENT verify;
class SK1,SK2,SK3 skill;
class MA agent_a;
class MB agent_b;
class JG judge;
class D1,D2,D3,EVAL,E1 store;
class CLAUDE,GEMINI,AZURE extc;
class SANITIZE planned;
