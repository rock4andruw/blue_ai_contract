---
name: presentation-generator
description: 制式簡報與報告自動生成助理 - 依公司風格自動產生簡報與報表
skill_type: agent
trigger: 當需要產生簡報、報告、依範本填入數據時使用
---

# 制式簡報與報告自動生成助理

## 功能目標
- 依公司規範或單位風格建立簡報範本
- 自動從數據源產生圖表與報表
- 智能填入數字與說明
- 產業專屬報告模板（如金融業）
- 支援多種輸出格式（PPT, PDF, HTML）
- 降低簡報製作時間 75% 以上

## 使用方式
```
/presentation-generator \
  --template <範本名稱> \
  --data <資料來源> \
  --output <輸出格式>
```

## 處理流程

### 1. 範本管理
- **預建範本庫**
  - 月報/季報/年報
  - 專案進度報告
  - 財務報表
  - 業務分析
  - 技術文件

- **客製化範本**
  - 企業識別系統套用（Logo, 配色）
  - 部門專屬樣式
  - 產業特定格式

### 2. 資料整合
- **資料來源**
  - Excel / CSV 檔案
  - 資料庫查詢
  - API 即時資料
  - 手動輸入

- **資料處理**
  - 自動計算（總和、平均、成長率）
  - 資料驗證與清理
  - 趨勢分析

### 3. 內容生成
- **自動填入**
  - 數字與統計
  - 日期與期間
  - 動態文字說明

- **智能撰寫**
  - 摘要與結論
  - 洞察與建議
  - 風險提示

### 4. 視覺化
- **圖表生成**
  - 長條圖、折線圖、圓餅圖
  - 組合圖、瀑布圖
  - 趨勢圖、散佈圖

- **排版優化**
  - 自動版面配置
  - 圖表大小調整
  - 美觀度優化

### 5. 輸出與分享
- PowerPoint (.pptx)
- PDF
- Google Slides
- HTML (Web 檢視)

## 範本範例

### 範本 1: 金融產業月報
```yaml
template: financial_monthly_report
industry: finance
sections:
  - cover_page:
      title: "{{month}} 月營運報告"
      subtitle: "{{company_name}}"
      date: "{{report_date}}"
      
  - executive_summary:
      layout: text_with_highlights
      content:
        - 營收概況
        - 重要指標
        - 本月亮點
        
  - revenue_analysis:
      layout: chart_with_explanation
      charts:
        - type: bar_chart
          data_source: revenue_by_product
          title: "產品別營收分析"
        - type: line_chart
          data_source: revenue_trend
          title: "營收趨勢"
      
  - profit_analysis:
      layout: dual_chart
      charts:
        - type: waterfall
          data_source: profit_breakdown
        - type: pie_chart
          data_source: cost_structure
          
  - kpi_dashboard:
      layout: metrics_grid
      metrics:
        - name: "總營收"
          value: "{{total_revenue}}"
          comparison: "{{mom_change}}%"
        - name: "毛利率"
          value: "{{gross_margin}}%"
          comparison: "{{yoy_change}}%"
          
  - risks_and_opportunities:
      layout: two_column
      
  - action_items:
      layout: table
      
  - appendix:
      layout: data_tables
```

---

### 範本 2: 專案進度報告
```yaml
template: project_progress_report
type: project_management
sections:
  - cover_page:
      project_name: "{{project_name}}"
      report_period: "{{period}}"
      
  - project_overview:
      - 專案目標
      - 當前階段
      - 整體進度: "{{overall_progress}}%"
      
  - milestone_status:
      layout: timeline
      data_source: milestones
      
  - sprint_summary:
      layout: burndown_chart
      data_source: sprint_data
      
  - team_performance:
      layout: metrics_cards
      metrics:
        - "完成 Story Points"
        - "速度 (Velocity)"
        - "缺陷率"
        
  - risks_and_issues:
      layout: rag_status  # Red/Amber/Green
      
  - next_steps:
      layout: action_items_table
```

## 實際輸出範例

### 金融業月報 - 執行摘要頁
```
╔══════════════════════════════════════════════════════════╗
║  📊 2026年5月 營運報告                                    ║
║  Blue-AI Financial Services                              ║
║  報告日期: 2026-06-05                                    ║
╚══════════════════════════════════════════════════════════╝

【執行摘要】

本月營收表現優異,較上月成長 8.5%,主要受惠於 AI 服務產品線的強勁需求。
毛利率提升至 42.5%,顯示營運效率持續改善。

📈 重要指標

┌─────────────────┬──────────┬──────────┬─────────┐
│ 指標            │ 本月     │ 上月     │ 月增率  │
├─────────────────┼──────────┼──────────┼─────────┤
│ 總營收          │ $10.5M   │ $9.7M    │ +8.5%   │
│ 毛利率          │ 42.5%    │ 40.7%    │ +1.8%   │
│ 營業利益        │ $2.1M    │ $1.87M   │ +12.3%  │
│ 淨利            │ $1.58M   │ $1.44M   │ +9.8%   │
│ 新客戶數        │ 23       │ 18       │ +27.8%  │
└─────────────────┴──────────┴──────────┴─────────┘

✨ 本月亮點

• AI 會議助理服務訂閱數突破 500 家企業
• 完成與 3 家金控公司的策略合作簽約
• 客戶滿意度達 4.7/5.0 (+0.2)
• 系統可用性維持 99.8%

⚠️ 需關注事項

• 應收帳款天數增加至 45 天 (目標: 30 天)
• 研發人員離職率上升至 8% (需改善)
```

