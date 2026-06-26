# MVP User Stories & Acceptance Criteria

**專案**: Blue-AI 合約比對助理（Contract Diff）  
**Sprint**: Sprint 1（Week 1-2）  
**目標**: 可執行的端到端合約比對功能

---

## Epic: 合約比對 MVP

**作為**企業法務/採購人員  
**我想要**能快速比對兩個版本的合約文件  
**以便**識別所有條款變更，避免遺漏重要修改

**成功指標**:
- 字元級準確率 >95%
- 單次比對時間 <3 分鐘（10 頁以內合約）
- 能標示出風險等級（高/中/低）

---

## User Story #1: 上傳合約文件

### 描述

**作為**使用者  
**我想要**能上傳兩份 PDF 格式的合約  
**以便**系統可以進行比對

### 驗收標準（Acceptance Criteria）

```gherkin
Given 我是一個登入的使用者
When 我在網頁上看到上傳介面
Then 我應該能看到兩個上傳欄位，分別標示「原始版本」和「修訂版本」

Given 我選擇了一份 PDF 檔案
When 我點擊「上傳原始版本」按鈕
Then 系統應該顯示檔案名稱與檔案大小
And 檔案應該上傳到後端伺服器

Given 我上傳的檔案不是 PDF 格式
When 我嘗試上傳該檔案
Then 系統應該顯示錯誤訊息「僅支援 PDF 格式」
And 不允許上傳

Given 我上傳的 PDF 檔案大於 10MB
When 我嘗試上傳該檔案
Then 系統應該顯示錯誤訊息「檔案大小不可超過 10MB」
And 不允許上傳

Given 我已成功上傳兩份 PDF
When 兩份檔案都上傳完成
Then 應該出現「開始比對」按鈕
```

### 技術任務（Tasks）

- [ ] **Task 1.1**: 建立 FastAPI 專案結構
  - 負責人: SA
  - 估時: 4 小時
  - 技術: FastAPI, Python 3.11+
  
- [ ] **Task 1.2**: 實作 POST `/api/v1/contracts/upload` 端點
  - 負責人: SA
  - 估時: 6 小時
  - 技術: FastAPI File Upload, 檔案驗證
  - 需求:
    - 接受 multipart/form-data
    - 驗證檔案類型（.pdf）
    - 驗證檔案大小（<10MB）
    - 回傳 file_id 與 upload_url
  
- [ ] **Task 1.3**: 建立簡單的上傳表單（HTML）
  - 負責人: 業務/SA
  - 估時: 4 小時
  - 技術: HTML5, JavaScript Fetch API
  - 需求:
    - 兩個檔案選擇器
    - 顯示上傳進度
    - 錯誤訊息顯示
  
- [ ] **Task 1.4**: 整合測試
  - 負責人: 業務
  - 估時: 2 小時
  - 測試:
    - 上傳正常 PDF（成功）
    - 上傳 Word 檔（失敗）
    - 上傳 >10MB PDF（失敗）

### Definition of Done

- [x] API 端點可正常接收 PDF 檔案
- [x] 檔案驗證機制正常運作
- [x] 前端表單可正常上傳
- [x] 有基本的錯誤處理
- [x] 業務實際測試通過
- [x] 程式碼通過 Black 格式化

---

## User Story #2: 萃取 PDF 文字內容

### 描述

**作為**系統  
**我需要**能從 PDF 中萃取純文字內容  
**以便**進行後續的文字比對

### 驗收標準

```gherkin
Given 系統收到一份上傳的 PDF 檔案
When 系統開始處理該 PDF
Then 應該能萃取出所有可讀取的文字內容

Given PDF 包含多頁內容（例如 10 頁）
When 系統萃取文字
Then 應該按頁面順序萃取所有文字
And 保留頁面資訊（第幾頁）

Given PDF 包含圖片或掃描文件
When 系統嘗試萃取文字
Then 應該能識別出該 PDF 為圖片型（無法萃取）
And 回傳適當的錯誤訊息

Given PDF 使用繁體中文
When 系統萃取文字
Then 應該正確識別中文字元
And 不應該出現亂碼

Given PDF 包含表格
When 系統萃取文字
Then 應該盡可能保留表格結構（MVP 階段盡力而為，不強制要求）
```

