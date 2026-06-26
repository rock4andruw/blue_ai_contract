# 新團隊完整規劃手冊

**團隊類型**: 新組建的跨職能團隊  
**成員組成**: 業務 + SA + Infra + 開發  
**專案**: Contract-Diff (合約比對助理)  
**目標**: 從 0 到 1 建立高效能 AI 團隊

---

## 📋 執行摘要

### 為什麼新團隊需要完整規劃？

```
❌ 錯誤假設: "新團隊 = 經驗豐富團隊 - 經驗"
✅ 正確認知: "新團隊需要建立共同語言、流程、信任"
```

**新團隊的特殊挑戰**:
1. 🔴 **職責不清** - 誰做什麼？邊界在哪？
2. 🟡 **技能缺口** - AI/ML 經驗可能不足
3. 🟡 **流程缺失** - 沒有 SOP、沒有最佳實踐
4. 🟢 **工具分散** - 每個人用不同工具
5. 🟢 **溝通成本高** - 不了解彼此的工作方式

**因此，是的，你需要完整規劃！但是...**

> **完整 ≠ 龐大**  
> **完整 = 涵蓋所有關鍵面向，但保持精實**

---

## 🎯 新團隊 4 階段規劃

```
階段 0: 團隊建立 (Week 0)        ← 你在這裡
   ↓
階段 1: MVP 驗證 (Week 1-2)      ← 技術可行性
   ↓
階段 2: 流程建立 (Week 3-4)      ← 團隊協作
   ↓
階段 3: 規模化 (Week 5-12)       ← 完整產品
```

---

## 🚀 階段 0: 團隊建立 (本週)

### 📊 現有團隊盤點

#### 步驟 1: 填寫團隊技能矩陣

| 成員 | 角色 | Python | AI/ML | Cloud | 前端 | SQL | Git | 專案經驗 |
|------|------|--------|-------|-------|------|-----|-----|----------|
| [名字] | 業務 | ? | ? | ? | ? | ? | ? | ?年 |
| [名字] | SA | ? | ? | ? | ? | ? | ? | ?年 |
| [名字] | Infra | ? | ? | ? | ? | ? | ? | ?年 |
| [名字] | Dev | ? | ? | ? | ? | ? | ? | ?年 |

**評分標準**:
- 0 = 完全不會
- 1 = 聽過但沒用過
- 2 = 用過但不熟練
- 3 = 熟練，可獨立完成
- 4 = 專家，可指導他人

**行動**: 
```
□ 每個人自評（誠實填寫）
□ 識別技能缺口
□ 決定: 培訓 vs 招聘 vs 外包
```

---

#### 步驟 2: 定義清晰的角色與職責

**問題**: 新團隊最大的問題是「不知道誰該做什麼」

**解決方案**: RACI 矩陣

| 任務 | 業務 | SA | Infra | 開發 |
|------|------|-------|-------|------|
| **需求定義** | R,A | C | I | I |
| **技術架構設計** | I | R,A | C | C |
| **資料庫設計** | I | C | I | R,A |
| **API 開發** | I | C | I | R,A |
| **基礎設施** | I | C | R,A | C |
| **測試** | C | C | I | R,A |
| **部署** | I | C | R | A |
| **文件撰寫** | C | R | C | A |

**圖例**:
- **R** (Responsible): 執行者
- **A** (Accountable): 負責人（最終決策）
- **C** (Consulted): 諮詢對象
- **I** (Informed): 知會對象

**範例**:
```
需求定義:
- 業務: R,A (主導需求收集與定義)
- SA: C (提供技術可行性建議)
- Infra: I (了解需求)
- 開發: I (了解需求)

API 開發:
- 業務: I (知道進度)
- SA: C (架構審查)
- Infra: I (了解部署需求)
- 開發: R,A (實作與負責)
```

---

#### 步驟 3: 建立溝通節奏

**新團隊需要高頻溝通** (隨時間遞減)

