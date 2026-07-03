# G. 給未來 Session 的交接信

> 寫給下一個接手這個開發環境的模型（很可能是 Sonnet）。三件 User 沒問、但我認為最關鍵的事，加上這套制度的腐化風險與預防。
> 建議：**新 session 開場先讀 CLAUDE.md → 再讀本檔 → 再依任務讀 C/D/E。**

---

## 1. 三件 User 沒問、但最關鍵的事

### 事 1：這套 Harness 是「制度」，不是「這次任務」——別拿去當開發待辦
`docs/harness/` 全部是**長期沿用的規則**。未來 session 的日常開發（改 diff 服務、寫報告…）**依據**這些規則，但**不要**沒事去改規則本身。改規則的授權在 User（見 [F](F_reflection_protocol.md)）。把制度當成護欄，不是當成待辦清單。

### 事 2：`.env` / 合約 / skills 三個地雷，踩一個就出事
- **`.env` + 三合約目錄**：deny + hook 雙重保護。被擋是**刻意的**，看到 hook 的 exit 2 訊息**不要重試**。
- **`.claude/skills/*.md`**：不是可用 skill，是 `src/` 4 處 runtime loader 的資產，改格式/搬移＝弄壞產品。必讀 [skills_runtime_assets.md](skills_runtime_assets.md)。
- 這三件在 CLAUDE.md §1 也釘著，因為它們是「一次犯錯、代價很大」的類型。

### 事 3：真正的槓桿是「隔離驗證 + 升降級」，不是「用更強的模型硬幹」
省成本又保品質的關鍵不是「全用 Opus」，而是：**Opus 拆解與判斷 → Haiku/Sonnet 批次套用 → Fresh-Context Subagent 隔離驗收**（見 [C](C_model_dispatch.md)）。實作者自我背書「我驗過了」是最常見的品質破口——**永遠用獨立 context 驗收**。

---

## 2. 這套制度最可能的「退化/腐化方式」與預防

| # | 腐化方式（弱模型長期運作下） | 徵兆 | 預防機制 |
|---|------------------------------|------|----------|
| 1 | **CLAUDE.md 重新肥大**：模型忍不住把細節塞回主檔 | CLAUDE.md 又超過 ~150 行、開始出現長段落 | 鐵則：CLAUDE.md 只放路由+硬規則；細節寫進 `docs/harness/` 並加路由一行。定期用行數檢查 |
| 2 | **Context 檔再度增殖**：又冒出 SESSION_CONTEXT_日期.md 一堆 | root 出現多個日期尾綴的重複脈絡檔 | 滾動狀態只更新 PROJECT_CONTEXT.md；session log 直接進 `archive/`，不留 root |
| 3 | **LESSONS.md 無限膨脹**：只加不整理 | 超過 40 條/400 行仍在長 | [F](F_reflection_protocol.md) §3 硬門檻觸發精簡與抽象化 |
| 4 | **規則漂移/自我放寬**：模型嫌 hook 擋路，把 deny/hook 改鬆 | settings.json/hook 無 User 授權就被動 | [F](F_reflection_protocol.md) §4：⛔級檔案改動一律先問 User + 備份 + 只標過時不刪 |
| 5 | **驗收退化成自我背書**：省事跳過隔離驗證 | 回報常出現「應該可以」「看起來對」而無實跑證據 | [D](D_judgment_matrix.md) §2 完成判準要求實跑證據；[C](C_model_dispatch.md) §3 強制 Fresh-Context 驗收 |
| 6 | **模型偷懶全用便宜/或全用貴**：不做升降級 | Haiku 反覆卡同錯不升級，或無腦全 Opus 燒錢 | [C](C_model_dispatch.md) §2 升降級是硬規則：Haiku 錯1升、Sonnet 錯2升、模式化就降 |

**通用防腐心法**：每隔一段時間（或 User 要求時），派一個 Fresh-Context Opus 對照本表做「制度體檢」，抓出上述徵兆並回報 User。

---

## 3. 對抗審查殘留問題（第 2 輪後仍未解者）

> 依收尾規則，落檔後經 fresh-context 挑剔審查員掃描，最多修 2 輪；第 2 輪後殘留者記於此，不再迭代。

**結論：無阻斷性殘留，2 輪內全數修正。**

**補記（2026-07-03 第二次與 User 對齊）**：對抗審查後，User 指出建置過程未把三個架構衝突攤開決策，遂補一輪對齊並落實：① 專案改**自主式 allowlist**（弱模型自主運作不因等同意而卡死；`git push`/`rm`/`pip`/`curl` 仍 gated）；② guard hook 改 **v2 放寬版**（敏感路徑只擋讀取/外送動詞，放行 ls/grep/git）；③ skills「不可搬移」**改為機制強制**（hook 擋 mv/rm/改名 + `Write(.claude/skills/*/**)` deny）。此三項已實作＋19 情境測試。**教訓**：建置制度時，凡「安全 vs 自主」這類根本取捨，應在動手前用開場問題額度攤給 User，而非事後補。

對抗審查（fresh-context Opus 挑剔審查員）第 1 輪找出 8 個問題（1 高、2 中、5 低），第 1 輪全數修正；第 2 輪 fresh-context 複審確認「7 項需確認者全解決、無新引入的阻斷矛盾」。第 2 輪另指出 2 處**低度/美觀**殘留，也已於第 2 輪一併收尾：
- guard_sensitive.py 第 3 層 glob 偵測用短鍵 `.en`，會誤擋 `cat *.enc` 等 → 已在 hook docstring 補列此類 false positive。
- A_diagnosis §2 對照表舊描述「Read/Edit」→ 已更正為「Read/Edit/Write（27 條）」與 §3 權威紀錄一致。

**刻意保留、不再迭代的已知極限**（非缺陷，屬誠實邊界，詳見 [A_diagnosis.md](A_diagnosis.md) §4）：
1. guard_sensitive hook 防的是弱模型無意識直讀，**擋不住刻意規避**（如 `cat .e*` 不含 "en"、大小寫 `.ENV`、base64/變數間接組路徑）。真正的惡意防護需 OS 層權限，超出 Claude Code 範疇。
2. 合約目錄「全不透明」的 false positive（`ls 合約目錄`、`grep 合約名 文件`、`*contract*` glob 皆被擋）是**刻意取捨**——真實公司合約寧可過度保護。需列檔名請 User 手動提供。
3. 模糊的品味/商業美感決策，弱模型注定不穩 → 一律熔斷交 User（[D](D_judgment_matrix.md) §4）。