### 技術任務

- [ ] **Task 2.1**: 研究 PyMuPDF 使用方式
  - 負責人: SA
  - 估時: 3 小時
  - 輸出: 技術 POC 文件與範例程式碼
  
- [ ] **Task 2.2**: 實作 PDF 文字萃取模組
  - 負責人: SA
  - 估時: 6 小時
  - 技術: PyMuPDF (fitz)
  - 需求:
    ```python
    def extract_text_from_pdf(pdf_path: str) -> List[PageText]:
        """
        返回格式:
        [
          {"page_number": 1, "text": "第一頁內容..."},
          {"page_number": 2, "text": "第二頁內容..."}
        ]
        """
        pass
    ```
  
- [ ] **Task 2.3**: 處理多頁 PDF 與錯誤情境
  - 負責人: SA
  - 估時: 4 小時
  - 需求:
    - 檢測圖片型 PDF（文字內容 <100 字元判定為掃描檔）
    - 處理損壞的 PDF
    - 限制最大頁數（MVP: 50 頁）
  
- [ ] **Task 2.4**: 測試不同格式 PDF
  - 負責人: 業務
  - 估時: 3 小時
  - 測試案例:
    - 純文字 PDF（Microsoft Word 產生）
    - 含圖片的 PDF
    - 掃描 PDF（預期失敗）
    - 多頁 PDF（10+ 頁）
    - 繁體中文合約

### Definition of Done

- [x] 能正確萃取純文字 PDF 內容
- [x] 能識別掃描 PDF 並回傳錯誤
- [x] 繁體中文無亂碼問題
- [x] 有單元測試
- [x] 業務用實際合約測試通過

---

## User Story #3: 比對兩份文件差異

### 描述

**作為**系統  
**我需要**能精確比對兩份文字的差異  
**以便**識別出新增、刪除、修改的內容

### 驗收標準

```gherkin
Given 系統有兩份已萃取的文字內容（原始版、修訂版）
When 系統執行比對演算法
Then 應該產生結構化的 diff 結果

Given 修訂版新增了一段文字
When 系統比對
Then diff 結果應該標示為「新增」(addition)
And 包含新增的完整內容

Given 修訂版刪除了一段文字
When 系統比對
Then diff 結果應該標示為「刪除」(deletion)
And 包含被刪除的完整內容

Given 修訂版修改了部分文字（例如金額從 100 萬改為 200 萬）
When 系統比對
Then diff 結果應該標示為「修改」(modification)
And 同時顯示修改前與修改後的內容

Given 兩份文件完全相同
When 系統比對
Then diff 結果應該為空（無差異）
```

### 技術任務

- [ ] **Task 3.1**: 使用 difflib 實作基礎比對
  - 負責人: SA
  - 估時: 4 小時
  - 技術: Python difflib.unified_diff 或 difflib.SequenceMatcher
  - 需求:
    ```python
    def compare_texts(original: str, revised: str) -> List[DiffItem]:
        """
        返回格式:
        [
          {
            "type": "addition",
            "content": "新增的文字",
            "position": {"line": 10}
          },
          {
            "type": "deletion",
            "content": "被刪除的文字",
            "position": {"line": 5}
          },
          {
            "type": "modification",
            "original_content": "100萬元",
            "revised_content": "200萬元",
            "position": {"line": 8}
          }
        ]
        """
        pass
    ```
  
- [ ] **Task 3.2**: 產生結構化 diff 結果
  - 負責人: SA
  - 估時: 4 小時
  - 需求:
    - 計算總變更數量（新增/刪除/修改各幾處）
    - 計算變更百分比
    - 標示變更位置（行號）
  
- [ ] **Task 3.3**: 單元測試
  - 負責人: SA
  - 估時: 3 小時
  - 測試案例:
    - 完全相同文件（預期 0 差異）
    - 僅新增內容
    - 僅刪除內容
    - 新增+刪除+修改混合
    - 大量差異（>50% 變更）

### Definition of Done

- [x] diff 演算法能正確識別新增/刪除/修改
- [x] 輸出為結構化資料（JSON）
- [x] 有完整單元測試（覆蓋率 >80%）
- [x] 效能測試：10 頁文件比對 <5 秒

---

## User Story #4: AI 分析差異風險等級