**Week 0-2** (團隊建立期):
```
□ Daily Standup: 每天 15 分鐘
   - 昨天做了什麼？
   - 今天要做什麼？
   - 有什麼阻礙？

□ Pairing Session: 每天 2 小時
   - 業務 + SA: 需求澄清
   - SA + Dev: 架構設計
   - Dev + Infra: 環境建置
   
□ Weekly Review: 每週五 1 小時
   - Demo 本週成果
   - 回顧流程
   - 規劃下週
```

**Week 3-4** (流程建立期):
```
□ Daily Standup: 每天 10 分鐘
□ Bi-weekly Sprint Review: 2 週一次
□ Retrospective: 2 週一次
```

**Week 5+** (成熟期):
```
□ Daily Standup: 可選（async 更新）
□ Sprint Review/Planning: 2 週一次
□ Retrospective: 2 週一次
```

---

#### 步驟 4: 統一工具鏈

**問題**: 每個人用不同工具 → 協作困難

**解決方案**: Week 0 就確定工具

| 用途 | 工具 | 負責人 | 完成時間 |
|------|------|--------|----------|
| **程式碼管理** | GitHub / Azure Repos | Infra | Day 1 |
| **專案追蹤** | Azure DevOps / Jira | SA | Day 1 |
| **文件協作** | Notion / Confluence | 業務 | Day 1 |
| **溝通** | Slack / Teams | 全員 | Day 1 |
| **設計** | Figma / Draw.io | SA | Day 2 |
| **CI/CD** | GitHub Actions / Azure Pipelines | Infra | Week 1 |
| **監控** | Grafana / Azure Monitor | Infra | Week 2 |

**行動清單**:
```
□ Day 1: 建立 GitHub repo
□ Day 1: 建立 Slack channel (#contract-diff)
□ Day 1: 建立 ADO 專案
□ Day 2: 所有人完成工具帳號設定
□ Day 2: 寫一份「工具使用指南」
```

---

#### 步驟 5: 技能培訓計劃

**識別缺口** → **制定培訓計劃**

**假設缺口**（根據典型新團隊）:
```
業務人員:
  缺: AI/ML 基礎知識、API 概念
  培訓: 1天 AI 101 工作坊
  
SA:
  缺: Claude API 使用、Legal-BERT
  培訓: 2天 hands-on 實作
  
Infra:
  缺: Docker、Kubernetes、ML 部署
  培訓: 1週線上課程 + 實作
  
開發:
  缺: NLP、transformers、Claude API
  培訓: 1週線上課程 + pair programming
```

**Week 0 培訓計劃**:
```
Day 1 (全員): 
  上午: 專案 Kick-off
  下午: AI/ML 基礎工作坊 (外部講師或 Tech Lead)

Day 2-3 (分組):
  業務組: 使用者訪談技巧、需求文件撰寫
  技術組: Python + Claude API hands-on
  Infra組: Docker 實作

Day 4 (全員):
  上午: 技術架構 walkthrough
  下午: 第一個 Hello World (全員一起寫)

Day 5 (全員):
  回顧與規劃 Sprint 1
```

---

### 🎯 階段 0 交付物 (Week 0 結束前)

**必須完成**:
- ✅ 團隊技能矩陣填寫完畢
- ✅ RACI 矩陣定義並確認
- ✅ 所有工具帳號設定完成
- ✅ GitHub repo 建立 + 所有人有權限
- ✅ 第一個 "Hello World" 程式跑起來
- ✅ Sprint 1 計劃完成

**檢驗標準**:
```
□ 每個人知道自己的職責
□ 每個人知道找誰問什麼問題
□ 每個人會用基本工具（Git, Slack, ADO）
□ 所有人能在本機跑起專案
```

---

## 🔨 階段 1: MVP 驗證 (Week 1-2)

### 目標: 驗證技術可行性 + 建立協作模式

