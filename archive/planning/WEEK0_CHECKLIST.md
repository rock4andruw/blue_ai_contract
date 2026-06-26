# Week 0 執行檢查清單

**目標**: 建立團隊協作基礎，完成技能盤點，定義工作流程  
**期限**: 3-5 個工作天  
**參與者**: 全體團隊成員（業務、SA、Infra、未來的 Dev）

---

## Day 1: 團隊啟動會議（2 小時）

### 會議議程

**時間分配**:
- 0:00-0:20 專案背景與目標對齊
- 0:20-0:50 技能盤點與角色定義
- 0:50-1:20 工作流程與工具確認
- 1:20-1:50 MVP 範圍共識
- 1:50-2:00 下一步行動

### ✅ 檢查項目

- [ ] 所有成員理解專案目標（合約比對自動化，字元準確率 >95%）
- [ ] 完成技能評估表（下方範本）
- [ ] 確認每個人的可投入時間（全職/兼職/顧問）
- [ ] 定義初步的 RACI 矩陣
- [ ] 選定溝通工具（Teams/Slack + Azure DevOps）
- [ ] 建立共享文件空間（SharePoint/OneDrive）

### 📋 技能評估表（每人填寫）

```markdown
| 技能領域              | 熟悉度 (0-5) | 實際專案經驗 | 願意學習 |
|-----------------------|--------------|--------------|----------|
| Python 開發           |              |              | ☐ 是     |
| FastAPI/Flask         |              |              | ☐ 是     |
| Claude API 整合       |              |              | ☐ 是     |
| PDF 處理 (PyMuPDF)    |              |              | ☐ 是     |
| NLP/文字比對          |              |              | ☐ 是     |
| React/前端開發        |              |              | ☐ 是     |
| Docker/容器化         |              |              | ☐ 是     |
| Azure Services        |              |              | ☐ 是     |
| 合約/法律文件領域知識 |              |              | ☐ 是     |
| 測試與 QA             |              |              | ☐ 是     |
```

**評分標準**:
- 0: 完全不熟
- 1-2: 聽過但未實作
- 3: 做過小專案
- 4: 有正式專案經驗
- 5: 專家級，可指導他人

---

## Day 2: RACI 定義與工具設置

### ✅ RACI 矩陣確認

基於 Day 1 的技能盤點，確認以下分工：

```markdown
| 任務                     | 業務 | SA | Infra | Dev (未來) |
|--------------------------|------|----|-------|------------|
| 需求定義與驗收標準       | R,A  | C  | I     | I          |
| 技術架構設計             | I    | R,A| C     | C          |
| API 介面設計             | I    | R  | I     | A,C        |
| Claude Prompt 設計       | C    | R,A| I     | C          |
| 基礎設施規劃             | I    | C  | R,A   | I          |
| MVP 開發（Python 後端）  | I    | C  | I     | R,A        |
| 部署與維運               | I    | I  | R,A   | C          |
| 測試與驗收               | A    | C  | I     | R          |
| 使用者文件               | R,A  | C  | I     | I          |
| 成本與預算控制           | R,A  | C  | C     | I          |
```

**說明**:
- R (Responsible): 實際執行者
- A (Accountable): 最終負責人（只能一位）
- C (Consulted): 需要諮詢的人
- I (Informed): 需要知情的人

**注意**: 如果團隊中目前沒有 Dev 人員，SA 可能需要暫時承擔部分開發工作，或業務/Infra 需要學習基礎 Python。

### ✅ 工具設置檢查清單

**必須在 Day 2 完成**:

- [ ] Azure DevOps 專案建立
  - [ ] 建立 Repo（或使用現有 Git）
  - [ ] 建立 Board（Sprint planning）
  - [ ] 匯入初步工作項目
  
- [ ] 溝通管道
  - [ ] Teams 頻道建立（#blue-ai-contract-diff）
  - [ ] 每日 standup 時間確認（建議早上 10:00，15 分鐘）
  
