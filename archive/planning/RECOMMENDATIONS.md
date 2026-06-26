# Contract-Diff 專案建議報告

**審閱日期**: 2026-05-29  
**審閱範圍**: 完整開發藍圖  
**目標**: Contract-Diff (合約比對助理) MVP 開發

---

## 📋 執行摘要

### 🎯 目前狀態評估

**✅ 已完成的優秀工作**:
```
✓ 完整的研究基礎 (6篇高引用論文分析)
✓ 詳細的技術設計 (162KB 技術文件)
✓ 清晰的技術路線圖 (5大方向, 61KB)
✓ 完整的專案計劃 (11週, WBS, 預算)
✓ 9個 Claude Code Skills (8題 + PM)
✓ 專案文檔齊全 (README, CLAUDE.md)
```

**📊 文件完整度**: ⭐⭐⭐⭐⭐ (5/5)  
**📊 技術準備度**: ⭐⭐⭐⭐☆ (4/5)  
**📊 執行準備度**: ⭐⭐⭐☆☆ (3/5)

### ⚠️ 關鍵發現

**優勢**:
1. 學術基礎紮實 - 基於最新 2026 年論文
2. 技術選型清晰 - Hybrid Multi-Phase 演算法明確
3. 架構設計完整 - 微服務架構、API 規格齊全
4. 風險識別充分 - 已識別 10 個主要風險

**挑戰**:
1. 🔴 **尚未開始實際編碼** - 所有文件都是規劃
2. 🟡 **團隊資源未確認** - 需要 6 人團隊 (2後端 + 1ML + 1前端 + 1DevOps + 1QA)
3. 🟡 **第三方依賴成本未驗證** - Claude API、Azure 成本預估需驗證
4. 🟢 **開發環境未建立** - Docker、PostgreSQL、Redis 尚未配置

---

## 🚨 關鍵建議（優先順序排序）

### 🏆 Priority 0: 立即行動 (本週)

#### 建議 1: 啟動 MVP 最小驗證 ⏰ 1-2天

**目標**: 驗證核心技術可行性，避免過度規劃

**行動步驟**:
```bash
1. 建立基礎 Python 專案
   mkdir -p contract-diff-mvp/{src,tests}
   cd contract-diff-mvp
   python -m venv venv
   source venv/bin/activate
   
2. 安裝核心依賴
   pip install PyMuPDF pdfplumber difflib anthropic
   
3. 實作最簡單的比對（2小時內完成）:
   - PDF 文字提取
   - difflib 文字比對
   - 輸出 Markdown 報告
   
4. 用真實合約測試（2個版本的 SLA）
```

**成功標準**:
- ✅ 能提取 PDF 文字
- ✅ 能產生差異報告
- ✅ 處理時間 < 30 秒 (10頁文件)

**風險**: 如果這步失敗，說明基礎工具有問題，需調整技術選型

---

#### 建議 2: Claude API 成本驗證 ⏰ 半天

**問題**: 預算預估 Claude API <$0.50/比對，但未實測

**行動**:
```python
# 測試腳本
import anthropic
client = anthropic.Anthropic()

# 模擬一次完整風險分析
test_prompt = """
分析以下合約條款變更...
[貼入真實的 500-1000 字條款]
"""

response = client.messages.create(
    model="claude-opus-4-20250514",
    max_tokens=2000,
    messages=[{"role": "user", "content": test_prompt}]
)

# 計算成本
input_tokens = response.usage.input_tokens
output_tokens = response.usage.output_tokens
cost = (input_tokens / 1000000 * 15) + (output_tokens / 1000000 * 75)

print(f"Cost per analysis: ${cost:.4f}")
print(f"Estimated cost for 10 clauses: ${cost * 10:.2f}")
```

**成功標準**:
- ✅ 單次分析成本 < $0.10
- ✅ 完整合約 (10 條款) < $1.00

**如果超標**: 改用 Claude Sonnet 或減少呼叫次數

---

#### 建議 3: 確認團隊組成 ⏰ 本週內

**目前規劃需要**:
- 後端工程師 × 2
- ML 工程師 × 1
- 前端工程師 × 1
- DevOps × 0.5
- QA × 1

**問題**: 
1. 團隊是否已到位？
2. 技能是否匹配（Legal-BERT、CV、Claude API）？
3. 是否需要招聘或培訓？

