---
name: weekly-report
description: 週報彙整助理 - 串接 ADO 與 Git 自動彙整各專案週報與進度
skill_type: agent
trigger: 當需要產生週報、彙整專案進度、分析開發狀況時使用
---

# 週報彙整助理

## 功能目標
- 自動串接 Azure DevOps (ADO) 與 Git
- 收集各專案看板數據
- 彙整開發進度與里程碑
- 產生週報並提供改善建議
- 節省人工彙整時間 85% 以上

## 使用方式
```
/weekly-report [--date <週期>] [--projects <專案清單>] [--format <輸出格式>]
```

## 處理流程
1. **數據收集**
   - 連接 ADO API 取得工作項目（Work Items）
   - 取得 Sprint 進度與 Burndown 數據
   - 拉取 Git 提交記錄與分支狀況
   - 收集 Pull Request 與 Code Review 統計

2. **進度分析**
   - 計算任務完成率
   - 識別延遲項目與阻礙
   - 統計程式碼提交量與品質
   - 分析團隊產能與負載

3. **風險識別**
   - 標記逾期或高風險任務
   - 檢測技術債累積
   - 識別資源瓶頸
   - 預警潛在延誤

4. **建議生成**
   - 提供優先順序調整建議
   - 資源分配優化
   - 流程改善建議
   - 下週重點規劃

5. **報告產出**
   - 結構化週報文件
   - 視覺化圖表
   - 匯出至 Email / Slack / Teams

## 輸出範例
```markdown
# 專案週報 - Week 22 (2026/05/26-05/30)

## 📊 整體概況
- **參與專案**: 5 個
- **團隊成員**: 12 人
- **本週完成**: 43 個工作項目
- **整體進度**: 符合預期 ✅

---

## 專案一：Blue-AI Platform

### Sprint 進度
- **完成率**: 87% (26/30 stories)
- **Story Points**: 52/60 完成
- **Burndown**: 輕微落後 ⚠️

### 本週完成
- ✅ 會議助理 API 開發 (8 points)
- ✅ 財務報表解析模組 (13 points)
- ✅ 前端介面優化 (5 points)

### 進行中
- 🔄 週報自動化整合 (8 points) - 80%
- 🔄 單元測試補強 (3 points) - 60%

### 阻礙事項
- ⚠️ ADO API 權限問題 - 等待 IT 處理
- ⚠️ 第三方語音 API 測試環境延遲

### Git 統計
- **Commits**: 87 次
- **PR Merged**: 12 個
- **Code Review**: 平均 4.2 小時
- **熱點檔案**: `src/api/meeting.py` (15 次修改)

---

## 專案二：Data Pipeline

### Sprint 進度
- **完成率**: 95% (19/20 stories)
- **Status**: 超前進度 🎉

### 本週亮點
- ✨ 效能優化完成，處理速度提升 40%
- ✨ 錯誤處理機制強化，穩定度大幅改善

---

## 📈 團隊統計

| 成員 | 完成任務 | Story Points | Commits | 負載狀況 |
|------|----------|--------------|---------|----------|
| Alice | 6 | 18 | 24 | 🟢 適中 |
| Bob | 8 | 22 | 31 | 🟡 偏高 |
| Carol | 5 | 15 | 19 | 🟢 適中 |

## ⚠️ 風險與建議

### 高優先級
1. **ADO API 權限問題** - 建議本週內完成申請
2. **Bob 工作負載偏高** - 建議部分任務重新分配

### 改善建議
- 增加前端自動化測試覆蓋率（目前 68%）
- 建立統一的 Code Review Checklist
- 安排技術分享會（主題：API 效能優化）

## 📅 下週重點
1. 完成會議助理功能整合測試
2. 啟動財務報表 UI 開發
3. 進行 Sprint Review 與 Retrospective
4. 規劃下一個 Sprint 目標
```

## 技術整合
- ADO API: `azure-devops` Python SDK
- Git API: GitPython / PyGithub
- 數據處理: pandas
- AI 分析: Claude API
- 通知推送: SMTP / Slack Webhook / MS Teams

## 設定檔範例
```json
{
  "ado": {
    "organization": "your-org",
    "project": "Blue-AI",
    "pat": "${ADO_PAT}"
  },
  "git": {
    "repos": [
      "https://github.com/company/blue-ai-platform",
      "https://github.com/company/blue-ai-skills"
    ]
  },
  "schedule": {
    "day": "Friday",
    "time": "17:00"
  }
}
```
