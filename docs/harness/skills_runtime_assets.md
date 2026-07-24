# Skills 雙重身分說明（動 `.claude/skills/` 前必讀）

> 決策：本專案採 **Q3 =「維持現狀 + 文件標註」**（不改格式、不搬移、不轉 `SKILL.md`），
> 並於 2026-07-03 **加上機制強制**（User 決策）：`guard_sensitive` hook 擋對 `.claude/skills/` 的
> mv/rm/改名，`Write(.claude/skills/*/**)` deny 擋轉目錄格式。故「不可搬移」不再只靠自覺。
> **2026-07-05 更新**：查證確認 `frontend-design.md` 是當時 5 個檔案裡唯一沒被任何 `src/` loader
> 引用的一個，經 User 同意後已改回一般 Claude Code skill 格式（`frontend-design/SKILL.md`）。
> **2026-07-16 更新**：逐段落精確 grep 全 `src/` 後發現，原本認定的「4 個 runtime 資產」裡，
> `contract-diff.md`、`report-writing.md` 其實**從未被任何 loader 引用**（2026-07-03 的核實只
> 抓到「有 4 處 loader 呼叫」，沒有逐一核對這 4 處呼叫具體讀的是哪幾個檔名，因此誤把這兩個也
> 算進保護範圍）。經 User 同意，這兩個檔案已封存至 `archive/skills_dead_assets/`，保護範圍收斂
> 為下方 **2 個**真正的 runtime 資產。本文是那道「告示牌」。任何模型想碰 `.claude/skills/` 下的
> 檔案，先讀完這裡。

---

## 1. 現況：2 個平面檔是 runtime 資產，1 個已是正式 Skill，2 個已封存

`.claude/skills/` 下現存 2 個**平面 `.md` 檔**（runtime 資產，非 Skill）：
`contract-risk-analysis.md`、`negotiation-strategy.md`。

- Claude Code **只載入 `<name>/SKILL.md` 目錄格式**的 skill。這 2 個是平面檔，**沒有被載入**。
- 因此 **`/contract-risk-analysis` 等 slash 指令實際上不存在**（已在 live session 的可用 skill 清單確認過）。
- ⛔ **不要嘗試呼叫這些不存在的指令**，也不要因為「找不到指令」而反覆重試——它們本來就不是給 Claude Code 當 skill 用的。

另外兩個已離開 `.claude/skills/`：
- `frontend-design/SKILL.md`（2026-07-05 已轉正）**是真正可用的 Claude Code skill**，可以正常用 Skill 工具呼叫。
- `contract-diff.md`、`report-writing.md`（2026-07-16 封存於 `archive/skills_dead_assets/`）**從未被任何 `src/` 程式碼讀取**，原因與歷史脈絡見下方第 4 節。這兩個檔案已不受本文任何保護規則限制，如需再利用內容可自由編輯/移動，不會影響任何 runtime 行為。

## 2. 真正的身分：`src/` 的 runtime prompt 資產（4 處 loader，已核實到段落層級）

這 2 個 `.md` 是**產品程式碼在執行時讀進去當 prompt 的資產**——但不是整份檔案，是用 `_load_skill_section(檔案, 段落標題)` 精確抓某個 `##` 段落。經逐段落 grep 核實（2026-07-16），有 4 處 loader、共讀取 5 個段落：

| 檔案:行 | 讀取的段落標題 | 讀取的檔案 |
|---------|---------------|----------|
| `src/services/contract/mas_service.py:39` | `MAS Agent A 知識庫（嚴格審查員）` | `contract-risk-analysis.md` |
| `src/services/contract/mas_service.py:43` | `MAS Agent B 知識庫（平衡審查員）` | `negotiation-strategy.md` |
| `src/services/contract/verifier.py:142` | `Verification Agent 知識庫（語意補漏審查員）` | `contract-risk-analysis.md` |
| `src/services/contract/negotiate_service.py:149` | `三層協商 Playbook（各風險類型標準立場）` | `negotiation-strategy.md` |
| `src/services/contract/llm_service.py:94` | `各風險類型的協商框架` | `negotiation-strategy.md` |

它們用 `Path(__file__).resolve().parents[3] / ".claude" / "skills" / "<平面檔名>.md"` 直接讀，再用段落標題文字精確比對切出該段內容。**檔名、位置、段落標題文字三者都是寫死的契約**——改動任一個都要同步確認 loader 端。