**行動**:
```
□ 盤點現有團隊技能
□ 識別技能缺口
□ 決定: 招聘 vs 培訓 vs 外包
□ 確認每個人的投入度與時間
```

---

### 🥇 Priority 1: 本月完成 (Week 1-4)

#### 建議 4: 簡化 MVP 範疇 ⏰ 2週

**問題**: 目前規劃太完整（11週），風險是投入大量時間但未驗證市場需求

**建議**: 採用 **2週 Sprint MVP**

**MVP 功能範圍** (僅限):
```
✅ PDF 文字提取
✅ 基礎 difflib 比對
✅ Claude API 風險分析 (5 種標準條款)
✅ Markdown 報告輸出
✅ 簡單 FastAPI 端點 (上傳 + 比對)
❌ 不做: 詐欺檢測
❌ 不做: Legal-BERT NER
❌ 不做: 七階段匹配
❌ 不做: 前端 UI
❌ 不做: Kubernetes 部署
```

**2週衝刺計劃**:
```
Week 1:
  Day 1-2: 文件處理器 (PDF → text)
  Day 3-4: 比對引擎 (difflib + 結構化輸出)
  Day 5: Claude API 整合
  
Week 2:
  Day 1-2: FastAPI 端點
  Day 3: 測試與除錯
  Day 4: 真實合約驗證
  Day 5: Demo 給 Stakeholders
```

**成功標準**:
- ✅ 能比對真實合約並輸出報告
- ✅ Stakeholders 認可價值
- ✅ 決定是否繼續投入

---

#### 建議 5: 建立持續驗證機制 ⏰ 持續

**問題**: 文件中提到 94% AI 準確率，但如何驗證？

**建議**: 建立測試資料集

**黃金標準測試集**:
```
收集 10 組真實合約對:
- 5 組 SLA (已知風險條款)
- 3 組 NDA (已知變更點)
- 2 組 MSA (複雜案例)

人工標註:
- 標記所有應偵測到的變更
- 標記風險等級 (Critical/High/Medium/Low)
- 記錄預期的風險說明

每次迭代都跑測試:
- Precision (找到的風險有多少是對的)
- Recall (應該找到的風險找到了多少)
- F1 Score
```

**工具**:
```python
# tests/test_accuracy.py
def test_contract_diff_accuracy():
    test_cases = load_golden_dataset()
    
    for case in test_cases:
        result = compare_contracts(case.old, case.new)
        
        # 計算指標
        tp = len(set(result.changes) & set(case.expected_changes))
        fp = len(set(result.changes) - set(case.expected_changes))
        fn = len(set(case.expected_changes) - set(result.changes))
        
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1 = 2 * precision * recall / (precision + recall)
        
        assert f1 > 0.85, f"F1 score {f1} below threshold"
```

---

### 🥈 Priority 2: 中期優化 (Month 2-3)

#### 建議 6: 漸進式加入進階功能

**策略**: 不要一次實作所有功能，依價值排序

**功能優先順序** (基於 ROI):

| 功能 | 實作難度 | 使用者價值 | ROI | 優先級 |
|------|---------|-----------|-----|--------|
| **Claude 風險分析** | 🟢 低 | ⭐⭐⭐⭐⭐ | 極高 | P0 ✅ |
| **PDF 版本分析** | 🟡 中 | ⭐⭐⭐⭐ | 高 | P1 |
| **七階段匹配** | 🟡 中 | ⭐⭐⭐ | 中 | P2 |
| **Legal-BERT NER** | 🔴 高 | ⭐⭐⭐ | 中 | P2 |
| **表格差異** | 🟡 中 | ⭐⭐⭐ | 中 | P2 |
| **視覺差異** | 🔴 高 | ⭐⭐ | 低 | P3 |
| **LBP 詐欺檢測** | 🔴 高 | ⭐⭐ | 低 | P3 |

**每 2 週加入 1-2 個新功能**，持續驗證價值

---

#### 建議 7: 技術債務管理

**觀察**: 初期會寫很多快速但不完美的程式碼

**策略**: 
```
✓ 允許 MVP 階段的技術債
✓ 但必須記錄在 TODO.md
✓ 每個 Sprint 預留 20% 時間還技術債
```

