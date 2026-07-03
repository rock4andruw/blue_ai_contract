#!/usr/bin/env python3
"""PreToolUse 守衛（v2，放寬版）：兩個任務。

任務 A｜擋敏感檔外洩：`.env` 真金鑰、真實合約目錄（pic/nda/sla_contract）。
  策略：命令觸及敏感路徑時，**只擋「真正會讀出內容或把檔案送出去」的動詞**
        （cat/head/tail/less、python/ruby/node 等直譯器、cp/scp/rsync/curl/wget/mv/base64…），
        **放行單純列舉與搜尋**（ls/grep/find/wc/stat/git…）——後者是弱模型日常流程，
        誤擋會卡死開發。（此為 User 2026-07-03「放寬」決策。）

任務 B｜保護 skills 結構：擋對 `.claude/skills/` 的 mv / rm / rename（搬移或改名會弄壞
        src 的 4 處 runtime loader）。**編輯 skill 檔內容不受影響**（那是允許的 prompt 迭代）。

協定：stdin ← {"tool_name":"Bash","tool_input":{"command":"..."}}；擋→exit 2＋stderr；放行→exit 0。
設計：fail-safe，腳本自身異常一律放行（exit 0），絕不因守衛壞掉卡死所有 Bash。

殘留（誠實標記，見 docs/harness/A_diagnosis.md §4）：
  - `grep KEY .env` 屬放行的搜尋，理論上會印出含金鑰的行 → User 已選擇放行 grep 換取流程順暢。
  - 直譯器以變數間接組路徑、大小寫變體(.ENV)、不含關鍵片段的 glob(`.e*`) 仍可能繞過。
    防的是弱模型無意識直讀，非惡意規避。
"""
import json
import re
import sys

# --- 敏感路徑偵測 ---
_SAFE_ENV = {".env.example", ".env.sample", ".env.template", ".env.dist"}
_CONTRACT_NAMES = ("pic_contract", "nda_contract", "sla_contract")
_GLOB = re.compile(r"[*?\[]")

# --- 動詞分類 ---
# 觸及敏感路徑時，這些動詞會被擋（會讀出內容 / 把檔案送出去）
_EXFIL_VERBS = {
    "cat", "head", "tail", "less", "more", "bat", "tac", "nl", "rev",
    "od", "xxd", "hexdump", "strings", "base64", "openssl", "gpg",
    "python", "python3", "ruby", "perl", "node", "php", "awk", "sed",
    "cp", "scp", "rsync", "curl", "wget", "mv", "dd", "tee",
}
# 這些會弄壞 skills 結構
_SKILL_MUTATORS = {"mv", "rm", "rename", "trash"}
# 動詞抽取時要跳過的前綴/包裝
_WRAPPERS = {"sudo", "env", "nohup", "time", "command", "builtin",
             "exec", "xargs", "then", "do", "else", "!"}


def _verbs(cmd: str):
    """抽出每個命令片段（以 ; | & 分段）的實際動詞（去掉 VAR=val、sudo 等包裝）。"""
    out = []
    for seg in re.split(r"[;&|\n]+", cmd):
        toks = seg.strip().split()
        i = 0
        while i < len(toks):
            t = toks[i]
            if re.match(r"^[A-Za-z_]\w*=", t):  # 環境變數指派
                i += 1
                continue
            if t in _WRAPPERS:
                i += 1
                continue
            break
        if i < len(toks):
            out.append(toks[i].split("/")[-1])  # /bin/cat -> cat
    return out


def _sensitive_hits(cmd: str):
    hits = []
    for tok in re.findall(r"\.env[\w.\-]*", cmd):
        if tok not in _SAFE_ENV:
            hits.append(tok)
    for d in _CONTRACT_NAMES:
        if d in cmd:
            hits.append(d + "/")
    if _GLOB.search(cmd):
        if "contract" in cmd:
            hits.append("(glob)*contract*")
        if ".en" in cmd:
            hits.append("(glob).en*")
    return sorted(set(hits))


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("tool_name") != "Bash":
        return 0

    cmd = (data.get("tool_input") or {}).get("command", "") or ""
    verbs = _verbs(cmd)

    # 任務 B：保護 skills 結構（mv/rm/rename）——優先判，訊息較具體
    if ("skills" in cmd) and (".claude" in cmd or "skills/" in cmd):
        if any(v in _SKILL_MUTATORS for v in verbs):
            sys.stderr.write(
                "🛑 guard_sensitive 阻擋：偵測到對 .claude/skills/ 的搬移/改名/刪除。\n"
                "這 5 個檔是 src/services/contract 的 4 處 runtime loader 資產，搬移或改名會弄壞產品。\n"
                "編輯檔案內容是允許的；但**絕不可**搬移、改名、刪除或轉成 <name>/SKILL.md 目錄格式。\n"
                "詳見 docs/harness/skills_runtime_assets.md。此為刻意保護，請勿重試。\n"
            )
            return 2

    # 任務 A：擋敏感檔外洩
    sens = _sensitive_hits(cmd)
    if sens and any(v in _EXFIL_VERBS for v in verbs):
        offending = [v for v in verbs if v in _EXFIL_VERBS]
        sys.stderr.write(
            "🛑 guard_sensitive 阻擋：命令用 "
            + "/".join(sorted(set(offending)))
            + " 讀取或外送敏感資源 "
            + ", ".join(sens)
            + "。\n這是刻意的機制級保護（.env 真金鑰／真實合約），非錯誤，請勿重試。\n"
            "（列舉/搜尋如 ls、grep、git 是放行的；只有真正讀出內容/外送的動詞會被擋。）\n"
            "請改用不觸及這些路徑的做法，或請 User 手動處理。\n"
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
