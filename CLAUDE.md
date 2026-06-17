# Claude Code 專案指南

本文件為 Claude Code 提供專案特定的指導原則與配置。

## 專案概覽

**專案名稱**: Blue-AI 企業智能助理平台  
**專案類型**: 企業級 AI 應用開發  
**主要技術**: Python, TypeScript, React, Claude API, Azure Services  
**開發模式**: Agile / Scrum

## 專案目標

開發 AI 驅動的**合約文件比對助理**，自動化合約審查與風險分析工作：

- 比對合約版本差異
- 識別條款變更（新增、修改、刪除）
- 風險條款標註與分析
- 生成比對報告與建議

## 目錄結構規範

```
bule-ai-team/
├── .claude/
│   ├── skills/              # Claude Code Skills（已建立）
│   └── settings.json        # 專案設定
├── docs/
│   ├── specs/               # 技術規格
│   ├── architecture/        # 架構文件
│   ├── api/                 # API 文件
│   └── guides/              # 開發指南
├── src/
│   ├── api/                 # API 層
│   ├── services/            # 業務邏輯層
│   │   └── contract/        # 合約比對服務
│   ├── integrations/        # 第三方整合
│   │   ├── claude/          # Claude API
│   │   └── azure/           # Azure Services (Blob Storage, Document Intelligence)
│   ├── models/              # 資料模型
│   ├── utils/               # 工具函數
│   └── config/              # 配置檔案
├── frontend/
│   ├── src/
│   │   ├── components/      # React 元件
│   │   ├── pages/           # 頁面
│   │   ├── services/        # API 呼叫
│   │   └── utils/           # 前端工具
│   └── public/
├── tests/
│   ├── unit/                # 單元測試
│   ├── integration/         # 整合測試
│   └── e2e/                 # E2E 測試
├── deploy/
│   ├── docker/              # Docker 配置
│   └── k8s/                 # Kubernetes 配置
└── scripts/                 # 工具腳本
```

## 開發規範

### 程式碼風格

**Python**:
- 使用 Black 格式化（line-length=100）
- 遵循 PEP 8
- Type hints 必須加上
- Docstrings 使用 Google Style

```python
def compare_contracts(
    original_file: str,
    revised_file: str,
    analysis_level: str = "standard"
) -> ContractComparisonResult:
    """比對兩份合約文件並分析差異。

    Args:
        original_file: 原始合約檔案路徑
        revised_file: 修訂合約檔案路徑
        analysis_level: 分析深度 ("basic", "standard", "comprehensive")

    Returns:
        ContractComparisonResult: 包含差異分析與風險評估

    Raises:
        ContractParsingError: 合約解析失敗時
    """
    pass
```

**TypeScript/React**:
- 使用 Prettier 格式化
- ESLint 規則嚴格遵循
- 元件使用 Function Component + Hooks
- 避免 `any` type

```typescript
interface ContractComparison {
  id: string;
  originalFile: string;
  revisedFile: string;
  comparisonDate: Date;
  status: 'pending' | 'completed' | 'failed';
  differences: ContractDifference[];
  riskLevel: 'low' | 'medium' | 'high';
}

const ContractComparisonCard: React.FC<{ comparison: ContractComparison }> = ({ comparison }) => {
  // 實作
};
```

### Git 工作流程

- **分支策略**: Git Flow
  - `main`: 正式版本
  - `develop`: 開發主分支
  - `feature/*`: 功能開發
  - `hotfix/*`: 緊急修復
  
- **Commit 訊息格式**:
  ```
  <type>(<scope>): <subject>
  
  <body>
  
  <footer>
  ```
  
  Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
  
  範例:
  ```
  feat(contract): 新增合約差異視覺化功能
  
  - 使用 diff 演算法標註變更段落
  - 支援 PDF/DOCX 格式
  - 風險等級自動分類
  
  Closes #123
  ```

### 測試要求

- **單元測試覆蓋率**: >80%
- **整合測試**: 所有 API 端點必須有測試
- **E2E 測試**: 核心使用者流程必須覆蓋

### API 設計原則

- RESTful API 設計
- 統一錯誤處理格式
- API 版本控制 (`/api/v1/...`)
- 所有 API 必須有 rate limiting
- 敏感資料傳輸使用 HTTPS + JWT

```python
# 統一回應格式
{
  "success": true,
  "data": { ... },
  "error": null,
  "timestamp": "2026-05-28T10:30:00Z"
}

# 錯誤格式
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_INPUT",
    "message": "音訊檔案格式不支援",
    "details": { ... }
  },
  "timestamp": "2026-05-28T10:30:00Z"
}
```

## AI/LLM 使用規範

### Claude API

- **模型選擇**:
  - 複雜分析: `claude-sonnet-4-6` 或 `claude-opus-4-7`
  - 簡單任務: `claude-haiku-4-5`
  
- **Prompt Engineering**:
  - 使用 System Prompt 定義角色與規則
  - 提供清晰的範例 (Few-shot learning)
  - 使用 XML tags 結構化輸入/輸出
  
- **成本優化**:
  - 啟用 Prompt Caching（重複的 system/context）
  - 避免不必要的長文本
  - 批次處理優先於單筆

```python
# 範例: 合約比對 Prompt
system_prompt = """你是專業的法律合約分析助理。
任務：比對兩份合約版本並識別重要差異與潛在風險。

輸出格式：
<comparison>
  <summary>主要變更摘要</summary>
  <changes>
    <change type="addition|modification|deletion" risk_level="low|medium|high">
      <location>條款位置（章節、條號）</location>
      <original>原始內容</original>
      <revised>修訂內容</revised>
      <impact>影響分析</impact>
      <recommendation>建議</recommendation>
    </change>
  </changes>
  <risk_assessment>
    <overall_risk>low|medium|high</overall_risk>
    <key_concerns>主要關注點列表</key_concerns>
  </risk_assessment>
</comparison>
"""
```