**這個階段的重點**:
1. ✅ 技術驗證（能不能做）
2. ✅ 成本驗證（Claude API 多少錢）
3. ✅ 價值驗證（Stakeholders 認不認可）
4. ✅ 協作驗證（團隊合作順不順）

---

### Week 1: 基礎建設 + 第一個功能

#### Day 1-2: 環境建置（全員參與）

**Infra 主導，其他人協助**

```bash
# Infra 準備 Docker Compose
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
  
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=dev123
  
  redis:
    image: redis:7

# 全員一起跑
docker-compose up
```

**目標**: 每個人的本機都能跑起開發環境

**業務人員**: 
- 準備 2-3 份測試用合約（不同版本）
- 撰寫「測試腳本」（如何驗證結果）

**SA**: 
- 設計 API 規格（簡化版）
- 畫流程圖

**開發**: 
- 建立專案結構
- 實作第一個 endpoint

**Infra**: 
- Docker 環境
- CI/CD 基礎（GitHub Actions）

---

#### Day 3-5: 第一個功能（Pair Programming）

**功能**: PDF 文字提取 + 基礎比對

**Pair 1: 業務 + SA**
```
任務: 定義「好的比對報告」長什麼樣
產出: 報告範本（Markdown）

範例:
# 合約比對報告

## 基本資訊
- 舊版本: contract_v1.pdf
- 新版本: contract_v2.pdf
- 比對時間: 2026-05-29 10:30

## 變更摘要
- 新增: 3 處
- 修改: 7 處
- 刪除: 2 處

## 詳細差異
### 第 5.2 條 - 服務水準
**舊**: 99.9%
**新**: 99.5%
**風險**: 🔴 高
...
```

**Pair 2: Dev + Infra**
```python
# 任務: 實作 PDF 提取
# src/services/document/extractor.py

import fitz  # PyMuPDF

class PDFExtractor:
    def extract_text(self, pdf_path: str) -> str:
        """提取 PDF 文字"""
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    
    def extract_metadata(self, pdf_path: str) -> dict:
        """提取 PDF 中繼資料"""
        doc = fitz.open(pdf_path)
        return {
            'page_count': len(doc),
            'author': doc.metadata.get('author'),
            'creation_date': doc.metadata.get('creationDate'),
        }

# 測試
if __name__ == "__main__":
    extractor = PDFExtractor()
    text = extractor.extract_text("test.pdf")
    print(f"Extracted {len(text)} characters")
```

**Pair 3: SA + Dev**
```python
# 任務: 實作比對邏輯
# src/services/contract/comparator.py

from difflib import SequenceMatcher, unified_diff

class ContractComparator:
    def compare(self, old_text: str, new_text: str) -> dict:
        """比對兩份文字"""
        # 計算相似度
        similarity = SequenceMatcher(None, old_text, new_text).ratio()
        
        # 產生 diff
        diff = list(unified_diff(
            old_text.splitlines(),
            new_text.splitlines(),
            lineterm=''
        ))
        
        return {
            'similarity': similarity,
            'diff': diff,
            'changes': self._count_changes(diff)
        }
    
    def _count_changes(self, diff: list) -> dict:
        return {
            'additions': len([l for l in diff if l.startswith('+')]),
            'deletions': len([l for l in diff if l.startswith('-')]),
            'modifications': 0  # TODO
        }
```

---

### Week 2: Claude API 整合 + 第一次 Demo

#### Day 1-3: AI 風險分析

**全員協作模式**: Mob Programming (所有人一起寫)