- [ ] 文件協作
  - [ ] SharePoint 資料夾結構
  - [ ] 存取權限設定
  
- [ ] 開發環境準備
  - [ ] Python 3.11+ 安裝
  - [ ] Git 設定（commit 規範）
  - [ ] IDE 推薦（VS Code + Python extension）
  
- [ ] API Key 申請
  - [ ] Claude API Key（Anthropic Console）
  - [ ] Azure Speech/Storage（如需要）

---

## Day 3: 技術學習與配對

### ✅ 學習資源分配

根據技能評估結果，安排以下學習任務：

**對於 Python 新手（熟悉度 0-2）**:
- [ ] 完成 Python 基礎教學（3-4 小時）
  - 推薦: [Python Official Tutorial](https://docs.python.org/3/tutorial/)
  - 重點: 函數、類別、檔案處理
- [ ] 安裝並執行簡單的 FastAPI Hello World
- [ ] 練習讀寫 PDF（使用 PyMuPDF 範例）

**對於 Claude API 新手**:
- [ ] 閱讀 [Claude API 文件](https://docs.anthropic.com/)
- [ ] 執行第一個 API 呼叫（使用 curl 或 Python）
  ```python
  import anthropic
  client = anthropic.Anthropic(api_key="YOUR_KEY")
  message = client.messages.create(
      model="claude-sonnet-4-6",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello, Claude!"}]
  )
  print(message.content)
  ```
- [ ] 理解 token 計費與 cost 計算

**對於合約領域新手**:
- [ ] 閱讀範例合約（保密協議 NDA、採購合約）
- [ ] 理解常見條款：甲乙方、有效期、違約責任、爭議解決
- [ ] 準備 2-3 份實際合約樣本（匿名化處理）

### ✅ 配對程式設計計劃

**Week 0 配對建議**:
- **業務 + SA**: 定義需求與驗收標準（2 小時）
- **SA + Infra**: 設計基礎架構與部署方案（2 小時）
- **有 Python 經驗者 + 新手**: 一起建立第一個 API 端點（3 小時）

---

## Day 4-5: MVP 準備與第一個 Sprint

### ✅ MVP Scope 最終確認

**2 週 MVP 必須包含**:
- [ ] PDF 上傳功能（前端簡單表單 + 後端 API）
- [ ] PDF 文字萃取（PyMuPDF）
- [ ] 基礎文字比對（Python difflib）
- [ ] Claude API 分析差異（風險等級標註）
- [ ] 簡單的 HTML 報告輸出

**明確排除**（未來 Sprint）:
- ❌ 圖片/表格比對
- ❌ 複雜的頁面對齊演算法
- ❌ 使用者帳號系統
- ❌ 精美的前端介面

### ✅ Sprint 1 Planning（Week 1-2）

**工作項目拆解**:

1. **User Story 1**: 作為使用者，我要能上傳兩份 PDF 合約
   - Task 1.1: 建立 FastAPI 專案骨架（SA/Dev，4 小時）
   - Task 1.2: 實作 POST /api/v1/contracts/upload 端點（SA/Dev，6 小時）
   - Task 1.3: 建立簡單的 HTML 上傳表單（業務/SA，4 小時）
   - Task 1.4: 測試檔案上傳（業務，2 小時）

2. **User Story 2**: 系統要能萃取 PDF 文字
   - Task 2.1: 研究 PyMuPDF 使用方式（SA，3 小時）
   - Task 2.2: 實作 PDF → 純文字轉換（SA/Dev，6 小時）
   - Task 2.3: 處理多頁 PDF（SA/Dev，4 小時）
   - Task 2.4: 測試不同格式 PDF（業務，3 小時）

3. **User Story 3**: 系統要能比對兩份文字差異
   - Task 3.1: 使用 difflib 實作基礎比對（SA/Dev，4 小時）
   - Task 3.2: 產生結構化 diff 結果（SA/Dev，4 小時）
   - Task 3.3: 單元測試（SA，3 小時）

4. **User Story 4**: 系統要能用 Claude 分析差異
   - Task 4.1: 設計 Claude Prompt（業務 + SA，4 小時）
   - Task 4.2: 整合 Claude API（SA/Dev，6 小時）
   - Task 4.3: 解析 Claude 回應（SA/Dev，4 小時）
   - Task 4.4: 測試分析準確度（業務，4 小時）

5. **User Story 5**: 產生比對報告
   - Task 5.1: 設計報告格式（HTML）（業務，3 小時）
   - Task 5.2: 實作報告產生器（SA/Dev，6 小時）
   - Task 5.3: 整合前端顯示（SA，4 小時）

**總時數估計**: 約 70-80 小時（假設 2 人全職 = 160 小時，足夠）

### ✅ Definition of Done (DoD)

每個 User Story 完成必須符合:
- [ ] 程式碼通過 Black 格式檢查
- [ ] 有基本的單元測試（不要求 80% 覆蓋率）
- [ ] 在本地環境可執行
- [ ] 業務人員實際測試通過
- [ ] 簡單的使用說明文件

---

## Day 5: Sprint Kickoff

### ✅ Sprint 1 啟動會議

**議程**（1.5 小時）:
1. Review Sprint Goal: "完成可執行的合約比對 MVP"
2. 逐項確認每個 Task 的負責人
3. 確認每日 Standup 時間與格式
4. 設定 Demo 日期（Week 2 結束）
5. 風險識別與應對計劃

**每日 Standup 格式**（15 分鐘）:
- 每人回答三個問題：
  1. 昨天做了什麼？
  2. 今天要做什麼？
  3. 有什麼阻礙？
- 如果有阻礙，會後立即討論解決方案（不佔用 standup 時間）

### ✅ 風險與應對

**已識別的風險**:

| 風險                          | 機率 | 影響 | 應對措施                                    |
|-------------------------------|------|------|---------------------------------------------|
| 團隊 Python 經驗不足          | 高   | 高   | 配對程式、每日 code review、SA 承擔主要開發 |
| Claude API 成本超出預期       | 中   | 中   | 設定每日用量上限、監控 token 使用           |
| PDF 格式多樣性導致萃取失敗    | 高   | 中   | 準備多種範例測試、預留 buffer 時間          |
| 無專職 DevOps 導致部署困難    | 中   | 低   | MVP 階段使用本地執行，暫不部署雲端          |
| 業務需求理解偏差              | 中   | 高   | 每週 demo、頻繁溝通、early feedback         |

---

## Week 0 交付成果

**必須產出的文件/工件**:

- [ ] 技能評估彙整表
- [ ] 確認的 RACI 矩陣
- [ ] Azure DevOps Board（含 Sprint 1 工作項目）
- [ ] 開發環境設置完成（每個成員）
- [ ] Claude API Key 申請完成
- [ ] 2-3 份測試用合約樣本（匿名化）
- [ ] Sprint 1 Goal 與 DoD
- [ ] 風險登記表

**驗收標準**:
- [ ] 全體成員對 MVP 範圍有共識
- [ ] 每個人知道自己在 Sprint 1 的角色與任務
- [ ] 開發環境可以執行 Python + Git
- [ ] 第一次每日 standup 已排定

---

## 下一步

**Week 0 完成後**:
1. 開始 Sprint 1 執行（參考上方工作項目）
2. 每日 10:00 Standup（嚴格 15 分鐘）
3. 每週三下午 code review session（2 小時）
4. Week 2 結束前安排 Sprint Review + Retrospective

**緊急聯絡**:
- 技術問題: SA 負責
- 流程問題: 業務負責
- 工具問題: Infra 負責

---

**版本**: 1.0  
**建立日期**: 2026-05-28  
**維護者**: Blue-AI Team