### Azure Services

- **Document Intelligence** (原 Form Recognizer): PDF/DOCX 文件解析與文字擷取
- **Blob Storage**: 合約檔案儲存
- **Key Vault**: 金鑰管理
- **Application Insights**: 監控與追蹤

所有 Azure 服務連線資訊必須從環境變數讀取，不可寫死在程式碼中。

## 安全性要求

### 必須遵守
- ✅ 所有敏感資料加密（傳輸 + 靜態）
- ✅ API Key / Secret 使用環境變數或 Key Vault
- ✅ 輸入驗證與清理（防止 injection）
- ✅ CORS 正確配置
- ✅ Rate limiting 與防暴力破解
- ✅ 完整的審計日誌

### 禁止事項
- ❌ 不可將 API Key 寫在程式碼中
- ❌ 不可將敏感資料 commit 到 Git
- ❌ 不可使用弱加密演算法
- ❌ 不可在 LOG 中記錄敏感資訊

## 效能要求

- API 回應時間: p95 < 5 秒
- 文件解析處理: 10 頁合約 < 30 秒
- AI 比對分析: 50 頁合約 < 3 分鐘
- 系統可用性: >99.5%
- 並發支援: >50 請求/秒

## Claude Code 特定指導

### 使用 Skills

使用 `/contract-diff` skill 進行合約比對開發：

```bash
# 開發合約比對功能
/contract-diff <合約檔案路徑>

# 測試合約差異分析
/contract-diff --test samples/contract_v1.pdf samples/contract_v2.pdf
```

### 開發工作流程

1. **需求分析**: 定義合約比對需求與風險分類標準
2. **文件解析**: 整合 Azure Document Intelligence 進行文件處理
3. **差異分析**: 實作差異演算法與條款比對邏輯
4. **風險評估**: 使用 Claude API 進行智能風險分析
5. **測試**: 自動產生測試案例（單元、整合、E2E）
6. **部署**: Docker/K8s 配置

### 常用指令範例

```bash
# 產生 API 端點程式碼
"幫我建立合約比對的 POST /api/v1/contracts/compare 端點"

# 產生測試
"為 contract_comparison_service.py 產生單元測試"

# 實作差異分析
"實作合約條款差異識別演算法，需支援 PDF 和 DOCX"

# 整合 Azure Document Intelligence
"整合 Azure Document Intelligence API 進行合約文件解析"

# 產生風險分析提示詞
"產生用於合約風險分析的 Claude API prompt template"

# Debug
"為什麼 PDF 解析會產生亂碼？"
```

## 協作規範

### 溝通管道
- **即時溝通**: Microsoft Teams
- **專案追蹤**: Azure DevOps
- **文件協作**: SharePoint
- **程式碼審查**: GitHub/Azure Repos

### 會議節奏
- **Daily Standup**: 每日 10:00 (15 分鐘)
- **Sprint Planning**: 每兩週一次 (2 小時)
- **Sprint Review**: 每兩週一次 (1 小時)
- **Retrospective**: 每兩週一次 (1 小時)

### 文件要求
- 所有功能必須有對應的技術文件
- API 變更必須更新文件
- 重大決策必須記錄在 ADR (Architecture Decision Record)

## 環境配置

### 開發環境

```bash
# Python 環境
python >= 3.11
poetry install

# Node.js 環境
node >= 20.0.0
npm install

# 環境變數
cp .env.example .env
# 編輯 .env 填入必要資訊
```

### 環境變數範例

```env
# Claude API
ANTHROPIC_API_KEY=sk-ant-...

# Azure Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://...cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=...

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=...
AZURE_STORAGE_CONTAINER_NAME=contracts

# Database
DATABASE_URL=postgresql://...

# Redis (快取)
REDIS_URL=redis://...
```

## 部署

### Docker

```bash
# 建立映像
docker build -t blue-ai-platform:latest .

# 執行
docker-compose up -d
```

### Kubernetes

```bash
# 部署至 K8s
kubectl apply -f deploy/k8s/

# 檢查狀態
kubectl get pods -n blue-ai
```

## 監控與維運

- **應用監控**: Azure Application Insights
- **LOG 管理**: ELK Stack
- **告警**: PagerDuty / Teams
- **效能監控**: Grafana + Prometheus

## 常見問題 (FAQ)

**Q: 支援哪些合約檔案格式？**  
A: 支援 PDF、DOCX、TXT 格式。PDF 使用 Azure Document Intelligence 解析，DOCX 使用 python-docx

**Q: Claude API 成本如何控制？**  
A: 1) 使用 prompt caching（合約模板可重用）2) 選擇 claude-sonnet-4-6（平衡效能與成本）3) 設定用量上限 4) 監控使用量

**Q: 如何處理大型合約檔案上傳？**  
A: 使用 Azure Blob Storage 直接上傳，後端僅處理 URL。檔案大小限制 50MB

**Q: 合約比對的準確率如何？**  
A: 文字差異識別準確率 >95%，風險分類需要人工複核（AI 輔助決策）

**Q: 如何處理掃描版 PDF（圖片）？**  
A: Azure Document Intelligence 支援 OCR，但建議使用文字版 PDF 以提高準確率

## 聯絡資訊

- **專案經理**: [PM Name] - pm@blue-ai.com
- **技術負責人**: [Tech Lead Name] - techlead@blue-ai.com
- **團隊 Slack**: #blue-ai-team

---

**版本**: 1.0  
**最後更新**: 2026-05-28  
**維護者**: Blue-AI Team
