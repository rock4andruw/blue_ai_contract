# 工程審查回應：已知限制與設計取捨說明

**文件性質**：回應外部工程師程式碼審查所提疑問  
**日期**：2026-06-27  
**版本**：Phase 1.5（MAS 雙重驗證已完成）

---

## 總體立場

以下四類問題均已在設計階段評估，屬於**刻意的設計取捨（Intentional Trade-off）**，而非疏漏。每一項均有對應的 Phase 2 / Phase 3 改善計畫。競賽 Demo 範圍內，這些限制不會影響功能展示與驗證數字。

---

## 1. 解析與對齊層（Parser & Aligner）

### 1-A 演算法效能（O(N×M) 複雜度）

**疑問**：LCS + Needleman-Wunsch 在大型合約（50 頁以上 MSA）會遭遇 CPU 瓶頸。

**回應**：

Phase 1 的設計範圍明確限定為 **≤ 20 頁的文字型合約**（NDA、SLA），在此規模下：
- 條款數量約 15–40 條
- 整體流程（含 LLM 呼叫）實測 26 秒內完成
- Needleman-Wunsch 在條款粒度（非字元粒度）運算，矩陣規模 ≤ 40×40，不構成瓶頸

若日後需支援 50 頁以上 MSA，規劃在 Phase 2 評估以下替代方案：
- 條款分塊（Chunking）後分批對齊，降低單次矩陣規模
- 以向量相似度（pgvector cosine similarity）取代 DP，O(N log N) 近似對齊

### 1-B 表格與非結構化排版

**疑問**：複雜表格（Nested Tables）被線性攤平後，Aligner 無法正確對齊欄位。

**回應**：

Phase 1 有意不支援表格型合約，原因：
1. 表格結構因工具而異（Word、PDF、掃描版），解析策略差異大
2. 競賽測試樣本均為條款式文字合約（SLA、NDA）

Phase 2 規劃引入 **Azure Document Intelligence** 進行結構化表格提取，取得欄位座標後再對齊。

---

## 2. 風險規則引擎（Risk Rule Engine）

### 2-A Regex 語意彈性的剛性限制

**疑問**：合約自然語言表達靈活，Regex 規則難以覆蓋全部寫法，可能導致 High-risk recall 在真實文本中下降。

**回應**：

這是 Rule Engine 架構的**核心取捨**，屬於刻意選擇：

| | Rule Engine（現行） | 純 LLM 判定 |
| --- | --- | --- |
| High-risk recall | **100%（可驗證）** | 不穩定，無法保證 |
| 語意彈性 | 弱（Regex 剛性） | 強 |
| 可解釋性 | 每條有 trigger_reason | 黑箱 |
| 幻覺風險 | 無 | 有 |

設計原則：**高風險不漏判比語意彈性更重要**。法務環境中，漏判一條真正有風險的條款所造成的損失，遠大於多判一條無風險條款的困擾。

**已驗證範圍**：gold set 38 筆標註（涵蓋 v1 vs v2-v5），High-risk recall = 100%，無漏判。

**已知邊界**：非常規中文表達（如「千分之九百九十五」）目前可能未覆蓋。這是 Phase 2 引入 LLM 輔助規則生成後要解決的問題，屆時流程如下：
```
新合約樣本 + 人工標注 → LLM 分析風險模式 → 候選規則草稿 → 工程師審核後加入 engine
```

---

## 3. 多代理人系統（MAS）

### 3-A 同質模型的 Echo Chamber 與 Sycophancy

**疑問**：Agent A 與 Agent B 使用相同底層模型（Gemini），在模糊地帶可能產生相同偏見。

**回應**：

Phase 1.5 的 MAS 設計**誠實定位**為「雙視角評估」，非「嚴格獨立驗證」。文獻已明確引用：

- *When Truth Is Overridden (2025)*：相同模型看到對方答案會觸發 Sycophancy → 因此採用**盲評**（Agent A/B 互不知對方結果）
- *Judging with Many Minds (2025)*：Multi-Agent Debate 可能放大偏見；Meta-Judge 獨立評估再彙整更穩定 → 因此採用 **Judge 矩陣**而非 debate

兩個 Agent 的知識庫完全不同：
- Agent A：最壞情況場景表（極端損失案例）
- Agent B：台灣 SaaS 業界慣例標準

即便底層相同，知識庫差異仍能產生有意義的觀點分歧——Demo 的 v3 pending 案例（67% pending 率）是實際驗證。

**Phase 2 改善**：引入 **Gemini（Agent A）+ Claude（Agent B）異質模型設計**，從根本消除 Echo Chamber。

### 3-B Judge 矩陣嚴格偏差導致虛警噪聲

**疑問**：gap=1 時一律嚴格 Agent 優先（判 High），可能導致大量 False Alarm，造成警示疲勞。

**回應**：

「嚴格優先」是有意設計，理由同 2-A——在合約審查的風險情境中，recall 優先於 precision。

實測數字：
- v4（明確高風險）：6 confirmed，0 pending，0 false alarm
- v3（條款有爭議）：1 confirmed，2 pending，0 false alarm

目前 gold set 上無虛警問題。同意在真實複雜合約上可能需要調整閾值；日後可針對特定 risk_code 設定個別的 gap 容忍度（例如某些低敏感度條款改為 gap=1 時平均，而非嚴格優先）。

---

## 4. 無狀態架構（Stateless API）

### 4-A 缺乏談判歷史脈絡

**疑問**：多輪談判中，系統無法追蹤「讓步軌跡」，使用者每輪都要重看相同風險提示。

**回應**：

競賽前**刻意不引入資料持久化**，理由：
1. 避免引入 DB / Session 管理增加維運複雜度
2. 競賽 Demo 情境為單輪比對（上傳兩份合約 → 得到結果），不需要歷史

談判歷史追蹤是 **Phase 3 功能**（History Agent），規劃架構：
```
上傳 v3 → 系統標記與 v2 的 delta（此輪新增了哪些讓步）
         → 追蹤哪些條款曾妥協、哪些被對方撤回
```

---

## 總結

| 疑問 | 性質 | 競賽前修？ | Phase |
| --- | --- | --- | --- |
| 演算法 O(N×M) 效能 | 刻意範圍限縮 | ❌ | Phase 2 |
| 表格解析脆弱 | 刻意不支援 | ❌ | Phase 2 |
| Regex 語意彈性 | 核心取捨（recall 優先） | ❌ | Phase 2（LLM 輔助生成） |
| 同質模型 Echo Chamber | 已知限制 + 文獻誠實揭露 | ❌ | Phase 2（異質模型） |
| Judge 嚴格偏差噪聲 | gold set 上無問題，真實合約待觀察 | ⚠️ 視情況 | 可針對性調整 |
| 無狀態 / 談判歷史 | 刻意不做持久化 | ❌ | Phase 3 |

以上所有限制均已在內部文件（`next_step_plan.md`、`docs/專案藍圖摘要.md`）中記錄，並對應到 Phase 2/3 的改善計畫。

---

*文件版本：1.0 ｜ 2026-06-27 ｜ Blue-AI Team*
