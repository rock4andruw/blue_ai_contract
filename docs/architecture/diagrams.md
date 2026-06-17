# 系統架構圖

**狀態**: 定案  
**最後更新**: 2026-06-17

---

## 系統架構圖（元件層）

```mermaid
flowchart TD
    U[使用者：法務 / PM] --> UI[Web UI<br/>上傳兩份 SLA PDF / DOCX]

    UI --> API[FastAPI Backend]
    API --> AUTH[Azure AD 驗證]
    AUTH --> ORCH[Orchestrator]
    API --> AUDIT[Audit Log<br/>PostgreSQL]

    ORCH --> PARSER[Parser Service<br/>pdfplumber / python-docx]
    PARSER --> ALIGN[Alignment Service<br/>條款切分 / 條款對齊]
    ALIGN --> DIFF[Diff Engine<br/>新增 / 修改 / 刪除]

    DIFF --> RULE[Risk Rule Engine<br/>規則判斷 / 風險旗標 / 初步分級]
    RULE --> RETRIEVE[Retrieval Service<br/>pgvector + metadata<br/>檢索相似條款 / 標準條款]
    RETRIEVE --> LLM[LLM Summary & Negotiation Service<br/>白話摘要 / 3-5 重點 / 協商對策]

    PARSER --> DB[(PostgreSQL + pgvector<br/>contracts / clauses / diff_reports<br/>risk_flags / audit_logs)]
    ALIGN --> DB
    DIFF --> DB
    RULE --> DB
    RETRIEVE --> DB

    LLM --> REPORT[Report Generator]
    REPORT --> DB
    REPORT --> DASH[Dashboard JSON API]
    DASH --> FE[HTML / React 報告頁]
```

---

## 系統運作流程（步驟層）

```mermaid
flowchart LR
    A[上傳舊版 / 新版 SLA] --> B[文件解析]
    B --> C[條款切分]
    C --> D[條款對齊]
    D --> E[差異比對]

    E --> F[Risk Rule Engine<br/>判斷風險類型 / 風險等級 / 觸發原因]
    F --> G[Retrieval Service<br/>查公司標準條款 / 相似案例 / metadata]
    G --> H[LLM Summary Service<br/>白話翻譯 / 重點摘要 / 協商建議]
    H --> I[輸出報告<br/>Dashboard / JSON API]
```

---

## 三層分工圖（判斷層 / 補強層 / 表達層）

```mermaid
flowchart TB
    subgraph S1[Risk Rule Engine：判斷層]
        R1[輸入：diff 結果]
        R2[規則庫<br/>SLA 百分比下降 / 回應時間拉長<br/>新增賠償上限 / 刪除保護條款<br/>終止條件變差 / 費用結構調整]
        R3[輸出：risk_code / risk_level / trigger_reason / evidence]
    end

    subgraph S2[Retrieval Service：補強層]
        Q1[查詢：相似條款]
        Q2[查詢：公司標準 SLA]
        Q3[查詢：metadata / 合約狀態]
    end

    subgraph S3[LLM Summary & Negotiation Service：表達層]
        L1[輸入：已旗標風險 + 條款內容 + 檢索參考]
        L2[輸出：白話摘要]
        L3[輸出：3-5 個重點變更]
        L4[輸出：2-3 個協商對策]
    end

    R1 --> R2 --> R3
    R3 --> Q1
    R3 --> Q2
    R3 --> Q3
    Q1 --> L1
    Q2 --> L1
    Q3 --> L1
    L1 --> L2
    L1 --> L3
    L1 --> L4
```

---

## 資料庫 Schema（主要欄位）

```sql
-- 合約 metadata
CREATE TABLE contracts (
    id UUID PRIMARY KEY,
    filename VARCHAR(255),
    contract_type VARCHAR(50),  -- SLA / NDA / 採購
    version VARCHAR(50),
    uploaded_at TIMESTAMPTZ,
    uploaded_by VARCHAR(100)
);

-- 條款（clause-level，存 embedding）
CREATE TABLE clauses (
    id UUID PRIMARY KEY,
    contract_id UUID REFERENCES contracts(id),
    clause_number VARCHAR(50),  -- 如 "5.2"
    title VARCHAR(255),
    content TEXT,
    embedding VECTOR(1536)
);

-- 差異比對結果
CREATE TABLE diff_reports (
    id UUID PRIMARY KEY,
    original_contract_id UUID REFERENCES contracts(id),
    revised_contract_id UUID REFERENCES contracts(id),
    created_at TIMESTAMPTZ,
    total_changes INT,
    overall_risk_level VARCHAR(10)  -- high / medium / low
);

-- 風險旗標（一對多：一份 diff_report 有多筆）
CREATE TABLE risk_flags (
    id UUID PRIMARY KEY,
    diff_report_id UUID REFERENCES diff_reports(id),
    clause_id UUID REFERENCES clauses(id),
    risk_code VARCHAR(50),       -- RISK_SLA_DEGRADE / RISK_LIABILITY_CAP_ADDED ...
    risk_level VARCHAR(10),      -- high / medium / low
    trigger_reason TEXT,
    old_text TEXT,
    new_text TEXT
);

-- 審計日誌
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    user_id VARCHAR(100),
    action VARCHAR(50),
    resource_id UUID,
    created_at TIMESTAMPTZ
);
```