### 描述

**作為**法務人員  
**我想要**AI 能自動標示哪些變更是高風險的  
**以便**我優先審查重要條款的修改

### 驗收標準

```gherkin
Given 系統已產生 diff 結果
When 系統將 diff 傳送給 Claude API
Then Claude 應該回傳每個變更的風險等級

Given 變更涉及「違約責任」或「賠償金額」
When Claude 分析該變更
Then 應該標示為「高風險」(high)

Given 變更涉及「通知地址」或「格式調整」
When Claude 分析該變更
Then 應該標示為「低風險」(low)

Given 變更涉及「付款條件」或「交付期限」
When Claude 分析該變更
Then 應該標示為「中風險」(medium)

Given Claude API 呼叫失敗（timeout 或錯誤）
When 系統偵測到錯誤
Then 應該回傳預設風險等級（medium）並記錄錯誤
And 不應該讓整個比對流程失敗
```

### 技術任務

- [ ] **Task 4.1**: 設計 Claude Prompt
  - 負責人: 業務 + SA（配對）
  - 估時: 4 小時
  - 需求:
    ```python
    SYSTEM_PROMPT = """
    你是專業的合約審查助理。
    分析合約條款變更，判斷風險等級。
    
    風險等級定義:
    - high: 涉及金額、違約責任、法律義務、爭議解決
    - medium: 涉及時程、交付條件、通知義務
    - low: 格式調整、錯字修正、聯絡資訊
    
    輸出格式:
    <analysis>
      <change id="1">
        <risk_level>high</risk_level>
        <reason>修改違約賠償金額從 100 萬提高至 500 萬</reason>
        <recommendation>建議法務主管審查</recommendation>
      </change>
    </analysis>
    """
    ```
  
- [ ] **Task 4.2**: 整合 Claude API
  - 負責人: SA
  - 估時: 6 小時
  - 技術: anthropic Python SDK
  - 需求:
    - 使用 claude-sonnet-4-6 模型
    - 設定 max_tokens=4096
    - 實作 retry 機制（最多 3 次）
    - 計算 token 使用量
  
- [ ] **Task 4.3**: 解析 Claude 回應
  - 負責人: SA
  - 估時: 4 小時
  - 需求:
    - 解析 XML 格式回應
    - 驗證風險等級（必須是 high/medium/low）
    - 處理 Claude 回應格式錯誤的情況
  
- [ ] **Task 4.4**: 測試分析準確度
  - 負責人: 業務
  - 估時: 4 小時
  - 測試:
    - 準備 10 個真實合約變更案例
    - 業務人員手動標記風險等級
    - 比對 Claude 判斷與人工判斷的一致性
    - 目標: >80% 一致性

### Definition of Done

- [x] Claude API 整合成功
- [x] 能正確解析 Claude 回應
- [x] 有錯誤處理與 retry 機制
- [x] 業務測試準確度 >80%
- [x] 記錄 token 使用量（用於成本估算）

---

## User Story #5: 產生比對報告

### 描述

**作為**使用者  
**我想要**能看到清楚易懂的比對報告  
**以便**快速了解兩份合約的差異

### 驗收標準

```gherkin
Given 系統完成所有分析步驟
When 系統產生報告
Then 報告應該包含以下資訊:
  - 文件基本資訊（檔名、頁數、比對時間）
  - 總變更摘要（共 X 處變更，高風險 Y 處）
  - 詳細差異列表（逐條顯示）
  - 每個變更的風險等級與建議

Given 報告包含多處變更
When 我瀏覽報告
Then 高風險變更應該排在最前面
And 使用紅色標示

Given 我點擊某個變更項目
When 報告展開該項目
Then 應該顯示完整的原文與修改後文字
And 以對照方式呈現（before/after）

Given 系統產生報告
When 報告完成
Then 應該提供「下載 PDF」或「下載 HTML」選項
```

### 技術任務

- [ ] **Task 5.1**: 設計報告格式（HTML 模板）
  - 負責人: 業務
  - 估時: 3 小時
  - 需求:
    - 使用 Jinja2 模板引擎
    - 包含 CSS 樣式（高風險=紅色，中=橘色，低=綠色）
    - RWD 設計（手機也能看）
  