**重要**：這 2 個檔案裡，**只有上表列出的段落是活的**。檔案裡其餘的 `##` 段落（例如「任務輸入」「輸出格式」「不要做的事」）只是給人看的說明文字，**沒有任何程式碼讀取**，改了不會影響系統行為——這跟第 4 節「整份檔案沒被引用」是不同層次的問題，容易混淆，動這兩個檔案前務必分清楚。

## 3. 動它們的鐵律

1. **⛔ 絕不**把下方 2 個檔案改成 `xxx/SKILL.md` 目錄格式——上表 4 處 loader 會立刻找不到檔案，合約比對／協商／風險服務全掛。
2. **⛔ 絕不**搬移、改名這 2 個檔（`contract-risk-analysis.md`、`negotiation-strategy.md`）。保護機制（`guard_sensitive.py` 的 `_PROTECTED_SKILL_FILES`，2026-07-16 已收斂為精確列出這 2 個檔名）。
3. ✏️ **可以**編輯這 2 個檔案的**內容**（那是 prompt 文本，本來就會迭代），包含上表列出的活段落、也包含其餘純文件段落。但改完必須實跑驗證 loader 仍讀得到、且內容非空：
   ```bash
   python3 -c "
   from src.services.contract import negotiate_service, mas_service, llm_service, verifier
   print('mas_service._SKILL_AGENT_A 長度:', len(mas_service._SKILL_AGENT_A))
   print('mas_service._SKILL_AGENT_B 長度:', len(mas_service._SKILL_AGENT_B))
   print('verifier._SKILL_VERIFICATION_AGENT 長度:', len(verifier._SKILL_VERIFICATION_AGENT))
   print('negotiate_service._SKILL_PLAYBOOK_TEXT 長度:', len(negotiate_service._SKILL_PLAYBOOK_TEXT))
   print('llm_service._SKILL_NEGOTIATION_FRAMEWORK 長度:', len(llm_service._SKILL_NEGOTIATION_FRAMEWORK))
   "
   ```
4. 若**真的**要把這 2 個也升級成正式 Claude Code skill：必須**同步**修改上述 4 處 `_SKILLS_DIR` 路徑邏輯，改完實跑驗證＋既有測試，通過才算數。這屬於「須先徵得 User 同意」的動作（見 [F_reflection_protocol.md](F_reflection_protocol.md)）——`frontend-design.md` 的轉正就是照這個流程走的先例：先 grep 核實無 loader 引用、跟 User 確認、備份 settings.json + hook、精確收斂保護範圍（不是整批放行）、搬移後實跑驗證 4 個 loader 仍正常。

## 4. 已封存的 2 個檔案：為什麼從未被使用（歷史脈絡，供後續參考）

- **`contract-diff.md`**：最初版本（`c67edd3` 初始 commit）就帶著 Claude Code skill 的 YAML frontmatter（`name:`/`description:`）格式，設計意圖是給人在 Claude Code 裡打 `/contract-diff` 叫出系統總覽，**從一開始就不是設計給 `_load_skill_section()` 讀的東西**。因為是平面檔案格式（不是 `<name>/SKILL.md` 目錄），從未被 Claude Code 註冊成可用指令。這個檔案被 5 次 commit 持續維護更新（最近一次是 Layer 4→Layer 3 改名），代表有人一直把它當「活的系統總覽文件」在維護，只是它從未真正「被使用」在它原本設計的用途上。
- **`report-writing.md`**：描述自己是「報告產出 Sub-Agent」，跟 `contract-risk-analysis.md`（風險分析 Sub-Agent）、`negotiation-strategy.md`（協商策略 Sub-Agent）在同一次 commit（`8650cf0`，Phase 1）一起建立，屬於最初設計的「Sub-Agent 接力鏈」架構願景的一環。但實作時，「報告產出」這一棒改用純 Python 字串組裝（`report_generator.py`，見 `docs/architecture/技術棧.md`「死資產」章節），沒有真的做成 LLM 呼叫——這是一個設計轉向，之後沒有人回頭清理這份被放棄的 Sub-Agent 規格。**2026-07-09 實測驗證過**：真的把這份檔案接上 LLM 呼叫測試，結果會算錯總數、捏造不存在的日期，證實當初改用純 Python 組裝是正確決定。

---
*核實者：Opus 4.8｜2026-07-03，grep 佐證見 [A_diagnosis.md](A_diagnosis.md) 痛點 3｜frontend-design 轉正：Sonnet 5，2026-07-05｜段落層級核實 + contract-diff/report-writing 封存：Sonnet 5，2026-07-16。*
