# 團隊協作工具指南

**目標**: 讓業務、SA、Infra 三個角色都能有效參與開發  
**原則**: 降低技術門檻，提高協作效率

---

## 📚 目錄

1. [工具總覽](#工具總覽)
2. [即時協作工具](#即時協作工具)
3. [程式碼協作](#程式碼協作)
4. [專案管理](#專案管理)
5. [文件協作](#文件協作)
6. [溝通工具](#溝通工具)
7. [快速設定指南](#快速設定指南)

---

## 工具總覽

### 必備工具（全員必須安裝）

| 工具 | 用途 | 適用角色 | 優先級 |
|------|------|----------|--------|
| **VS Code** | 程式碼編輯與協作 | 全員 | 🔴 P0 |
| **VS Code Live Share** | 即時配對程式 | 全員 | 🔴 P0 |
| **Git** | 版本控制 | 全員 | 🔴 P0 |
| **Microsoft Teams** | 即時溝通、會議 | 全員 | 🔴 P0 |
| **Azure DevOps** | 專案管理、看板 | 全員 | 🔴 P0 |
| **GitHub Desktop** | Git 圖形化介面 | 業務 | 🟡 P1 |
| **Python 3.11+** | 執行程式 | SA、業務 | 🔴 P0 |
| **Poetry** | Python 套件管理 | SA、業務 | 🔴 P0 |
| **Docker Desktop** | 容器化 | SA、Infra | 🟡 P1 |

### 推薦工具（提升效率）

| 工具 | 用途 | 適用角色 |
|------|------|----------|
| **Postman** | API 測試 | SA、業務 |
| **TablePlus** | 資料庫管理 | SA |
| **Figma** | UI 設計（如需要） | 業務 |
| **Notion** | 知識庫 | 全員 |
| **Loom** | 螢幕錄影分享 | 全員 |

---

## 即時協作工具

### 🎯 VS Code Live Share（強烈推薦）

**為什麼選它**:
- ✅ 多人即時編輯同一份程式碼（類似 Google Docs）
- ✅ 不需要 Git commit 就能協作
- ✅ 內建語音通話
- ✅ 共享終端機（可一起執行指令）
- ✅ 共享伺服器（可一起測試 API）
- ✅ **完全免費**

#### 安裝步驟

1. **安裝 VS Code**
   ```bash
   # macOS
   brew install --cask visual-studio-code
   
   # Windows
   # 從官網下載: https://code.visualstudio.com/
   ```

2. **安裝 Live Share 擴充套件**
   - 打開 VS Code
   - 點擊左側「Extensions」圖示（或按 `Cmd+Shift+X`）
   - 搜尋 "Live Share"
   - 安裝 **Live Share Extension Pack**（包含語音、聊天功能）

3. **登入 Microsoft 帳號**
   - 點擊左下角「人像」圖示
   - 選擇「Sign in to sync settings」
   - 使用公司 Microsoft 帳號登入

#### 使用方式

**主持人（Host）- 通常是 SA**:

```bash
1. 打開專案資料夾
   File > Open Folder > 選擇 bule-ai-team/

2. 點擊左下角「Live Share」按鈕
   或按 Cmd+Shift+P 輸入 "Live Share: Start"

3. 複製分享連結
   Live Share 會自動複製連結到剪貼簿

4. 傳送連結給團隊成員（透過 Teams）
   https://prod.liveshare.vsengsaas.visualstudio.com/join?xxx
```

**參與者（Guest）- 業務或 Infra**:

```bash
1. 收到連結後，點擊連結
   瀏覽器會詢問是否開啟 VS Code

2. VS Code 自動開啟並加入協作
   可以看到主持人正在編輯的檔案

3. 開始協作！
   - 游標會顯示每個人的名字
   - 可以自由編輯程式碼
   - 可以開啟語音通話（右上角麥克風圖示）
```

#### 協作場景範例

**場景 1: SA 教業務寫 Python**

```
時間: 週二上午 10:30-12:00
模式: SA 當 Host

流程:
1. SA 分享 Live Share 連結給業務
2. 業務加入後，SA 帶著業務看 src/api/contracts.py
3. SA 解釋程式碼邏輯（可用語音或 Teams）
4. 業務嘗試修改程式碼（SA 即時看到）
5. SA 即時指導、糾正錯誤
6. 一起執行測試（共享終端機）
```

**場景 2: 全員 Debug**

```
時間: 週四下午發現 Bug
模式: SA 當 Host，業務 + Infra 一起加入

流程:
1. SA 分享連結
2. 業務描述問題（語音）
3. SA 在程式碼中加 print() 除錯
4. 業務即時看到輸出結果
5. Infra 提供基礎設施相關建議
6. 一起找到問題並修復
```

#### Live Share 進階功能

**共享終端機**:
```bash
# 主持人
1. 打開終端機（Terminal > New Terminal）
2. 右鍵點擊終端機標籤
3. 選擇 "Share Terminal" > "Read/Write"

# 參與者可以在同一個終端機執行指令
# 例如: poetry run pytest
```

**共享伺服器**:
```bash
# 主持人啟動開發伺服器
poetry run uvicorn src.main:app --reload

# Live Share 自動分享 localhost:8000
# 參與者可以在自己瀏覽器訪問主持人的伺服器！
# 不需要自己啟動
```

**追蹤其他人的游標**:
```bash
# 點擊左下角 "Live Share" 面板
# 點擊某個參與者的名字
# 你的畫面會自動跟隨他的游標
```

---

## 程式碼協作

### 🌿 Git + GitHub/Azure Repos

雖然 Live Share 很方便，但正式的程式碼變更仍需要透過 Git。

#### 對於不熟悉 Git 的成員：使用 GitHub Desktop

**安裝**:
```bash
# macOS
brew install --cask github

# Windows
# https://desktop.github.com/
```

**圖形化操作**:

```
1. Clone Repository（複製專案）
   File > Clone Repository
   輸入: https://github.com/your-org/bule-ai-team
   選擇本地資料夾

2. 建立分支（Branch）
   Current Branch > New Branch
   命名: feature/your-task-name

3. 進行修改
   （在 VS Code 中編輯檔案）

4. Commit（提交變更）
   左側會顯示修改的檔案
   在 "Summary" 欄位輸入簡短描述
   點擊 "Commit to feature/..."

5. Push（推送到遠端）
   點擊右上角 "Push origin"

6. 建立 Pull Request
   GitHub Desktop 會提示 "Create Pull Request"
   點擊後會開啟瀏覽器，填寫 PR 描述
```

**適合角色**: 業務、不熟悉命令列的成員

#### 對於熟悉命令列的成員：使用 Git CLI

```bash
# 每日工作流程
git checkout develop
git pull origin develop
git checkout -b feature/US1-upload
# ... 進行修改 ...
git add .
git commit -m "feat(upload): 實作上傳功能"
git push origin feature/US1-upload
# 在網頁上建立 PR
```

**適合角色**: SA、Infra、有經驗的 Dev

### 🔍 Code Review 工具

**在 GitHub/Azure Repos 上**:

```
1. PR 建立後，指定 Reviewer
   右側選擇 "Reviewers" > 選擇 SA 或其他成員

2. Reviewer 收到通知
   可以在網頁上逐行評論

3. 評論範例:
   [在第 42 行點擊 "+" ]
   "建議加上錯誤處理，避免程式崩潰"

4. 作者修正後再次 Push
   評論會自動更新狀態

5. Approve 後合併
   點擊 "Merge Pull Request"
```

---

## 專案管理

### 📊 Azure DevOps Board

**為什麼用 Azure DevOps**:
- ✅ 與 Azure 生態系整合
- ✅ 完整的 Scrum 功能
- ✅ 免費（5 人以內）
- ✅ 中文化介面

#### 設定步驟

**1. 建立組織與專案**

```bash
1. 訪問 https://dev.azure.com/
2. 登入 Microsoft 帳號
3. 建立組織（Organization）
   名稱: blue-ai-team
4. 建立專案（Project）
   名稱: Contract Comparison
   類型: Scrum
   版本控制: Git
```

**2. 設定 Board**

```
1. 左側選單 > Boards > Work items
2. 建立 Epic
   Title: 合約比對 MVP
   
3. 建立 User Stories（6 個）
   從 docs/MVP_USER_STORIES.md 複製
   US#1: 上傳合約
   US#2: 萃取 PDF
   US#3: 比對差異
   US#4: AI 分析
   US#5: 產生報告
   US#6: 端到端整合
   
4. 為每個 US 建立 Tasks
   US#1 > Add Task
   Task 1.1: 建立 FastAPI 專案 (SA, 4h)
   Task 1.2: 實作 upload API (SA, 6h)
   ...
```

**3. 指派任務**

```
每個 Task:
- Assigned To: 選擇負責人（SA/業務/Infra）
- Original Estimate: 填入估時（小時）
- State: 預設為 "To Do"
```

**4. 每日更新**

```
每天 Standup 後:
1. 將昨天完成的 Task 拖到 "Done"
2. 將今天要做的 Task 拖到 "In Progress"
3. 如果有阻礙，在 Task 中記錄
```

#### Board 視圖說明

**看板視圖（Board View）**:
```
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│ Backlog  │ To Do    │ In Prog  │ Review   │ Done     │
├──────────┼──────────┼──────────┼──────────┼──────────┤
│          │ Task 1.2 │ Task 1.1 │          │ Task 0.1 │
│          │ (SA)     │ (SA)     │          │ (全員)   │
│          │          │          │          │          │
│ US#3     │ Task 2.1 │ Task 1.3 │          │ Task 0.2 │
│          │ (SA)     │ (業務)   │          │          │
└──────────┴──────────┴──────────┴──────────┴──────────┘
```

**Sprint Burndown（燃盡圖）**:
```
顯示剩餘工作量趨勢
理想狀況: 直線往下
實際狀況: 追蹤是否落後
```

### 🎯 每週 Sprint Planning 流程

**時間**: 每兩週一上午 10:00-12:00

```
1. Review 上個 Sprint（30 分鐘）
   - Demo 完成的功能
   - 檢視 Burndown Chart
   
2. Planning 下個 Sprint（60 分鐘）
   - 從 Backlog 拉 User Stories 到 Sprint
   - 拆解 Tasks
   - 指派負責人
   - 估時（Planning Poker）
   
3. 確認 Sprint Goal（30 分鐘）
   - 例如: "完成 PDF 上傳與萃取功能"
   - 定義 Definition of Done
```

---

## 文件協作

### 📝 選項 1: Markdown + Git（推薦）

**優點**:
- ✅ 版本控制完整
- ✅ 與程式碼放在一起
- ✅ 支援程式碼語法高亮
- ✅ 可用 VS Code 編輯

**使用方式**:

```bash
# 所有文件放在 docs/
docs/
├── WEEK0_CHECKLIST.md
├── MVP_USER_STORIES.md
├── DEVELOPMENT_GUIDE.md
└── api/
    └── API_SPECIFICATION.md

# 編輯文件
在 VS Code 中打開 .md 檔案
按 Cmd+Shift+V 預覽 Markdown

# 協作
使用 Live Share 一起編輯文件
或透過 Git PR 流程 Review
```

**適合**: 技術文件、API 文件、需求規格

### 📝 選項 2: Microsoft Teams + SharePoint

**優點**:
- ✅ 非技術人員友善
- ✅ 即時協作（類似 Google Docs）
- ✅ 權限管理方便
- ✅ 整合在 Teams 中

**使用方式**:

```
1. 在 Teams 頻道中建立分頁
   頻道 > + > OneNote/Word/Excel

2. 建立共享文件
   Files 分頁 > New > Word Document

3. 多人同時編輯
   其他成員打開同一份文件
   即時看到彼此的修改

4. 版本歷史
   右上角 > Version History
   可還原到任何時間點
```

**適合**: 會議記錄、非技術文件、業務需求

### 📝 選項 3: Notion（可選）

**優點**:
- ✅ 美觀易用
- ✅ 強大的組織能力（資料庫、看板）
- ✅ 跨平台（桌面、手機）

**使用方式**:

```
1. 建立 Workspace
   https://notion.so/ > 註冊

2. 建立頁面結構
   📁 Blue-AI 合約比對
      📄 專案總覽
      📁 會議記錄
         📄 2026-05-28 Kickoff
         📄 2026-06-04 Sprint Planning
      📁 技術文件
      📁 決策記錄（ADR）

3. 邀請成員
   右上角 Share > Invite > 輸入 Email

4. 協作
   @mention 其他成員
   留言討論
```

**適合**: 知識庫、會議記錄、腦力激盪

---

## 溝通工具

### 💬 Microsoft Teams

**頻道設定建議**:

```
團隊: Blue-AI Contract Diff

頻道:
📢 General（一般討論）
  - 日常溝通
  - 非正式討論

💻 Development（開發討論）
  - 技術問題
  - Code Review 通知
  - 部署通知

📋 Sprint（Sprint 相關）
  - Daily Standup 記錄
  - Sprint Planning 通知
  - Demo 排程

🐛 Issues（問題追蹤）
  - Bug 回報
  - 緊急問題

📚 Resources（資源分享）
  - 教學文章
  - 有用工具
  - 參考資料
```

**會議設定**:

```
1. 每日 Standup（固定排程）
   時間: 每日 10:00-10:15
   類型: 語音會議（可開鏡頭）
   
   Teams > Calendar > New Meeting
   Title: Daily Standup
   Recurrence: Daily, Mon-Fri
   
2. Sprint Planning（固定排程）
   時間: 每兩週一 10:00-12:00
   類型: 視訊會議
   
3. 臨時 Pair Programming
   直接在 Development 頻道發起通話
   "Meet now" > 開始協作
```

**實用功能**:

```
🔔 @mention 通知
   @SA 請幫忙看一下這個錯誤

📌 Pin 重要訊息
   右鍵 > Pin > 釘選在頻道頂部

🔗 分享 Live Share 連結
   直接貼在頻道中，點擊即可加入

📊 整合 Azure DevOps
   Connectors > Azure DevOps
   自動通知 PR、Work Item 更新
```

### 📞 配對程式時的語音選擇

| 工具 | 優點 | 缺點 | 推薦情境 |
|------|------|------|----------|
| **VS Code Live Share Audio** | 整合在編輯器中 | 音質普通 | 1-2 人配對 |
| **Teams** | 音質好、可錄影 | 需要另開視窗 | 正式會議、多人 |
| **Discord** | 音質最佳、延遲低 | 需額外申請 | 長時間協作 |

**建議**:
- 配對程式: 用 Live Share Audio（方便）
- Standup/會議: 用 Teams（正式）
- 長時間協作（>2 小時）: 用 Discord（舒適）

---

## 快速設定指南

### 🚀 Day 1: 必裝工具（全員，2 小時）

#### Step 1: 安裝 VS Code（15 分鐘）

**macOS**:
```bash
brew install --cask visual-studio-code
```

**Windows**:
1. 訪問 https://code.visualstudio.com/
2. 下載 Windows 版本
3. 執行安裝程式（全部預設值即可）

#### Step 2: 安裝 VS Code 擴充套件（15 分鐘）

在 VS Code 中按 `Cmd+Shift+X`（macOS）或 `Ctrl+Shift+X`（Windows），搜尋並安裝：

```
✅ 必裝:
1. Live Share Extension Pack
2. Python
3. Pylance
4. GitLens

✅ 推薦:
5. Markdown All in One
6. YAML
7. Docker（SA、Infra）
8. Azure Account（如使用 Azure）
```

#### Step 3: 安裝 Git（15 分鐘）

**macOS**:
```bash
# 檢查是否已安裝
git --version

# 如果沒有
brew install git

# 設定個人資訊
git config --global user.name "Your Name"
git config --global user.email "your.email@company.com"
```

**Windows**:
```bash
# 下載 Git for Windows
https://git-scm.com/download/win

# 安裝後，在 CMD 中設定
git config --global user.name "Your Name"
git config --global user.email "your.email@company.com"
```

#### Step 4: 安裝 GitHub Desktop（選用，15 分鐘）

**適合不熟悉命令列的成員**

```bash
# macOS
brew install --cask github

# Windows
https://desktop.github.com/
```

#### Step 5: 安裝 Python 與 Poetry（30 分鐘）

**macOS**:
```bash
# 安裝 Python 3.11
brew install python@3.11

# 驗證
python3 --version  # 應該顯示 3.11.x

# 安裝 Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 加入 PATH（將以下加入 ~/.zshrc 或 ~/.bash_profile）
export PATH="$HOME/.local/bin:$PATH"

# 重新載入
source ~/.zshrc

# 驗證
poetry --version
```

**Windows**:
```powershell
# 1. 安裝 Python 3.11
# 從官網下載: https://www.python.org/downloads/
# ⚠️ 安裝時勾選 "Add Python to PATH"

# 2. 驗證
python --version

# 3. 安裝 Poetry
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# 4. 重啟 PowerShell 後驗證
poetry --version
```

#### Step 6: Clone 專案（15 分鐘）

**使用 GitHub Desktop（簡單）**:
```
1. File > Clone Repository
2. URL 分頁 > 輸入專案網址
3. 選擇本地路徑（建議: ~/Documents/bule-ai-team）
4. Clone
```

**使用命令列**:
```bash
cd ~/Documents
git clone https://github.com/your-org/bule-ai-team.git
cd bule-ai-team
```

#### Step 7: 安裝專案依賴（15 分鐘）

```bash
cd bule-ai-team

# 安裝依賴
poetry install

# 啟動虛擬環境
poetry shell

# 驗證（應該看到 .venv 環境啟動）
which python  # macOS/Linux
where python  # Windows
```

#### Step 8: 第一次執行（15 分鐘）

```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env（加入 Claude API Key）
# macOS
code .env

# Windows
notepad .env

# 啟動開發伺服器
poetry run uvicorn src.main:app --reload

# 看到以下訊息表示成功:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete.

# 在瀏覽器訪問
http://localhost:8000/docs
```

---

### 🎯 Day 2: 第一次協作（全員，1 小時）

#### 練習 1: Live Share 配對（30 分鐘）

**SA（主持人）**:
```bash
1. 在 VS Code 打開專案
2. 點擊左下角 "Live Share"
3. 複製連結傳到 Teams #Development 頻道
```

**業務、Infra（參與者）**:
```bash
1. 點擊 Teams 中的 Live Share 連結
2. VS Code 自動開啟並加入
3. 看到 SA 的游標和檔案

嘗試:
- 打開 src/main.py
- 嘗試修改一行註解
- 看到 SA 即時看到你的修改
- 開啟語音通話（右上角麥克風）
```

#### 練習 2: 第一次 Commit（30 分鐘）

**每個成員**:

```bash
# 1. 建立自己的分支
git checkout -b feature/add-my-name

# 2. 在 VS Code 中編輯 README.md
# 加入自己的名字到團隊成員清單

# 3. Commit（使用 GitHub Desktop 或命令列）

# GitHub Desktop:
# - 左側看到修改的檔案
# - 輸入 commit message: "docs: 加入我的名字到團隊清單"
# - 點擊 Commit
# - 點擊 Push

# 命令列:
git add README.md
git commit -m "docs: 加入我的名字到團隊清單"
git push origin feature/add-my-name

# 4. 在網頁上建立 PR
# 5. 請其他成員 Review
# 6. 合併
```

---

## 協作最佳實踐

### ✅ Do（建議做）

```
✅ 每天 Standup 後更新 Azure DevOps Board
✅ Code Review 在 24 小時內完成
✅ 配對程式時每 25 分鐘交換角色
✅ 重要決策記錄在文件中
✅ 遇到問題先查文件，再問人
✅ 善用 @mention 通知相關人員
✅ 定期 Push 程式碼（至少每天一次）
✅ Commit message 使用英文（或至少統一語言）
```

### ❌ Don't（避免做）

```
❌ 直接在 main/develop 分支上修改
❌ Commit message 寫 "update" "fix" 等無意義訊息
❌ Review 時只說 "LGTM" 沒有實際檢查
❌ 獨自奮戰超過 2 小時不求助
❌ 忘記更新 Board 狀態
❌ 在 Git 中提交機敏資訊（API Key、密碼）
❌ 會議遲到或缺席不事先通知
```

---

## 疑難排解

### Q: Live Share 連線失敗？

```bash
1. 確認網路連線正常
2. 確認已登入 Microsoft 帳號
3. 嘗試重新安裝 Live Share Extension
4. 檢查防火牆設定（可能阻擋連線）
```

### Q: Poetry 安裝依賴很慢？

```bash
# 使用國內鏡像（中國地區）
poetry source add tsinghua https://pypi.tuna.tsinghua.edu.cn/simple/
poetry source add aliyun https://mirrors.aliyun.com/pypi/simple/

# 或使用 pip 安裝後用 poetry
pip install -r requirements.txt
```

### Q: Git 衝突（Conflict）怎麼辦？

```bash
# 1. 更新 develop
git checkout develop
git pull origin develop

# 2. 回到自己的分支
git checkout feature/my-branch

# 3. 合併 develop
git merge develop

# 4. 如果有衝突，VS Code 會顯示
# 選擇 "Accept Current Change" 或 "Accept Incoming Change"
# 或手動編輯

# 5. 完成合併
git add .
git commit -m "merge: 解決與 develop 的衝突"
git push
```

### Q: 不小心 Commit 了 API Key？

```bash
# ⚠️ 緊急處理
1. 立即更換 API Key（在 Anthropic Console）
2. 從 Git 歷史中移除（需要 force push，慎用）
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
3. 通知團隊成員重新 clone

# 💡 預防
在專案根目錄建立 .gitignore:
.env
*.key
secrets/
```

---

## 總結

### 立即開始（今天）

**全員**:
- [ ] 安裝 VS Code + Live Share
- [ ] 加入 Teams 頻道
- [ ] Clone 專案
- [ ] 第一次 Live Share 測試

**SA**:
- [ ] 建立 Azure DevOps Board
- [ ] 匯入 User Stories
- [ ] 設定 Git Repository

**業務**:
- [ ] 安裝 GitHub Desktop（如不熟悉命令列）
- [ ] 準備合約樣本

**Infra**:
- [ ] 規劃 Azure 資源
- [ ] 準備 Docker 環境

### 本週目標

- [ ] 全員完成開發環境設定
- [ ] 成功進行至少 2 次 Live Share 配對
- [ ] 每個人至少完成 1 次 PR 流程
- [ ] Azure DevOps Board 上線並使用

---

**有問題？**
在 Teams #Development 頻道提問，或使用 `/help` 指令尋求 Claude Code 協助。

**讓我們開始協作吧！** 🚀
