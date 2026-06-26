# 開發方式指南

**專案**: Blue-AI 合約比對助理  
**團隊組成**: 業務、SA、Infra（+ 未來招募的 Dev）  
**開發時程**: MVP 2 週，完整版 8-12 週

---

## 📚 目錄

1. [技術棧](#技術棧)
2. [開發方法論](#開發方法論)
3. [開發工作流程](#開發工作流程)
4. [協作模式](#協作模式)
5. [工具鏈](#工具鏈)
6. [程式碼規範](#程式碼規範)
7. [測試策略](#測試策略)
8. [部署流程](#部署流程)

---

## 技術棧

### 後端 (Backend)

```yaml
語言: Python 3.11+
框架: FastAPI
原因: 
  - 自動生成 API 文件（OpenAPI/Swagger）
  - 型別提示（Type Hints）支援良好
  - 非同步處理能力（async/await）
  - 學習曲線較 Django 平緩
  - 效能優異

套件管理: Poetry
原因:
  - 依賴管理比 pip 更可靠
  - 自動處理虛擬環境
  - 支援 lock file（確保團隊環境一致）
```

**核心套件**:
```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.110.0"
uvicorn = "^0.28.0"           # ASGI server
pydantic = "^2.6.0"            # 資料驗證
anthropic = "^0.21.0"          # Claude API SDK
PyMuPDF = "^1.23.0"            # PDF 處理（別名 fitz）
python-multipart = "^0.0.9"   # 檔案上傳
jinja2 = "^3.1.0"              # HTML 模板

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"              # 測試框架
pytest-asyncio = "^0.23.0"    # 非同步測試
black = "^24.0.0"              # 程式碼格式化
ruff = "^0.2.0"                # Linter（比 flake8 快）
mypy = "^1.8.0"                # 型別檢查
httpx = "^0.26.0"              # 測試用 HTTP client
```

### 前端 (Frontend)

**MVP 階段** (Week 1-2):
```yaml
技術: 純 HTML + Vanilla JavaScript
原因:
  - 團隊前端經驗有限
  - 快速驗證功能
  - 無需額外建置工具
  - 專注於後端邏輯
```

**未來優化** (Week 3+):
```yaml
框架: React 18 + TypeScript
狀態管理: Zustand 或 React Context
UI 框架: Ant Design 或 Material-UI
建置工具: Vite
```

### AI/ML

```yaml
模型: Claude API (Anthropic)
  - MVP: claude-sonnet-4-6（平衡效能與成本）
  - 複雜分析: claude-opus-4-7（準確度優先）
  - 簡單任務: claude-haiku-4-5（成本優先）

文字處理:
  - difflib（Python 標準庫）: 基礎比對
  - 未來: spaCy 或 jieba（中文斷詞）
```

### 基礎設施

```yaml
雲端平台: Azure
  - App Service: 後端 API 部署
  - Blob Storage: PDF 檔案儲存
  - Key Vault: 金鑰管理
  - Application Insights: 監控與追蹤

容器化: Docker + Docker Compose
  - 本地開發環境一致性
  - 未來可部署至 Azure Container Apps

版本控制: Git (GitHub 或 Azure Repos)

CI/CD: Azure DevOps Pipelines（未來設置）
```

### 資料庫

**MVP 階段**:
```yaml
資料庫: SQLite（檔案型資料庫）
原因:
  - 零設定
  - 適合 MVP 驗證
  - 可輕鬆遷移至 PostgreSQL
```

**生產環境**:
```yaml
資料庫: Azure Database for PostgreSQL
ORM: SQLAlchemy 2.0
遷移工具: Alembic
```

---

## 開發方法論

### Scrum 框架

```yaml
Sprint 長度: 2 週

Sprint 活動:
  - Sprint Planning: 每兩週一（2 小時）
  - Daily Standup: 每日 10:00（15 分鐘，線上或實體）
  - Sprint Review: 每兩週五下午（1 小時）
  - Sprint Retrospective: Review 後（1 小時）

工作可視化: Azure DevOps Board
  - Backlog: 待辦事項
  - To Do: 本 Sprint 待做
  - In Progress: 進行中（限制 WIP = 每人最多 2 項）
  - In Review: 待審查
  - Done: 完成
```

### User Story 格式

```gherkin
作為 [角色]
我想要 [功能]
以便 [價值/目的]

驗收標準:
Given [前置條件]
When [動作]
Then [預期結果]
```

### Definition of Done (DoD)

每個 User Story 完成必須:
- [x] 程式碼通過 Black 格式化
- [x] 程式碼通過 Ruff Linting（無錯誤）
- [x] 型別檢查通過（mypy）
- [x] 有對應的單元測試（MVP 階段不強制 80% 覆蓋率）
- [x] 測試全部通過
- [x] 在本地環境可執行
- [x] 業務人員實際測試通過
- [x] Code Review 完成（至少 1 人）
- [x] 已合併至 `develop` 分支

---

## 開發工作流程

### 分支策略（簡化版 Git Flow）

```
main (正式版本，受保護)
  └─ develop (開發主分支)
       ├─ feature/US1-upload-contract (功能分支)
       ├─ feature/US2-extract-pdf (功能分支)
       └─ hotfix/fix-upload-error (緊急修復)
```

**分支命名規則**:
```bash
feature/<ticket-id>-<short-description>
# 範例: feature/US1-upload-contract

hotfix/<issue-description>
# 範例: hotfix/pdf-parsing-crash
```

### 每日開發流程

#### 早上（9:00-12:00）

```bash
# 1. 同步最新程式碼
git checkout develop
git pull origin develop

# 2. 建立或切換到功能分支
git checkout -b feature/US1-upload-contract
# 或
git checkout feature/US1-upload-contract

# 3. 開始開發前：確認今日目標（參考 Azure DevOps Board）

# 4. 10:00 參加 Daily Standup（15 分鐘）
#    回答三個問題：
#    - 昨天做了什麼？
#    - 今天要做什麼？
#    - 有什麼阻礙？

# 5. 開發
#    - 遵循 TDD（可選）：先寫測試 -> 寫程式碼 -> 跑測試
#    - 頻繁 commit（每完成一個小功能就 commit）
```

#### 中午（12:00-13:00）

```bash
# 休息！重要！
```

#### 下午（13:00-18:00）

```bash
# 6. 繼續開發

# 7. 定期執行程式碼品質檢查
poetry run black .                # 格式化
poetry run ruff check .           # Linting
poetry run mypy src/              # 型別檢查
poetry run pytest                 # 執行測試

# 8. 完成階段性功能後：提交 commit
git add src/api/contracts.py
git commit -m "feat(upload): 實作 PDF 檔案上傳 API

- 新增 POST /api/v1/contracts/upload 端點
- 檔案大小限制 10MB
- 僅接受 PDF 格式
- 回傳 file_id 供後續處理

Refs: #US1"

# 9. 推送到遠端
git push origin feature/US1-upload-contract

# 10. 如果功能完成：建立 Pull Request (PR)
#     - 在 GitHub/Azure Repos 上建立 PR
#     - 指定 Reviewer（至少 1 人）
#     - 連結對應的 Work Item
```

#### 晚上（可選）

```bash
# 如果有緊急問題或想多做一點
# 但要注意 Work-Life Balance！
```

### Pull Request (PR) 流程

#### 1. 建立 PR

```markdown
標題: [US1] 實作合約上傳功能

描述:
## 變更內容
- 新增 POST /api/v1/contracts/upload API 端點
- 實作檔案驗證（格式、大小）
- 新增單元測試

## 測試
- [x] 上傳正常 PDF（成功）
- [x] 上傳非 PDF 檔案（失敗，錯誤訊息正確）
- [x] 上傳 >10MB 檔案（失敗，錯誤訊息正確）
- [x] 單元測試通過（15 個測試案例）

## 截圖（如適用）
[貼上 API 測試結果截圖]

## Checklist
- [x] 程式碼已格式化（Black）
- [x] Linting 通過（Ruff）
- [x] 型別檢查通過（mypy）
- [x] 測試通過
- [x] 已更新文件（如需要）

Refs: #123
```

#### 2. Code Review

**Reviewer 檢查項目**:
- [ ] 程式碼邏輯正確
- [ ] 符合專案規範（見下方「程式碼規範」）
- [ ] 沒有明顯的安全問題（SQL injection, XSS 等）
- [ ] 測試覆蓋核心邏輯
- [ ] 命名清晰易懂
- [ ] 沒有重複程式碼（DRY 原則）
- [ ] 效能考量（如適用）

**Review 回饋範例**:
```markdown
# 建議修改
src/api/contracts.py:42
建議加上檔案類型驗證，目前僅檢查副檔名，可能被繞過。
可使用 python-magic 檢查實際檔案類型。

# 問題
src/services/pdf_service.py:28
這裡會拋出未處理的例外，建議加上 try-except。

# 讚賞
測試案例寫得很完整！👍
```

#### 3. 修正後合併

```bash
# 修正 Review 意見
git add .
git commit -m "fix(upload): 加強檔案類型驗證"
git push origin feature/US1-upload-contract

# PR 獲得批准後
# 在網頁上點擊 "Merge" 或使用 CLI
git checkout develop
git pull origin develop
git merge feature/US1-upload-contract
git push origin develop

# 刪除已合併的分支
git branch -d feature/US1-upload-contract
git push origin --delete feature/US1-upload-contract
```

---

## 協作模式

### 配對程式設計（Pair Programming）

**適用時機**（Week 0-2 高頻使用）:
- 新手學習新技術時
- 複雜邏輯實作
- 關鍵功能開發
- Debug 困難問題

**角色**:
- **Driver（駕駛員）**: 實際寫程式碼
- **Navigator（領航員）**: 思考邏輯、查文件、提醒

**實作方式**:
```yaml
方式 1: 螢幕分享 + 遠端控制
  工具: Teams 或 VS Code Live Share
  適合: 遠端協作

方式 2: 實體配對
  工具: 一台電腦 + 大螢幕
  適合: 同地點工作

時間分配:
  - 每 25 分鐘交換角色（番茄鐘）
  - 每 2 小時休息 15 分鐘
```

**建議配對組合**（Week 1-2）:

| 時段           | 配對組合    | 目標                           |
|----------------|-------------|--------------------------------|
| 週一上午       | SA + 業務   | 一起設計 Claude Prompt         |
| 週一下午       | SA + Infra  | 討論部署架構                   |
| 週二-週四上午  | SA + 業務   | SA 寫程式，業務學習 Python      |
| 週三下午       | 全員        | Code Review Session            |
| 週五上午       | SA + 業務   | 一起測試與 Debug               |

### 知識分享

**每週三下午: Tech Sharing（1 小時）**

```yaml
Week 1: SA 分享「FastAPI 快速入門」
Week 2: 業務分享「合約條款風險識別」
Week 3: Infra 分享「Azure 部署最佳實踐」
Week 4: Dev（新人）分享「我如何快速上手專案」
```

**文件協作**:
- 所有文件放在 `docs/` 目錄
- 使用 Markdown 格式
- 重要決策記錄在 `docs/decisions/ADR-XXX.md`（Architecture Decision Record）

---

## 工具鏈

### 本地開發環境設置

#### 1. 安裝必要工具

```bash
# macOS
brew install python@3.11
brew install poetry
brew install git

# Windows
# 從官網下載安裝 Python 3.11+
# 安裝 Poetry: https://python-poetry.org/docs/#installation
```

#### 2. Clone 專案

```bash
cd ~/Documents
git clone <repository-url> bule-ai-team
cd bule-ai-team
```

#### 3. 安裝依賴

```bash
# 安裝 Python 依賴
poetry install

# 啟動虛擬環境
poetry shell

# 驗證安裝
python --version  # 應該顯示 3.11+
poetry --version
```

#### 4. 設定環境變數

```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 填入實際值
# macOS/Linux
nano .env

# Windows
notepad .env
```

`.env` 內容範例:
```env
# Claude API
ANTHROPIC_API_KEY=sk-ant-api03-xxx

# Azure (如已設定)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...

# 應用設定
DEBUG=True
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=10
```

#### 5. 啟動開發伺服器

```bash
# 方式 1: 直接執行
poetry run uvicorn src.main:app --reload --port 8000

# 方式 2: 使用專案腳本（建立後）
poetry run python -m src.main

# 訪問 API 文件
# 瀏覽器打開: http://localhost:8000/docs
```

### IDE 設定（VS Code）

**必裝擴充套件**:
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
    "ms-azuretools.vscode-docker",
    "redhat.vscode-yaml",
    "yzhang.markdown-all-in-one"
  ]
}
```

**設定檔** (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.testing.pytestEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.rulers": [100]
  }
}
```

### Azure DevOps Board 設定

**欄位（Columns）**:
```
Backlog -> To Do -> In Progress -> In Review -> Done
```

**Work Item Types**:
- **Epic**: 大功能（例如「合約比對 MVP」）
- **User Story**: 使用者故事（例如「上傳合約」）
- **Task**: 技術任務（例如「實作 PDF 萃取」）
- **Bug**: 缺陷

**範例 Board 設定**:
```
Epic: 合約比對 MVP
  ├─ User Story #1: 上傳合約
  │   ├─ Task 1.1: 建立 FastAPI 專案 (SA, 4h) [Done]
  │   ├─ Task 1.2: 實作 upload API (SA, 6h) [In Progress]
  │   └─ Task 1.3: 建立上傳表單 (業務, 4h) [To Do]
  ├─ User Story #2: 萃取 PDF
  └─ ...
```

---

## 程式碼規範

### Python 風格指南

#### 1. 命名規範

```python
# 模組/套件: 小寫底線分隔
# 檔案: pdf_extractor.py, contract_service.py

# 類別: PascalCase
class ContractComparison:
    pass

class PDFExtractor:
    pass

# 函數/變數: snake_case
def extract_text_from_pdf(file_path: str) -> str:
    page_count = 0
    extracted_text = ""
    return extracted_text

# 常數: 大寫底線分隔
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = [".pdf"]

# 私有成員: 前綴單底線
class PDFProcessor:
    def _internal_method(self):
        pass
    
    def public_method(self):
        self._internal_method()
```

#### 2. 型別提示（Type Hints）

```python
from typing import List, Dict, Optional, Union
from pathlib import Path

# 必須為函數參數和返回值加上型別提示
def process_contract(
    file_path: Path,
    language: str = "zh-TW",
    extract_tables: bool = False
) -> Dict[str, any]:
    """處理合約文件。
    
    Args:
        file_path: PDF 檔案路徑
        language: 語言代碼
        extract_tables: 是否萃取表格
    
    Returns:
        包含萃取結果的字典
    
    Raises:
        FileNotFoundError: 檔案不存在
        PDFProcessingError: PDF 處理失敗
    """
    result: Dict[str, any] = {
        "text": "",
        "pages": 0
    }
    return result

# 複雜型別使用 TypeAlias（Python 3.12+）或 NewType
from typing import TypeAlias

UserId: TypeAlias = str
ContractId: TypeAlias = str

def get_contract(contract_id: ContractId) -> Optional[Dict]:
    pass
```

#### 3. Docstrings（Google Style）

```python
def compare_contracts(
    original: str,
    revised: str,
    sensitivity: float = 0.95
) -> List[Dict[str, any]]:
    """比對兩份合約的差異。
    
    使用 difflib 演算法進行逐字比對，識別新增、刪除、修改的內容。
    
    Args:
        original: 原始合約文字
        revised: 修訂合約文字
        sensitivity: 比對敏感度（0.0-1.0），越高越嚴格
    
    Returns:
        差異列表，每個元素包含:
        - type: 'addition' | 'deletion' | 'modification'
        - content: 變更內容
        - position: 行號
        
    Raises:
        ValueError: sensitivity 超出範圍
        
    Examples:
        >>> original = "甲方應支付 100 萬元"
        >>> revised = "甲方應支付 200 萬元"
        >>> diffs = compare_contracts(original, revised)
        >>> len(diffs)
        1
        >>> diffs[0]['type']
        'modification'
    """
    if not 0.0 <= sensitivity <= 1.0:
        raise ValueError("sensitivity must be between 0.0 and 1.0")
    
    # 實作...
    return []
```

#### 4. 錯誤處理

```python
# 自訂例外
class PDFProcessingError(Exception):
    """PDF 處理相關錯誤"""
    pass

class InvalidFileFormatError(PDFProcessingError):
    """無效的檔案格式"""
    pass

# 使用範例
def extract_pdf(file_path: Path) -> str:
    """萃取 PDF 文字"""
    if not file_path.exists():
        raise FileNotFoundError(f"檔案不存在: {file_path}")
    
    if file_path.suffix.lower() != ".pdf":
        raise InvalidFileFormatError(
            f"不支援的檔案格式: {file_path.suffix}"
        )
    
    try:
        # 使用 PyMuPDF 萃取
        import fitz
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        raise PDFProcessingError(f"PDF 處理失敗: {e}") from e
    finally:
        if 'doc' in locals():
            doc.close()
```

#### 5. FastAPI 路由規範

```python
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/v1/contracts", tags=["contracts"])

# Request/Response Models
class ContractUploadResponse(BaseModel):
    """合約上傳回應"""
    file_id: str
    filename: str
    size_bytes: int
    upload_timestamp: str

class ErrorResponse(BaseModel):
    """錯誤回應"""
    error_code: str
    message: str
    details: Optional[Dict[str, any]] = None

# API 端點
@router.post(
    "/upload",
    response_model=ContractUploadResponse,
    status_code=201,
    summary="上傳合約文件",
    description="上傳 PDF 格式的合約文件，檔案大小限制 10MB"
)
async def upload_contract(
    file: UploadFile = File(..., description="PDF 檔案")
) -> ContractUploadResponse:
    """上傳合約文件端點"""
    
    # 驗證檔案類型
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "INVALID_FILE_FORMAT",
                "message": "僅支援 PDF 格式",
                "allowed_formats": [".pdf"]
            }
        )
    
    # 驗證檔案大小
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail={
                "error_code": "FILE_TOO_LARGE",
                "message": "檔案大小超過限制",
                "max_size_mb": 10
            }
        )
    
    # 處理上傳...
    file_id = "generated-uuid"
    
    return ContractUploadResponse(
        file_id=file_id,
        filename=file.filename,
        size_bytes=len(contents),
        upload_timestamp="2026-05-28T10:30:00Z"
    )
```

---

## 測試策略

### 測試金字塔

```
        /\
       /  \      E2E Tests (少量，10%)
      /____\     - 完整流程測試
     /      \    Integration Tests (中量，30%)
    /________\   - API 整合測試
   /          \  Unit Tests (大量，60%)
  /____________\ - 函數/類別測試
```

### 單元測試範例

```python
# tests/unit/test_pdf_extractor.py
import pytest
from pathlib import Path
from src.services.pdf_extractor import PDFExtractor, PDFProcessingError

@pytest.fixture
def sample_pdf_path():
    """測試用 PDF 檔案"""
    return Path("tests/fixtures/sample_contract.pdf")

@pytest.fixture
def extractor():
    """PDF 萃取器實例"""
    return PDFExtractor()

def test_extract_text_success(extractor, sample_pdf_path):
    """測試成功萃取 PDF 文字"""
    result = extractor.extract_text(sample_pdf_path)
    
    assert isinstance(result, str)
    assert len(result) > 0
    assert "甲方" in result or "乙方" in result  # 合約常見詞彙

def test_extract_text_file_not_found(extractor):
    """測試檔案不存在的情況"""
    non_existent = Path("non_existent.pdf")
    
    with pytest.raises(FileNotFoundError):
        extractor.extract_text(non_existent)

def test_extract_text_invalid_format(extractor, tmp_path):
    """測試無效檔案格式"""
    invalid_file = tmp_path / "test.txt"
    invalid_file.write_text("not a pdf")
    
    with pytest.raises(PDFProcessingError, match="不支援的檔案格式"):
        extractor.extract_text(invalid_file)

@pytest.mark.parametrize("filename,expected_pages", [
    ("single_page.pdf", 1),
    ("multi_page.pdf", 5),
    ("complex_contract.pdf", 10),
])
def test_page_count(extractor, filename, expected_pages):
    """測試頁數計算"""
    pdf_path = Path(f"tests/fixtures/{filename}")
    result = extractor.extract_text(pdf_path)
    
    assert result.page_count == expected_pages
```

### 整合測試範例

```python
# tests/integration/test_api_upload.py
from fastapi.testclient import TestClient
from src.main import app
import io

client = TestClient(app)

def test_upload_valid_pdf():
    """測試上傳有效的 PDF"""
    # 準備測試檔案
    pdf_content = b"%PDF-1.4..."  # 實際 PDF 內容
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    
    response = client.post("/api/v1/contracts/upload", files=files)
    
    assert response.status_code == 201
    data = response.json()
    assert "file_id" in data
    assert data["filename"] == "test.pdf"

def test_upload_invalid_format():
    """測試上傳非 PDF 檔案"""
    files = {"file": ("test.txt", io.BytesIO(b"text"), "text/plain")}
    
    response = client.post("/api/v1/contracts/upload", files=files)
    
    assert response.status_code == 400
    assert "INVALID_FILE_FORMAT" in response.text
```

### 執行測試

```bash
# 執行所有測試
poetry run pytest

# 執行特定檔案
poetry run pytest tests/unit/test_pdf_extractor.py

# 執行特定測試函數
poetry run pytest tests/unit/test_pdf_extractor.py::test_extract_text_success

# 顯示詳細輸出
poetry run pytest -v

# 顯示 print 輸出
poetry run pytest -s

# 測試覆蓋率報告
poetry run pytest --cov=src --cov-report=html
# 報告在 htmlcov/index.html
```

---

## 部署流程

### MVP 階段（本地執行）

```bash
# 1. 確保所有測試通過
poetry run pytest

# 2. 啟動服務
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000

# 3. 團隊成員訪問
# http://<開發者 IP>:8000
```

### Docker 化（Week 3+）

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安裝 Poetry
RUN pip install poetry

# 複製依賴定義
COPY pyproject.toml poetry.lock ./

# 安裝依賴（不含開發依賴）
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# 複製原始碼
COPY src/ ./src/

# 暴露端口
EXPOSE 8000

# 啟動命令
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DEBUG=False
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped

  # 未來可加入資料庫、Redis 等
```

### Azure 部署（未來）

```bash
# 使用 Azure CLI
az login
az webapp up --name blue-ai-contract-diff --runtime PYTHON:3.11
```

---

## 總結

### 新團隊的開發建議

**Week 0** (現在):
- ✅ 設定開發環境（每個人）
- ✅ 熟悉工具鏈（Git、Poetry、VS Code）
- ✅ 第一次 commit 與 PR（練習流程）

**Week 1-2** (MVP):
- 👥 高強度配對程式（SA + 業務）
- 📝 每日 Standup 嚴格執行
- 🧪 邊開發邊測試
- 📊 每週五 Demo

**Week 3-4** (優化):
- 🔧 重構程式碼
- 📚 補充文件
- 🚀 準備部署

**Week 5+** (擴展):
- ➕ 新增進階功能
- 🏗️ 改善架構
- 📈 效能優化

---

**需要協助時**:
- 技術問題: 優先查文件，再問 SA
- 流程問題: 參考本文件
- Claude Code: 使用 `/help` 指令

**保持溝通、頻繁整合、持續改進！** 🚀