```python
# src/services/ai/risk_analyzer.py

import anthropic
import os

class RiskAnalyzer:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )
    
    def analyze_changes(self, old_clause: str, new_clause: str) -> dict:
        """使用 Claude 分析條款變更的風險"""
        
        prompt = f"""
你是專業的合約風險分析助理。分析以下條款變更：

原條款:
{old_clause}

新條款:
{new_clause}

請評估風險等級（Critical/High/Medium/Low）並說明原因。

以 JSON 格式回覆:
{{
    "risk_level": "...",
    "summary": "...",
    "why_risky": "...",
    "recommendation": "..."
}}
"""
        
        response = self.client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # 記錄成本
        cost = self._calculate_cost(response.usage)
        print(f"API Cost: ${cost:.4f}")
        
        return {
            'analysis': response.content[0].text,
            'cost': cost
        }
    
    def _calculate_cost(self, usage) -> float:
        input_cost = usage.input_tokens / 1_000_000 * 15
        output_cost = usage.output_tokens / 1_000_000 * 75
        return input_cost + output_cost
```

**業務人員**: 
- 準備「預期結果」（這個條款變更應該是高風險）
- 驗證 AI 分析是否合理

**SA**:
- 優化 prompt
- 定義評估標準

**開發**:
- 實作 API
- 處理錯誤

**Infra**:
- 設定環境變數（API Key）
- 監控 API 用量

---

#### Day 4: 整合所有模組

```python
# src/main.py - FastAPI 應用

from fastapi import FastAPI, UploadFile
from services.document.extractor import PDFExtractor
from services.contract.comparator import ContractComparator
from services.ai.risk_analyzer import RiskAnalyzer

app = FastAPI()

@app.post("/compare")
async def compare_contracts(
    old_file: UploadFile,
    new_file: UploadFile
):
    # 1. 提取文字
    extractor = PDFExtractor()
    old_text = extractor.extract_text(old_file.file)
    new_text = extractor.extract_text(new_file.file)
    
    # 2. 比對
    comparator = ContractComparator()
    diff_result = comparator.compare(old_text, new_text)
    
    # 3. AI 分析（簡化版：只分析第一個差異）
    analyzer = RiskAnalyzer()
    if diff_result['diff']:
        risk = analyzer.analyze_changes(
            old_text[:500],  # 簡化：只取前 500 字
            new_text[:500]
        )
    
    return {
        'diff': diff_result,
        'risk_analysis': risk
    }

# 測試
# curl -X POST -F "old_file=@contract_v1.pdf" \
#              -F "new_file=@contract_v2.pdf" \
#              http://localhost:8000/compare
```

---

#### Day 5: Demo Day! 🎉

**準備**:
```
□ 業務: 準備 Demo 腳本（故事性）
□ SA: 準備架構圖（展示技術）
□ 開發: 確保 demo 能跑
□ Infra: 準備 backup 環境（以防萬一）
```

**Demo 流程** (30 分鐘):
```
1. 業務開場 (5min)
   - 問題: 人工比對合約很痛苦
   - 展示: 2 份真實合約

2. 展示系統 (15min)
   - 上傳兩份合約
   - 等待處理（<30秒）
   - 展示比對報告
   - 展示 AI 風險分析

3. 技術說明 (5min)
   - SA: 架構圖快速走過
   - 成本: 每次比對 <$1

4. Q&A (5min)
   - 收集反饋
   - 詢問是否有價值
```

**決策點**:
```
如果 Stakeholders 認可:
  → 繼續投入，進入階段 2
  
如果 Stakeholders 不認可:
  → Pivot: 調整方向或換題目
```

---

### 🎯 階段 1 交付物 (Week 2 結束)

**技術交付**:
- ✅ 可運行的 MVP（本機 + Docker）
- ✅ 能處理真實 PDF 合約
- ✅ 能產生比對報告
- ✅ 有 AI 風險分析
- ✅ 簡單的 API

**團隊交付**:
- ✅ 每個人都貢獻了程式碼
- ✅ 建立了 pair/mob programming 習慣
- ✅ 第一次成功的 Demo
- ✅ 了解彼此的工作方式

**數據交付**:
- ✅ Claude API 實際成本數據
- ✅ 處理速度數據
- ✅ 使用者反饋

---

## 🔧 階段 2: 流程建立 (Week 3-4)

### 目標: 從「能跑」到「能維護」

