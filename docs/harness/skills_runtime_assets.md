# Skills 雙重身分說明（動 `.claude/skills/` 前必讀）

> 決策：本專案採 **Q3 =「維持現狀 + 文件標註」**（不改格式、不搬移、不轉 `SKILL.md`），
> 並於 2026-07-03 **加上機制強制**（User 決策）：`guard_sensitive` hook 擋對 `.claude/skills/` 的
> mv/rm/改名，`Write(.claude/skills/*/**)` deny 擋轉目錄格式。故「不可搬移」不再只靠自覺。
> **2026-07-05 更新**：查證確認 `frontend-design.md` 是 5 個檔案裡唯一沒被任何 `src/` loader
> 引用的一個，經 User 同意後已改回一般 Claude Code skill 格式（`frontend-design/SKILL.md`），
> 現在是真正可用的 skill。保護規則同步收斂為**只針對下方 4 個真正的 runtime 資產**，不再是整批
> `.claude/skills/*` 通用規則。本文是那道「告示牌」。任何模型想碰 `.claude/skills/` 下的檔案，
> 先讀完這裡。

---

## 1. 現況：4 個平面檔是 runtime 資產，1 個已是正式 Skill

`.claude/skills/` 下有 4 個**平面 `.md` 檔**（runtime 資產，非 Skill）：
`contract-diff.md`、`contract-risk-analysis.md`、`negotiation-strategy.md`、`report-writing.md`。

- Claude Code **只載入 `<name>/SKILL.md` 目錄格式**的 skill。這 4 個是平面檔，**沒有被載入**。
- 因此 **`/contract-diff`、`/contract-risk-analysis` 等 slash 指令實際上不存在**（已在 live session 的可用 skill 清單確認過）。
- ⛔ **不要嘗試呼叫這些不存在的指令**，也不要因為「找不到指令」而反覆重試——它們本來就不是給 Claude Code 當 skill 用的。

另外 `frontend-design/SKILL.md`（2026-07-05 已轉正）**是真正可用的 Claude Code skill**，可以正常用 Skill 工具呼叫，不受本文其餘規則限制。

## 2. 真正的身分：`src/` 的 runtime prompt 資產（4 處 loader，已核實）

這些 `.md` 是**產品程式碼在執行時讀進去當 prompt 的資產**。經 `grep` 核實（2026-07-03），有 4 處 loader：

| 檔案:行 | `_SKILLS_DIR` 定義 | 讀取的 skill 檔 |
|---------|-------------------|----------------|
| `src/services/contract/mas_service.py:35` | `parents[3] / ".claude" / "skills"` | `contract-risk-analysis.md`、`negotiation-strategy.md` |
| `src/services/contract/negotiate_service.py:146` | 同上 | `negotiation-strategy.md` |
| `src/services/contract/llm_service.py:91` | 同上 | `negotiation-strategy.md` |
| `src/services/contract/verifier.py:139` | 同上 | `contract-risk-analysis.md` |

它們用 `Path(__file__).resolve().parents[3] / ".claude" / "skills" / "<平面檔名>.md"` 直接讀。**檔名與位置是寫死的契約。**

## 3. 動它們的鐵律

1. **⛔ 絕不**把下方 4 個檔案改成 `xxx/SKILL.md` 目錄格式——那 4 處 loader 會立刻找不到檔案，合約比對／協商／風險服務全掛。
2. **⛔ 絕不**搬移、改名這 4 個檔（`contract-diff.md`、`contract-risk-analysis.md`、`negotiation-strategy.md`、`report-writing.md`）。保護機制（settings.json deny + guard_sensitive hook）2026-07-05 已改成**精確列出這 4 個檔名**，不再是整個 `.claude/skills/*` 的通用規則——`frontend-design/` 不在保護範圍內，可自由編輯移動。
3. ✏️ **可以**編輯這 4 個檔案的**內容**（那是 prompt 文本，本來就會迭代）。但改完必須實跑驗證 loader 仍讀得到：
   ```bash
   python3 -c "from src.services.contract import negotiate_service, mas_service, llm_service, verifier; print('4 loaders OK')"
   ```
4. 若**真的**要把這 4 個也升級成正式 Claude Code skill：必須**同步**修改上述 4 處 `_SKILLS_DIR` 路徑邏輯，改完實跑驗證＋既有測試，通過才算數。這屬於「須先徵得 User 同意」的動作（見 [F_reflection_protocol.md](F_reflection_protocol.md)）——`frontend-design.md` 的轉正就是照這個流程走的先例：先 grep 核實無 loader 引用、跟 User 確認、備份 settings.json + hook、精確收斂保護範圍（不是整批放行）、搬移後實跑驗證 4 個 loader 仍正常。

---
*核實者：Opus 4.8｜2026-07-03，grep 佐證見 [A_diagnosis.md](A_diagnosis.md) 痛點 3｜frontend-design 轉正：Sonnet 5，2026-07-05。*
