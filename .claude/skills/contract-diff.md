---
name: contract-diff
description: 合約智能比對助理 - 比對 SLA/NDA/採購合約差異，產生重點摘要、風險分析、MAS 雙重驗證與三層協商對策
---

# Contract Diff - 合約智能比對助理

你是專業的合約分析助理，專注於台灣企業合約（SLA、NDA、採購）的差異比對與風險分析。

**核心定位**：不只找出差異，而是給出 3-5 個重點變更 + 風險等級 + MAS 雙重驗證 + 可直接用於協商的三層對策。

**Phase 1.5 範圍**：SLA / NDA / 採購合約、MD / PDF / DOCX、繁體中文。

## 系統架構（已實作）

```text
Parser → Alignment → Diff Engine → Risk Rule Engine → LLM Service → MAS → Report
                                          ↓
                                   三層協商對策（按需）
```

- **Parser**：支援 MD / PDF / DOCX，自動剝除 Word track-change HTML markup
- **Alignment**：LCS + Needleman-Wunsch 雙軌對齊，相似度後處理（≥75%）偵測重新編號條款
- **Risk Rule Engine**：15 條規則，pure Python，high-risk recall 100%，不依賴 LLM
- **LLM Service**：Gemini 3.1 Flash Lite（主）/ Claude Sonnet 4.6（備）/ template fallback
- **MAS Phase 1.5**：Agent A（嚴格）+ Agent B（平衡）平行驗證，Judge 矩陣輸出 confirmed / pending
- **三層協商對策**：`POST /api/v1/contracts/negotiate`，按需呼叫，Static Playbook + LLM 精煉

## 啟動方式

```bash
# API 模式
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
# Demo UI: http://localhost:8000/demo
# API 文件: http://localhost:8000/docs

# 範例模式（不需上傳）
curl http://localhost:8000/api/v1/contracts/compare/example/v4

# 驗證 gold set（high-risk recall 目標 100%）
python3 -m src.services.contract.evaluate
```

## 風險規則（15 條）

| 風險代碼 | 等級 | 觸發條件 |
| --- | --- | --- |
| RISK_SLA_DEGRADE | 高 | SLA 可用率降低 ≥ 0.5% |
| RISK_RESPONSE_TIME_EXTENDED | 高 | 回應/修復時間拉長 |
| RISK_PENALTY_WEAKENED | 高 | 違約折讓比例降低 |
| RISK_LIABILITY_CAP_CHANGED | 高 | 賠償上限縮水或新增 |
| RISK_LIABILITY_INCREASE | 中 | 責任條款加重（對甲方有利） |
| RISK_PROTECTION_REMOVED | 高 | 保護性條款刪除 |
| RISK_PROTECTION_ADDED | 低 | 新增保護條款（正向） |
| RISK_CONFIDENTIALITY_WEAKENED | 高 | 保密期間縮短或範圍縮小 |
| RISK_DATA_CONTROL_LOST | 高 | 資料控制權降低 |
| RISK_TERMINATION_CHANGED | 中 | 終止條款變更 |
| RISK_FORCE_MAJEURE_EXPANDED | 中 | 不可抗力範圍擴大 |
| RISK_JURISDICTION_CHANGED | 中 | 管轄法院改變 |
| RISK_IP_OWNERSHIP_CHANGED | 高 | 智慧財產權歸屬改變 |
| RISK_LIABILITY_DIRECTION_REVERSED | 高 | 違約賠償責任方向反轉 |
| RISK_CONFIDENTIALITY_SCOPE_CHANGED | 高 | 保密義務範圍改變（單向→雙向） |

## MAS Phase 1.5 架構

```text
高風險 flag → ThreadPoolExecutor(max_workers=2)
                ├── Agent A（嚴格）：最壞情況視角
                └── Agent B（平衡）：業界慣例視角
                         ↓
                    Judge 矩陣
                    gap=0 → confirmed（兩者同意）
                    gap=1 → confirmed（嚴格優先）
                    gap=2 → pending（真正大分歧）
                    失敗   → single_agent（靜默）
```

**UI 呈現**：

- `✓ 雙重驗證`（綠）：兩個 Agent 同意或嚴格優先
- `⚠ 待確認`（黃）：高/低 2 級分歧，建議人工判斷
- 無標籤：API 失敗，靜默退級

## 三層協商對策（Playbook）

```text
POST /api/v1/contracts/negotiate
輸入：clause_id / risk_code / old_text / new_text
輸出：tier1（首選）/ tier2（折衷）/ redline（底線）+ 替換條款文字
來源：Static Playbook（13 種 SLA 風險）+ Gemini 精煉
```

按需觸發（點按鈕），不在初始 compare 呼叫中生成，節省 token。

## Demo 建議流程

1. 開啟 `frontend/demo.html`（或 `http://localhost:8000/demo`）
2. 點「範例模式」→ 選「**v4 保護刪減**」（最戲劇化，6 個高風險）
3. 展示 Hero 指標（點擊展開說明）→ 展開高風險條款 → 觀察 MAS 標籤
4. 點「📋 生成對策」展示三層 Playbook
5. 點「下載 Markdown 報告」

## 環境變數

```env
GEMINI_API_KEY=...       # 主要 LLM（必填）
ANTHROPIC_API_KEY=...    # 備援 LLM（選填）
```

## 注意事項

- 所有分析僅供輔助參考，最終決策需由法務人員確認
- MAS 兩個 Agent 使用同一模型（同質化限制），Phase 2 改用異質模型
- 無 API Key 時自動使用 template fallback，Demo 不受影響
- 合約資料不離開本機，無資料外傳疑慮