**Week 1-2 的問題**:
- 程式碼可能很亂（technical debt）
- 沒有測試
- 沒有文件
- 沒有標準流程

**Week 3-4 的重點**:
- 建立開發流程
- 補測試與文件
- Code review 機制
- 持續整合

---

### Week 3: 建立開發流程

#### 定義 Git 工作流程

**問題**: 新團隊常見混亂
```
❌ 直接 commit 到 main
❌ commit message 隨便寫
❌ 不做 code review
❌ merge 前不測試
```

**解決**: Git Flow (簡化版)

```
main (保護分支，只能透過 PR merge)
  ↑
develop (開發主分支)
  ↑
feature/xxx (功能分支)
```

**工作流程**:
```bash
# 1. 從 develop 切新分支
git checkout develop
git pull
git checkout -b feature/add-table-diff

# 2. 開發
# ... 寫程式 ...

# 3. Commit (遵循格式)
git add .
git commit -m "feat(compare): add table diff support

- Extract tables from PDF using pdfplumber
- Compare cell by cell
- Highlight changed cells in red

Closes #42"

# 4. Push 並建立 PR
git push origin feature/add-table-diff
# 在 GitHub 建立 Pull Request

# 5. Code Review
# 等待至少 1 人 approve

# 6. Merge
# PR merge 後自動跑 CI/CD
```

**Commit Message 規範**:
```
<type>(<scope>): <subject>

<body>

<footer>

Types:
- feat: 新功能
- fix: 修復
- docs: 文件
- style: 格式
- refactor: 重構
- test: 測試
- chore: 雜項
```

---

#### 建立 Code Review 文化

**PR Checklist Template**:
```markdown
## PR Description
簡述這個 PR 做了什麼

## Changes
- [ ] 新增功能 X
- [ ] 修復 bug Y
- [ ] 更新文件 Z

## Testing
- [ ] 單元測試通過
- [ ] 手動測試過
- [ ] 測試覆蓋率 >80%

## Screenshots (如果有 UI 變更)
[貼圖]

## Reviewer Checklist
- [ ] 程式碼符合 style guide
- [ ] 有適當的錯誤處理
- [ ] 有測試
- [ ] 文件已更新
- [ ] 沒有明顯的安全問題
```

**Review 準則**:
```
✅ 每個 PR 至少 1 人 review
✅ Review 在 24 小時內完成
✅ 用「建議」語氣，不用「命令」
✅ 解釋「為什麼」，不只說「不行」
```

---

#### 建立測試文化

**測試金字塔**:
```
        /\
       /E2E\    (少量，關鍵流程)
      /------\
     /整合測試 \  (中量，模組間)
    /----------\
   /  單元測試   \ (大量，每個函數)
  /--------------\
```

**Week 3 目標**: 
```
□ 所有新功能都有測試
□ 測試覆蓋率 >60% (Week 3 結束)
□ CI 自動跑測試
```

**範例**:
```python
# tests/test_extractor.py

import pytest
from services.document.extractor import PDFExtractor

def test_extract_text_from_valid_pdf():
    """測試從有效 PDF 提取文字"""
    extractor = PDFExtractor()
    text = extractor.extract_text("tests/fixtures/sample.pdf")
    
    assert len(text) > 0
    assert "合約" in text  # 應該包含關鍵字

def test_extract_metadata():
    """測試提取 PDF 中繼資料"""
    extractor = PDFExtractor()
    metadata = extractor.extract_metadata("tests/fixtures/sample.pdf")
    
    assert 'page_count' in metadata
    assert metadata['page_count'] > 0

def test_extract_from_invalid_file():
    """測試處理無效檔案"""
    extractor = PDFExtractor()
    
    with pytest.raises(Exception):
        extractor.extract_text("not_a_pdf.txt")
```

---

### Week 4: CI/CD + 文件

#### 設定 CI/CD Pipeline