**技術債範例**:
```markdown
## Technical Debt Backlog

### High Priority
- [ ] 文件處理器沒有錯誤處理（會 crash）
- [ ] API 沒有 rate limiting（可被 DDoS）
- [ ] 密碼寫死在程式碼中（安全風險）

### Medium Priority
- [ ] difflib 對大文件很慢（>1000頁）
- [ ] 沒有單元測試（覆蓋率 0%）
- [ ] LOG 太少（難以 debug）

### Low Priority
- [ ] 程式碼重複（DRY 原則）
- [ ] 變數命名不一致
```

---

### 🥉 Priority 3: 長期策略 (Month 4-6)

#### 建議 8: 準備擴展至其他題目

**觀察**: Contract-Diff 只是 8 題中的第 4 題

**策略**: 
```
如果 Contract-Diff 成功 → 複製模式至其他題目

共用元件:
✓ Document Processor (題 1,3,4,5,8 都需要)
✓ Claude API 整合 (所有題目)
✓ Report Generator (所有題目)
✓ FastAPI 框架 (所有題目)

題目特定:
- 題 1 (會議): Azure Speech API
- 題 2 (財務): pandas, 表格處理
- 題 3 (週報): ADO/Git API
- 題 6 (維運): LOG 解析, 時序分析
- 題 7 (架構圖): Mermaid, PlantUML
```

**建議**: 
- ✅ 設計時考慮可重用性
- ✅ 模組化架構（不寫 monolith）
- ✅ 文件清楚（團隊其他人可複製）

---

#### 建議 9: 建立 AI 成本控管機制

**問題**: Claude API 無限制使用會爆預算

**建議設定**:
```python
# config/limits.py
COST_LIMITS = {
    'daily_max_usd': 50.0,        # 每日上限 $50
    'per_comparison_max_usd': 2.0, # 單次比對上限 $2
    'monthly_budget_usd': 1000.0   # 月預算 $1000
}

# 使用時檢查
def call_claude_with_limit(prompt):
    current_cost = get_today_cost()
    if current_cost > COST_LIMITS['daily_max_usd']:
        raise BudgetExceededError("Daily limit reached")
    
    # 預估這次呼叫成本
    estimated_cost = estimate_cost(prompt)
    if estimated_cost > COST_LIMITS['per_comparison_max_usd']:
        # 降級到較小模型
        model = "claude-sonnet-4-6"
    else:
        model = "claude-opus-4-20250514"
    
    response = client.messages.create(model=model, ...)
    
    # 記錄實際成本
    log_cost(response.usage)
    
    return response
```

---

## 📊 風險評估與對策

### 🔴 高風險

| 風險 | 可能性 | 影響 | 對策 |
|------|--------|------|------|
| **Claude API 成本超標** | 高 70% | 高 | 實測驗證、設定上限、降級策略 |
| **準確率未達 85%** | 中 40% | 高 | 建立測試集、持續調優、人工校正 |
| **團隊技能不足** | 中 50% | 高 | 提早培訓、引入顧問、簡化技術 |
| **時程延誤** | 高 60% | 中 | 簡化 MVP、敏捷開發、雙週檢討 |

### 🟡 中風險

| 風險 | 可能性 | 影響 | 對策 |
|------|--------|------|------|
| **Legal-BERT 繁中效果差** | 中 50% | 中 | 備案: 全用 Claude API |
| **PDF 格式多樣性** | 高 70% | 中 | 測試多種 PDF、OCR 備案 |
| **使用者接受度低** | 低 30% | 高 | Early adopters、UAT |

---

## ✅ 具體行動清單（本週）

### Day 1-2: MVP 驗證 ⏰ 2天
```bash
□ 建立 Python 專案 (venv + requirements.txt)
□ 實作 PDF 文字提取 (PyMuPDF)
□ 實作 difflib 基礎比對
□ 用 2 份真實合約測試
□ 輸出 Markdown 報告
```

### Day 3: Claude API 測試 ⏰ 半天
```bash
□ 申請 Claude API Key (如果沒有)
□ 寫測試腳本測量成本
□ 測試 5 個不同條款
□ 記錄 token 用量與成本
□ 決定: Opus vs Sonnet
```

