# Harness 制度總覽（docs/harness/）

> 本目錄是 Blue-AI 專案的「工作流防閉環迭代機制」。讀者是未來的**主控模型與弱模型（Sonnet / Haiku）**。
> CLAUDE.md 只是路由中心，真正的規則在這裡。**動手前先讀對應章節，不要靠記憶或自由心證。**

## 檔案地圖

| 檔案 | 用途 | 何時讀 |
|------|------|--------|
| [A_diagnosis.md](A_diagnosis.md) | 漏水診斷書：前三大痛點與機制級阻斷方案 | 想理解「為什麼有這些規則」時 |
| [C_model_dispatch.md](C_model_dispatch.md) | 模型調度與動態升降級守則 | 派工給 subagent、決定用哪個模型時 |
| [D_judgment_matrix.md](D_judgment_matrix.md) | 判斷力外化矩陣（Checklist + 正反例） | 判斷「該停/該交付/該問人」時 |
| [E_dispatch_templates.md](E_dispatch_templates.md) | 標準化派工 Prompt 模板（可複製填空） | 實際撰寫 subagent prompt 時 |
| [F_reflection_protocol.md](F_reflection_protocol.md) | 知識迭代與反思協議 | 踩坑後、要更新這套 Harness 時 |
| [G_handover.md](G_handover.md) | 給未來 session 的交接信 | 接手新 session 時第一份讀 |
| [skills_runtime_assets.md](skills_runtime_assets.md) | `.claude/skills/*.md` 雙重身分說明 | 想碰 skills 檔案前 **必讀** |

> 註：編號跳過 B——**「交付 B」指的是 CLAUDE.md 的路由化改寫**（見專案根目錄 `CLAUDE.md`），不是 `docs/harness/` 下的獨立檔案。A_diagnosis.md 內提到的「見交付 B」即指此。

## 啟動順序（新 session）

1. 讀 CLAUDE.md（路由）→ 2. 讀 G_handover.md（現況）→ 3. 依任務讀 C/D/E → 4. 有更新需求才讀 F。

---
*建立者：Opus 4.8｜建立日：2026-07-03｜維護規則見 F_reflection_protocol.md*
