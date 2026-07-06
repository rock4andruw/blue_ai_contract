# 報告內問答（Report Q&A）設計規格

**文件版本**：1.0
**日期**：2026-07-06
**狀態**：✅ 已實作並測試（`POST /api/v1/contracts/ask`）
**目的**：讓使用者針對已產出的比對報告提問，只根據報告內容回答，查無資訊時誠實告知，不編造。

---

## 一、這是什麼

一個問答端點，接在合約比對報告產出**之後**使用。使用者輸入問題（例如「為什麼這條被標高風險？」），系統把當次報告的重點變更（`key_changes`）連同問題一起送給 LLM，LLM 只能根據這些內容回答。

**不是**開放式聊天助理——LLM 不能引用訓練知識、不能推測、不能回答報告以外的事。這跟 Layer 3（法律依據檢索）的「查不到就留空」是同一套誠實揭露原則。

---

## 二、System Prompt 現況

程式碼位置：`src/services/contract/llm_service.py`，常數 `ASK_SYSTEM_PROMPT`（第 463 行附近）。

```text
你是合約審查報告的問答助理。

你只能根據下方提供的報告內容回答問題。報告內容沒有提到的資訊，一律回答「這份報告沒有相關資訊」，不可推測、不可引用訓練知識、不可編造。

使用繁體中文，簡潔直接回答，不要重複整段報告內容。
```

實際送給 LLM 的完整 prompt，是這段 System Prompt + 使用者問題 + 報告內容組成的 context（由 `_build_report_context()` 組裝，把每個重點變更的風險等級、白話說明、商業影響、法律依據、**法條原文、相似先例（含相似度）**、雙重驗證意見整理成文字區塊）。

> **2026-07-06 修正**：`_build_report_context()` 原本只讀 `legal_basis`（LLM 統整過的一句話），沒有讀 `legal_citation_raw`（MCP 查到的法條原文）跟 `precedent_raw`（先例向量檢索的原始文字＋相似度）——這兩個欄位其實已經存在於同一批 `key_changes` 資料裡，只是沒被組進 context，導致問「法條完整原文是什麼」這類問題答不出來。已修正並驗證（fail-then-pass）：修正前 `grounded: false`（「這份報告沒有相關資訊」），修正後正確引用完整法條原文與先例相似度百分比，`grounded: true`。

---

## 三、為什麼沒有像其他 4 個 LLM 角色一樣外部化成 `.claude/skills/*.md`

專案裡另外 4 個 LLM 角色（Verification Agent、MAS Agent A/B、協商摘要框架、三層 Playbook）的知識庫都外部化了，因為那些內容是**法律/商業判斷**（風險評估標準、協商立場、業界慣例），法務同仁會想調整。

這個 Ask 功能的 System Prompt 幾乎全部是**安全防護規則**（只能根據提供內容回答、查無資訊要誠實說、用繁中簡答）——沒有實質的「領域判斷」內容需要法務編輯，硬做成 skill.md 外部化沒有對應的價值，所以維持寫死在程式碼裡，用這份文件記錄內容供理解與維護。

---

## 四、如何維護（沒有自動載入機制，改了要手動同步）

1. 直接編輯 `src/services/contract/llm_service.py` 裡的 `ASK_SYSTEM_PROMPT` 常數
2. **改完務必同步更新本文件第二節**，保持文件內容跟程式碼一致——這份文件不是 runtime 讀取的來源，只是人工參考用的說明文件，兩邊會各自獨立，不會自動同步
3. 改完建議跑一次回歸測試（至少 3 題）：
   - 問報告有涵蓋的內容（例如「為什麼這條高風險？」）→ 應正確引用報告內容，`grounded: true`
   - 問報告有法律依據的條款 → 應正確引用 `legal_basis`
   - 問報告沒涵蓋的內容 → 應誠實回答「這份報告沒有相關資訊」，`grounded: false`，**不可編造**
4. 測試方式參考 `docs/specs/verification_agent_spec.md` 或直接呼叫 `POST /api/v1/contracts/ask` 端點驗證

---

## 五、相關檔案

| 內容 | 位置 |
| --- | --- |
| System Prompt + 問答邏輯 | `src/services/contract/llm_service.py`（`ASK_SYSTEM_PROMPT`、`answer_report_question()`） |
| API 端點 | `src/api/contracts.py`（`POST /ask`） |
| 前端 UI | `frontend/demo.html`（「報告問答」卡片，Q/A 批註樣式） |