### Day 4: 團隊確認 ⏰ 半天
```bash
□ 列出所需技能清單
□ 盤點現有團隊成員技能
□ 識別缺口（招聘 vs 培訓）
□ 確認每人投入度
□ 排定 Kick-off meeting
```

### Day 5: 規劃 Sprint 1 ⏰ 半天
```bash
□ 根據 MVP 驗證結果調整範疇
□ 拆分 User Stories
□ 估算每個 Story 的 Story Points
□ 排定 Sprint 1 (2週) Backlog
□ 設定 Definition of Done
```

---

## 🎯 成功指標（2週後檢驗點）

### 技術指標
- ✅ MVP 能處理真實合約（10-50 頁）
- ✅ 處理時間 < 2 分鐘
- ✅ 能識別至少 80% 的明顯變更
- ✅ Claude API 成本 < $1/合約

### 業務指標
- ✅ 至少 3 位 Stakeholders 認可價值
- ✅ 找到至少 1 個真實錯誤（人工沒發現的）
- ✅ 節省至少 50% 人工比對時間

### 團隊指標
- ✅ 團隊成員理解技術架構
- ✅ 開發流程順暢（無重大阻礙）
- ✅ 程式碼品質可接受（可維護）

**如果 2 週後這些指標都達成 → 繼續投入完整開發**  
**如果未達成 → Pivot 或調整方向**

---

## 🚀 推薦的啟動方式

### 選項 A: 保守漸進式 (推薦)
```
Week 1-2: MVP 驗證
Week 3-4: 加入 API + 基礎 UI
Week 5-6: 加入進階功能 (七階段)
Week 7-8: 加入 NER + 詐欺檢測
Week 9-10: 優化 + 測試
Week 11: 部署 + 上線
```
**優點**: 風險低、持續驗證、可隨時調整  
**缺點**: 較慢

### 選項 B: 激進快速式
```
Week 1: 完整文件處理 + 比對
Week 2-4: 所有 AI 功能
Week 5-6: 所有詐欺檢測
Week 7-8: API + UI
Week 9-11: 測試 + 部署
```
**優點**: 快速、功能完整  
**缺點**: 風險高、可能需要大量返工

### 選項 C: 混合式 (最佳)
```
Week 1-2: MVP 驗證 ← 快速驗證可行性
Week 3-6: 核心功能完整實作 ← 激進開發
Week 7-8: 使用者測試 ← 驗證價值
Week 9-11: 根據回饋優化 ← 保守調整
```
**優點**: 平衡風險與速度  
**缺點**: 需要靈活調整

---

## 📝 結論

### 👍 做得很好的地方
1. ✅ **研究充分** - 6 篇論文、產業最佳實踐
2. ✅ **文件完整** - 技術設計、API 規格、程式碼範例
3. ✅ **架構清晰** - 微服務、資料流程、部署方案
4. ✅ **風險意識** - 已識別主要風險

### ⚠️ 需要改進的地方
1. 🔴 **立即開始編碼** - 不要再規劃了，寫程式！
2. 🟡 **簡化 MVP** - 2 週驗證，不要 11 週大計劃
3. 🟡 **驗證假設** - Claude API 成本、準確率都需實測
4. 🟢 **確認團隊** - 人到位了嗎？技能夠嗎？

### 🎯 下一步（本週內完成）

```
Priority 0 (必須):
1. ✅ 建立 MVP Python 專案
2. ✅ 實測 Claude API 成本
3. ✅ 確認團隊組成

Priority 1 (重要):
4. ✅ 找 2-3 份真實合約測試
5. ✅ 排定 2 週 Sprint 計劃
6. ✅ Kick-off meeting

Priority 2 (可選):
7. □ 設定開發環境 (Docker)
8. □ 建立 Git repository
9. □ 設定 CI/CD
```

---

## 💬 最後的話

你已經有了**非常扎實的基礎**，文件品質很高。

但記住：
> **"The best plan is to start coding"** - 最好的計劃就是開始寫程式

現在是時候：
- ✅ 停止規劃
- ✅ 開始驗證
- ✅ 快速迭代

**2 週後見真章！** 🚀

---

**報告版本**: 1.0  
**下次審閱**: 2 週後 (2026-06-12)  
**審閱者**: Blue-AI Technical Advisor