---

### 產品別營收分析頁
```
╔══════════════════════════════════════════════════════════╗
║  產品別營收分析                                          ║
╚══════════════════════════════════════════════════════════╝

【營收組成】

會議助理服務    ████████████████████ 45% ($4.73M)
財務分析服務    ██████████████ 30% ($3.15M)
週報自動化      ████████ 15% ($1.58M)
其他服務        ████ 10% ($1.05M)

【同期比較】

      會議助理    財務分析    週報自動化    其他
5月   ▓▓▓▓▓▓▓▓▓  ▓▓▓▓▓▓     ▓▓▓          ▓▓
4月   ▒▒▒▒▒▒▒▒   ▒▒▒▒▒      ▒▒           ▒▒
      +12%       +6%        +18%         +5%

【關鍵洞察】

✓ 會議助理服務持續為主要營收來源,成長強勁
✓ 週報自動化服務增長最快 (+18%),顯示市場需求升溫
✓ 建議加強財務分析服務的行銷力度
✓ 評估開發新產品線以分散風險

【客戶分布】

企業規模          客戶數    平均訂閱金額
大型企業 (>1000人)  45      $85,000/年
中型企業 (100-1000) 180     $28,000/年
小型企業 (<100)     275     $8,500/年
```

## 自動化功能

### 1. 數據驅動文字生成
```python
# 範例: 自動產生營收說明
template = """
本月營收為 ${revenue:,.0f},較上月{comparison}。
主要{driver}為 {top_product},貢獻 ${top_revenue:,.0f}。
{outlook}
"""

# AI 自動填入
output = """
本月營收為 $10,500,000,較上月成長 8.5%。
主要成長動能為 AI 會議助理服務,貢獻 $4,730,000。
預期下月在新產品上線後將持續成長趨勢。
"""
```

### 2. 智能圖表選擇
系統會依資料類型自動選擇最適合的圖表：
- 時間序列 → 折線圖
- 組成比例 → 圓餅圖
- 多項目比較 → 長條圖
- 趨勢+組成 → 堆疊面積圖
- 階層結構 → 樹狀圖

### 3. 異常標示
自動標示重要變化：
- 🔴 下降超過 10%
- 🟢 成長超過 10%
- ⚠️ 超出預期範圍
- 📈 創新高
- 📉 創新低

## 技術整合

### 簡報生成
- **python-pptx**: PowerPoint 檔案操作
- **reportlab**: PDF 生成
- **Google Slides API**: 雲端簡報

### 圖表產生
- **Matplotlib**: 基礎圖表
- **Plotly**: 互動式圖表
- **Seaborn**: 統計視覺化
- **ECharts**: 網頁圖表

### AI 分析
- **Claude API**: 文字生成、洞察分析
- **GPT-4**: 輔助文字潤飾

### 資料處理
- **Pandas**: 資料分析
- **NumPy**: 數值計算
- **SQLAlchemy**: 資料庫查詢

## 範本庫結構

```
templates/
├── financial/
│   ├── monthly_report.yaml
│   ├── quarterly_report.yaml
│   ├── annual_report.yaml
│   └── board_meeting.yaml
├── project/
│   ├── progress_report.yaml
│   ├── sprint_review.yaml
│   └── retrospective.yaml
├── sales/
│   ├── pipeline_review.yaml
│   └── performance_report.yaml
└── technical/
    ├── architecture_review.yaml
    └── incident_report.yaml
```

## 使用案例

### 案例 1: 產生月報
```bash
/presentation-generator \
  --template financial/monthly_report \
  --data revenue_data_2026-05.xlsx \
  --company-style blue-ai-standard \
  --output report_2026-05.pptx
```

### 案例 2: 專案進度報告
```bash
/presentation-generator \
  --template project/progress_report \
  --data-source ado-api \
  --project blue-ai-platform \
  --period 2026-W22 \
  --output weekly_report.pdf
```

### 案例 3: 客製化範本
```bash
/presentation-generator \
  --create-template \
  --name custom_board_report \
  --based-on financial/quarterly_report \
  --customize-sections "cover,executive_summary,financials,strategy" \
  --save-to templates/custom/
```

## 品質保證
- 數字準確性驗證
- 圖表清晰度檢查
- 文字錯別字檢測
- 格式一致性確認
- 符合企業識別規範