**GitHub Actions** (Infra 主導):
```yaml
# .github/workflows/ci.yml

name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=src tests/
    
    - name: Check coverage
      run: |
        coverage report --fail-under=60
    
    - name: Lint
      run: |
        pip install black flake8
        black --check src/
        flake8 src/
  
  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t contract-diff:${{ github.sha }} .
    
    - name: Push to registry (if main branch)
      if: github.ref == 'refs/heads/main'
      run: |
        # Push to Docker registry
        echo "Pushing to registry..."
```

---

#### 補完文件

**必須文件** (SA + 業務協作):

1. **API 文件**:
```markdown
# API Documentation

## POST /compare

比對兩份合約並分析風險

### Request
- Content-Type: multipart/form-data
- Body:
  - old_file: PDF file
  - new_file: PDF file

### Response
{
  "diff": {
    "similarity": 0.85,
    "changes": {
      "additions": 3,
      "deletions": 2
    }
  },
  "risk_analysis": {
    "risk_level": "High",
    "summary": "..."
  }
}

### Example
```bash
curl -X POST \
  -F "old_file=@contract_v1.pdf" \
  -F "new_file=@contract_v2.pdf" \
  http://localhost:8000/compare
```
```

2. **使用手冊** (業務主導):
```markdown
# 合約比對系統使用手冊

## 快速開始

### 1. 準備合約
- 格式: PDF
- 大小: <50MB
- 語言: 繁體中文或英文

### 2. 上傳比對
[步驟截圖]

### 3. 查看報告
[報告範例截圖]

## 常見問題

Q: 支援哪些合約類型？
A: SLA, NDA, MSA, 採購合約...

Q: 處理時間多久？
A: 10 頁合約約 30 秒

Q: 成本多少？
A: 每次比對約 $0.50
```

3. **開發者指南** (開發主導):
```markdown
# 開發者指南

## 環境設定
```bash
git clone ...
cd contract-diff
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 專案結構
```
src/
  services/
    document/     # PDF 處理
    contract/     # 比對邏輯
    ai/           # AI 分析
  api/            # FastAPI 端點
tests/
docs/
```

