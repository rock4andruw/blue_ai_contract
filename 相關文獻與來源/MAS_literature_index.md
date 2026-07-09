# MAS 雙 Agent 設計相關文獻

收錄日期：2026-06-26  
用途：支撐 Blue-AI 合約比對助理 MAS Phase 1.5 架構設計決策

---

## 核心議題

我們的 MAS 設計使用兩個相同模型（Gemini）搭配不同 Persona，以下文獻指出此設計的潛在問題與改善方向。

---

## 文獻清單

### 1. Can LLM Agents Really Debate?
**檔案**：`can_llm_agents_really_debate_2511.07784.pdf`  
**來源**：https://arxiv.org/abs/2511.07784  

**核心發現**：
- 多 Agent 辯論在邏輯推理任務上不一定優於單一 Agent
- 同質 Agent（相同模型）容易形成 Echo Chamber，強化錯誤而非修正
- 真正有效的辯論需要 Agent 具備不同的推理起點

**對我們的影響**：Agent A/B 使用相同模型，底層偏見相同，「辯論」結果可能只是 Persona 強度差異在驅動

---

### 2. Talk Isn't Always Cheap: Failure Modes in Multi-Agent Debate
**檔案**：`talk_isnt_cheap_failure_modes_debate_2509.05396.pdf`  
**來源**：https://arxiv.org/abs/2509.05396  

**核心發現**：
- 多 Agent 辯論的常見失敗模式：過早收斂、Sycophancy、少數服從多數
- 若多數 Agent 持同一立場，少數 Agent 傾向放棄正確答案去從眾
- 多樣性（Diversity）是有效辯論的必要條件，不是充分條件

**對我們的影響**：需要確保 Persona 差異夠大，避免 Agent B 對強烈的 Agent A 立場直接從眾

---

### 3. Multi-LLM Debate: Framework, Principals, and Interventions
**檔案**：`multi_llm_debate_framework_openreview.pdf`  
**來源**：https://openreview.net/forum?id=sy7eSEXdPC  

**核心發現**：
- 提出系統性的多 LLM 辯論框架
- Echo Chamber 的結構性解法：使用異質模型（Heterogeneous Agents）
- Blind Evaluation（不告知其他 Agent 的答案）能提升獨立性

**對我們的影響**：Phase 2 使用 Gemini + Claude 的設計方向有文獻支撐

---

### 4. When Truth Is Overridden: Sycophancy in LLMs
**檔案**：`sycophancy_truth_overridden_2508.02087.pdf`  
**來源**：https://arxiv.org/abs/2508.02087  

**核心發現**：
- Sycophancy 的來源在模型內部——即使訓練時沒有明確強化，LLM 天生傾向迎合
- 當 Prompt 暗示「正確答案」時，模型準確率下降
- 與錨定效應（Anchoring Bias）直接相關

**對我們的影響**：我們的 Prompt 包含「規則引擎判定此條款為 high 風險」→ 告知答案 → 觸發 Sycophancy。Agent 判斷結果部分受錨定而非獨立推理。

---

### 5. Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge
**檔案**：`justice_or_prejudice_llm_judge_bias_2410.02736.pdf`  
**來源**：https://arxiv.org/abs/2410.02736  

**核心發現**：
- LLM-as-Judge 存在多種系統性偏見：Position Bias、Verbosity Bias、Self-enhancement Bias
- 同模型系列的 Agent 互評時傾向給出更高分（Self-enhancement）
- 建議：使用多個不同模型的 Judge 取平均，比單一 Judge 更可靠

**對我們的影響**：A/B 使用相同模型系列，Self-enhancement Bias 可能使兩者的推理方式過度相似

---

### 6. Judging with Many Minds: Bias in Multi-Agent LLM-as-Judge
**檔案**：`judging_many_minds_multi_agent_2505.19477.pdf`  
**來源**：https://arxiv.org/abs/2505.19477  

**核心發現**：
- 增加 Agent 數量不一定減少偏見，有時會放大偏見
- 多 Agent 系統需要系統層級（system-level）的偏見評估，而非只看個別 Agent
- 結構性多樣性（不同模型、不同 context）比數量更重要

**對我們的影響**：加第三個 Agent 不一定有幫助，解決問題的關鍵是異質性

---

## 對 MAS 設計的整體建議（文獻依據）

| 問題 | 文獻來源 | 建議改善 |
| --- | --- | --- |
| Echo Chamber（同質模型） | 論文 1、3 | Phase 2：Gemini + Claude 異質設計 |
| Sycophancy（Prompt 錨定） | 論文 4 | 移除 Prompt 中的 Rule Engine 答案，讓 Agent 盲評 |
| Self-enhancement Bias | 論文 5 | Judge 矩陣不依賴 Agent 互評，只做獨立判斷 |
| 從眾效應 | 論文 2 | 確保 Persona 差異夠大，避免 Agent B 對 Agent A 從眾 |

---

## Phase 1.5 現狀的誠實定位

> 我們的 MAS 是「對立 Persona 驅動的雙視角評估」，而非嚴格意義的「獨立 Agent 驗證」。  
> 相同模型 + Prompt 錨定使結果受限，但 Persona 差異仍能提供有意義的觀點分歧。  
> Phase 2 引入異質模型後，才能達到真正的獨立交叉驗證。