- [ ] **Task 5.2**: 實作報告產生器
  - 負責人: SA
  - 估時: 6 小時
  - 需求:
    ```python
    def generate_report(
        original_file: str,
        revised_file: str,
        diff_result: List[DiffItem],
        analysis_result: List[RiskAnalysis]
    ) -> str:
        """
        返回 HTML 格式報告
        """
        pass
    ```
  
- [ ] **Task 5.3**: 整合前端顯示
  - 負責人: SA
  - 估時: 4 小時
  - 需求:
    - GET `/api/v1/reports/{report_id}` 端點
    - 前端接收 HTML 並顯示
    - 提供下載按鈕

### Definition of Done

- [x] 報告包含所有必要資訊
- [x] 高風險變更優先顯示
- [x] HTML 格式美觀易讀
- [x] 可下載報告
- [x] 業務驗收通過

---

## User Story #6: 端到端流程整合

### 描述

**作為**使用者  
**我想要**能一鍵完成上傳→比對→產生報告的完整流程  
**以便**快速獲得分析結果

### 驗收標準

```gherkin
Given 我上傳了兩份合約
When 我點擊「開始比對」按鈕
Then 系統應該自動執行:
  1. 萃取兩份 PDF 的文字
  2. 比對差異
  3. Claude AI 分析
  4. 產生報告
And 顯示處理進度

Given 系統正在處理
When 處理時間超過 10 秒
Then 應該顯示進度指示器（例如「正在萃取 PDF...」）

Given 處理過程中發生錯誤（例如 PDF 無法讀取）
When 錯誤發生
Then 應該顯示清楚的錯誤訊息
And 不應該顯示技術性錯誤（例如 stack trace）

Given 處理完成
When 報告產生
Then 應該自動跳轉到報告頁面
And 顯示成功訊息
```

### 技術任務

- [ ] **Task 6.1**: 實作整合 API 端點
  - 負責人: SA
  - 估時: 4 小時
  - 需求:
    ```python
    POST /api/v1/contracts/compare
    {
      "original_file_id": "xxx",
      "revised_file_id": "yyy"
    }
    
    Response:
    {
      "success": true,
      "report_id": "zzz",
      "report_url": "/reports/zzz"
    }
    ```
  
- [ ] **Task 6.2**: 實作非同步處理（可選）
  - 負責人: SA
  - 估時: 6 小時（可選，如果時間不夠則先做同步）
  - 技術: Celery 或 FastAPI BackgroundTasks
  - 需求:
    - 長時間處理不阻塞 API
    - 提供狀態查詢端點
  
- [ ] **Task 6.3**: 前端整合與進度顯示
  - 負責人: 業務/SA
  - 估時: 4 小時
  - 需求:
    - 呼叫整合 API
    - 顯示 loading 動畫
    - 錯誤處理與顯示
  
- [ ] **Task 6.4**: 端到端測試
  - 負責人: 全員
  - 估時: 3 小時
  - 測試:
    - 完整流程（上傳→比對→報告）
    - 錯誤情境（無效 PDF、網路中斷）
    - 效能測試（10 頁合約）

### Definition of Done

- [x] 完整流程可正常執行
- [x] 有錯誤處理
- [x] 處理時間 <3 分鐘（10 頁合約）
- [x] 所有團隊成員測試通過
- [x] 可進行 Demo

---

## Sprint 1 總結

### 預期交付成果

1. ✅ 可執行的合約比對 Web 應用
2. ✅ 後端 API（FastAPI）
3. ✅ 簡單的前端介面（HTML）
4. ✅ Claude AI 整合
5. ✅ 端到端測試通過
6. ✅ 基本的使用說明文件

### 技術債（已知但可接受）

- 🔶 前端介面較陽春（未來改用 React）
- 🔶 尚未支援表格比對
- 🔶 尚未支援圖片/圖表比對
- 🔶 無使用者帳號系統
- 🔶 未部署至雲端（僅本地執行）

### 下一個 Sprint 可能的優化

- 改善前端 UI/UX
- 加入頁面對齊演算法（Hybrid Multi-Phase）
- 支援表格比對
- 建立使用者帳號系統
- 部署至 Azure

---

**文件版本**: 1.0  
**建立日期**: 2026-05-28  
**維護者**: Blue-AI Team