## 新增功能
1. 從 develop 切分支
2. 寫測試（TDD）
3. 實作功能
4. 跑測試 `pytest`
5. 建立 PR
```

---

### 🎯 階段 2 交付物 (Week 4 結束)

**流程建立**:
- ✅ Git 工作流程文件
- ✅ Code Review 準則
- ✅ CI/CD Pipeline 運作
- ✅ 測試覆蓋率 >60%

**文件齊全**:
- ✅ API 文件
- ✅ 使用手冊
- ✅ 開發者指南
- ✅ 架構圖

**團隊成熟度**:
- ✅ 每個人會做 PR
- ✅ 每個人會寫測試
- ✅ 每個人會 review code
- ✅ 流程順暢，不需要每次問

---

## 🚀 階段 3: 規模化 (Week 5-12)

### 此時你已經有：
- ✅ 運作的 MVP
- ✅ 成熟的流程
- ✅ 有默契的團隊

### 接下來就是執行原本的 11 週計劃！

參考: [TECHNICAL_DESIGN.md 的實作計劃](./architecture/TECHNICAL_DESIGN.md#7-實作計劃)

---

## 📊 新團隊特殊注意事項

### 1. 避免常見陷阱

**陷阱 1: 完美主義**
```
❌ "要等架構完美才能開始寫"
✅ "先寫能跑的，再逐步重構"
```

**陷阱 2: 過度設計**
```
❌ "要支援未來 10 年的擴展性"
✅ "先滿足當前需求，YAGNI"
```

**陷阱 3: 缺乏溝通**
```
❌ "各自悶頭寫 2 週再整合"
✅ "每天 sync，頻繁整合"
```

**陷阱 4: 忽略技術債**
```
❌ "先做功能，debt 以後還"
✅ "每個 sprint 20% 時間還 debt"
```

---

### 2. 團隊健康度指標

**每週檢查** (PM/SA 負責):

| 指標 | 綠燈 | 黃燈 | 紅燈 | 當前 |
|------|------|------|------|------|
| **溝通頻率** | 每天多次 | 2-3天一次 | 一週一次 | ? |
| **PR Review 時間** | <24h | 24-48h | >48h | ? |
| **CI 通過率** | >90% | 80-90% | <80% | ? |
| **測試覆蓋率** | >80% | 60-80% | <60% | ? |
| **團隊士氣** | 😊😊😊 | 😐😐 | 😞😞 | ? |

**如果出現紅燈**:
```
□ 立即召開團隊會議
□ 識別問題（技術？流程？人？）
□ 制定改善計劃
□ 1 週後重新檢查
```

---

### 3. 知識分享機制

**新團隊容易形成知識孤島** → 需要主動分享

**建議機制**:

**每週 Tech Talk** (30min):
```
Week 3: "Claude API 使用技巧" (Dev)
Week 4: "PDF 處理的坑" (Dev)
Week 5: "CI/CD 最佳實踐" (Infra)
Week 6: "如何寫好 PR" (SA)
```

**Pair Rotation**:
```
Week 1: A+B, C+D
Week 2: A+C, B+D
Week 3: A+D, B+C
→ 確保知識流通
```

**Documentation First**:
```
遇到問題 → 解決 → 寫文件
下次遇到 → 查文件 → 解決
```

---

## ✅ 檢查清單：你準備好了嗎？

### Week 0 (團隊建立)
```
□ 填寫技能矩陣
□ 定義 RACI
□ 設定所有工具
□ 完成基礎培訓
□ 跑起第一個 Hello World
```

### Week 1-2 (MVP)
```
□ 環境建置完成
□ PDF 提取功能
□ 基礎比對功能
□ Claude API 整合
□ 第一次 Demo
```

### Week 3-4 (流程)
```
□ Git 工作流程建立
□ CI/CD Pipeline
□ 測試覆蓋率 >60%
□ 文件齊全
```

### Week 5+ (規模化)
```
□ 按原計劃執行
□ 定期回顧與調整
```

---

## 🎯 最後的建議

### 給業務人員
```
你的價值:
✓ 定義「好的結果」是什麼
✓ 驗證系統是否真的有用
✓ 收集使用者反饋
✓ 撰寫易懂的文件

不要:
✗ 覺得自己不懂技術就不敢發言
✗ 只丟需求不參與討論
```

### 給 SA
```
你的價值:
✓ 架構設計與技術決策
✓ 橋接業務與技術
✓ Code Review 與品質把關
✓ 技術文件撰寫

不要:
✗ 過度設計（YAGNI）
✗ 只畫圖不寫 code
```

### 給 Infra
```
你的價值:
✓ 環境建置與維護
✓ CI/CD 自動化
✓ 監控與告警
✓ 效能優化

不要:
✗ 等到最後才介入
✗ 過早優化
```

### 給開發
```
你的價值:
✓ 高品質程式碼
✓ 完整的測試
✓ 技術創新
✓ 知識分享

不要:
✗ 只寫 code 不寫測試
✗ 拒絕 code review 意見
```

---

## 🚀 現在就開始！

**本週行動** (Week 0):
```
Day 1 (今天):
  □ 召集團隊會議
  □ 說明專案目標
  □ 填寫技能矩陣

Day 2:
  □ 定義 RACI
  □ 設定工具（GitHub, Slack）
  
Day 3:
  □ 技術培訓（AI/ML 101）
  
Day 4:
  □ Hands-on: 寫第一個程式
  
Day 5:
  □ 回顧 + 規劃 Sprint 1
```

**記住**:
> **"The strength of the team is each individual member.  
> The strength of each member is the team."**  
> — Phil Jackson

你們可以的！💪

---

**文件版本**: 1.0  
**適用對象**: 新組建的跨職能團隊  
**下次更新**: Week 4 結束後（根據實際經驗調整）
