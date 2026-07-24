# CLAUDE.md — Blue-AI 合約比對助理｜路由中心

> 本檔每個 session 全量載入，故**只放「路由 + 必須永遠在場的硬規則」**。
> 細節一律外連。**不要在這裡堆長內容**（會每 session 漏 token）。新增細節請寫進對應檔案並在下方路由表加一行。
> 版本 2.0（2026-07-03 由 Opus 4.8 重寫為路由中心）｜舊版備份見 `CLAUDE.md.bak`

---

## 0. 這個專案是什麼（一句話）

AI 驅動的**合約文件比對助理**：比對合約版本差異、標註風險條款、產出比對報告與協商對策。企業競賽專案（截止 2026 年 8 月初）。技術：Python、Claude API、Azure Document Intelligence、前端 `frontend/demo.html`。

---

## 1. ⛔ 硬規則（違反會出事，永遠遵守）

1. **機密不可讀**：`.env`（真 API key）與 `nda_contract/`、`sla_contract/`（真實/測試合約）**受 deny + hook 雙重保護**。列舉/搜尋（`ls`/`grep`/`git`）放行；但**讀取內容**（`cat`/`head`/`python 開檔`）或用 Read/Edit/Write 工具會被擋。若 Bash 被 `guard_sensitive` hook 擋下（exit 2），那是**刻意的**，**不要重試**，改用不讀取該內容的做法或請 User 處理。（`pic_contract/` 2026-07-16 經 User 明確同意後已解除保護，可正常讀取，唯用 Bash 指令**同時**出現萬用字元 + 讀取類動詞時仍會被廣泛的 glob 保護攔截，改用 Read 工具或不含萬用字元的指令即可。）詳見 [docs/harness/A_diagnosis.md](docs/harness/A_diagnosis.md)。
2. **不要搬移/改名 `.claude/skills/*.md`**：`contract-risk-analysis.md`、`negotiation-strategy.md` 這 2 個平面檔**不是可用的 Claude Code skill**（`/contract-risk-analysis` 等指令不存在），它們是 `src/` 在 runtime 讀取的 **prompt 資產**（精確讀取特定 `##` 段落，非整份檔案）。**編輯內容可以**；但**搬移、改名、或轉成 `<name>/SKILL.md` 目錄格式會弄壞 4 處產品 loader**——此限制已由 hook + `Write(.claude/skills/*/**)` deny **機制強制**（不是靠自覺）。（`contract-diff.md`、`report-writing.md` 2026-07-16 已核實從未被讀取，封存至 `archive/skills_dead_assets/`；`frontend-design.md` 2026-07-05 已轉正為正式 Claude Code skill，兩者皆不受此規則限制。）**動它前必讀** [docs/harness/skills_runtime_assets.md](docs/harness/skills_runtime_assets.md)。
3. **模型不釘死**：全域已移除 `model` 欄位，每個 session 自行用 `/model` 選模型。本專案 `.claude/settings.json` 有**自主式 allowlist**（常用開發命令放行，`git push`/`rm`/`pip install`/`curl` 仍 gated）。派工給 subagent 時依 [docs/harness/C_model_dispatch.md](docs/harness/C_model_dispatch.md) 決定 haiku/sonnet/opus。
4. **正確模型 ID**（勿用舊名）：複雜分析 `claude-opus-4-8` 或 `claude-sonnet-5`；簡單任務 `claude-haiku-4-5`。（舊版寫的 `claude-sonnet-4-6`/`claude-opus-4-7` 已作廢。）
5. **改既有檔前先備份 `.bak`**；敏感操作、外送、刪除前先確認。

---

## 2. 📍 檔案路由表（要找東西看這裡）

### 工作流制度（Harness）— 弱模型的作業依據

| 需求                         | 去哪                                                                          |
| ---------------------------- | ----------------------------------------------------------------------------- |
| 整套制度總覽與啟動順序       | [docs/harness/README.md](docs/harness/README.md)                               |
| 為什麼有這些規則（診斷）     | [docs/harness/A_diagnosis.md](docs/harness/A_diagnosis.md)                     |
| 派工／選模型／升降級         | [docs/harness/C_model_dispatch.md](docs/harness/C_model_dispatch.md)           |
| 判斷「該停/該交付/該問人」   | [docs/harness/D_judgment_matrix.md](docs/harness/D_judgment_matrix.md)         |
| 派工 Prompt 模板（複製即用） | [docs/harness/E_dispatch_templates.md](docs/harness/E_dispatch_templates.md)   |
| 踩坑後如何更新這套制度       | [docs/harness/F_reflection_protocol.md](docs/harness/F_reflection_protocol.md) |
| 接手新 session 先讀          | [docs/harness/G_handover.md](docs/harness/G_handover.md)                       |

### 專案脈絡與計畫

| 需求                                                     | 去哪                                    |
| -------------------------------------------------------- | --------------------------------------- |
| 冷啟動專案脈絡（權威）                                   | [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) |
| 簡報內容／里程碑／Q&A 話術（給評審看的）                 | [PROJECT_PLAN.md](PROJECT_PLAN.md)       |
| **待辦清單（還沒做完的事，滾動更新，開發前先看）** | [next_step_plan.md](next_step_plan.md)   |
| 對外專案簡介                                             | [README.md](README.md)                   |
| 競賽原始題目（參考）                                     | 專案.md                                 |
| 歷史 session log／舊計畫                                 | `archive/`（過時，僅考古用）          |

### 程式碼與規格

| 需求                | 去哪                       |
| ------------------- | -------------------------- |
| 技術規格            | `docs/specs/`            |
| 架構文件            | `docs/architecture/`     |
| 合約比對服務        | `src/services/contract/` |
| Claude / Azure 整合 | `src/integrations/`      |
| 前端 demo           | `frontend/demo.html`     |

---

## 3. 開發規範（精要；細則見各檔）

- **Python**：Black（line-length=100）、PEP 8、必加 type hints、Google-style docstring。
- **TypeScript/React**：Prettier、ESLint、Function Component + Hooks、禁 `any`。
- **Git**：分支 `feature/*`；commit 格式 `<type>(<scope>): <subject>`（type：feat/fix/docs/style/refactor/test/chore）。commit/push 只在 User 要求時做。
- **API**：RESTful、`/api/v1/...`、統一回應格式（`success`/`data`/`error`/`timestamp`）。
- **安全**：金鑰只走環境變數/Key Vault，永不進 code、git、log。

> ⚠️ 舊版 CLAUDE.md 的「目錄結構規範」與現實不符（實際無 `tests/`、`deploy/`、`scripts/`；`frontend/` 只有 `demo.html`）。以實際檔案樹為準，勿據舊圖建目錄。

---

## 4. 給弱模型的一句話

不確定就查；查不到就標註「未驗證」；**絕不編造**。判斷卡住看 [D_judgment_matrix.md](docs/harness/D_judgment_matrix.md)；要派工看 [C](docs/harness/C_model_dispatch.md)+[E](docs/harness/E_dispatch_templates.md)。
