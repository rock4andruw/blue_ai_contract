接下來最好的規劃是：**先把 FastAPI + Demo UI 做出可展示版本，同時用最小成本把 skill 分層定型；等 Demo 穩了，再進入 Retrieval / MCP / product 化。**
這個順序最符合你目前「Phase 1 核心管道已完成、待完成 FastAPI

+ Dashboard」的專案狀態。

**目標排序**

你現在的主線很清楚：核心管道已完成，下一步就是 FastAPI endpoint、Demo UI 與月會展示。

而且你目前的技術核心也已經定案：Risk Rule Engine 做判斷與標記，LLM 只做解釋與表達，LLM 吃的是結構化資料而不是原始全量文件。

所以接下來不要大幅重構，而是做三件事：

+ **把已完成的核心能力包裝成可 demo 的產品形態** 。
+ **把 skill layer 定義出來，但只先做最重要的 1–2 個 skill** 。
+ **為 Phase 1.5 的 Retrieval 與 Phase 2 的 MCP 預留接口** 。

**四階段規劃**

**第 1 階段：封裝成 API**

先完成 POST /api/v1/contracts/compare，因為這會成為 CLI、Demo
UI、未來 Dashboard 的共同入口。

建議 API 直接回傳固定 JSON 結構：metadata、diff_items、risk_flags、key_changes、report_sections、markdown_report、summary_mode，其中 summary_mode
用來標示是 Claude API 還是 template fallback。

做法：

+ 不重寫核心邏輯，直接包 orchestrator.py。
+ llm_service.py若失敗，回 template_fallback，不要讓整個 API 失敗。
+ 先不接 DB，先走檔案上傳與記憶體處理。這符合你「Demo 先快速，正式再升級」的前端與系統策略。

**第 2 階段：做穩定 Demo UI**

UI 只做一頁靜態 HTML 就夠，因為專案文件本來就把 Demo 階段的前端定位成靜態 HTML，而不是正式版 React。

畫面只要能清楚展示：

+ 兩份合約輸入
+ 3–5 個主要變更
+ 高 / 中 / 低風險條款
+ 每個高風險的協商對策
+ 完整報告下載 / 顯示

做法：

+ 一定加上  **範例模式** （v1 vs v2 / v3 / v4 / v5），確保 demo 不受上傳格式影響。這會讓你在月會或比賽展示時更穩定。
+ 第一版 UI 不做複雜互動，只要資料可讀、層次分明、能把「像有資深法務顧問幫你審合約」這句定位展示出來即可。

**第 3 階段：最小 skill 分層**

這階段不是全面 skill 化，而是把**最容易變、最值得重用**的部分抽出來。

以你現在架構，最優先應該抽成 skill 的只有這幾個：

+ contract-risk-analysis.md：把 risk_code
  + trigger_reason + evidence轉成白話摘要與商業影響。
+ negotiation-strategy.md：每個 high-risk 生成 2–3 個協商方案的規則與輸出格式。
+ report-writing.md：Markdown 報告的章節結構、重點排序、語氣與審閱分層。

做法：

+ skill 只負責 prompt/spec，不碰 parser / diff / risk rule。
+ llm_service.py改成讀 skill 內容或 skill adapter。
+ 先保留現有
  template fallback，避免 skill 化後影響 Demo 穩定性。

**第 4 階段：Phase 1.5 能力補強**

等 Demo 穩了，再做 Retrieval Service，也就是你 service design 裡提到的 tool_rag / retrieval.py。

這一層的價值是：

+ 幫 LLM 找公司標準條款、相似條款、參考依據。
+ 讓
  negotiation_options 更具體，也能開始接近你專案文件中的 Insight 分析方向。

做法：

+ 先用檔案型的
  reference clause corpus，不一定馬上上 pgvector。
+ 等 reference
  規模變大，再進 PostgreSQL + pgvector，這也對齊你文件中的 Phase 1.5 規劃。

**這樣做的理由**

這種順序最符合你現在的成熟度。

因為你已經有完整核心鏈：Parser → Alignment → Diff → Risk → LLM →
Report，現在最缺的是「入口與展示」，不是再做新的分析模組。

而且 service design 已經很明確地把責任切開了：

+ rule
  engine 可測試、可重現、可追溯；
+ LLM 處理結構化輸入，降低幻覺；
+ 新增風險類型只補規則，優化語氣只改 prompt，彼此互不影響。

換句話說，你現在最應該做的是 **順著這個設計把外層補齊** ，而不是回頭大改核心。

**建議的時間排程**

**今天到明天**

+ 定 API
  schema。
+ 做 POST /api/v1/contracts/compare。
+ 增加 summary_mode、example_id、processing_time_ms等對 demo 有幫助的欄位。

**明天到後天**

+ 完成靜態 Demo
  UI。
+ 加上範例模式與
  Markdown 報告展示。
+ 準備 3 組固定展示案例：v1-v2、v1-v4、v1-v5。

**後天到本週末**

+ 抽出第一個 skill：contract-risk-analysis.md。
+ 視時間加第二個：negotiation-strategy.md。
+ 做一次
  end-to-end demo rehearsal。

**下週**

+ 規劃 retrieval.py與 reference
  clause corpus。
+ 盤點 Taiwan
  Law MCP / office-365 MCP 的接法，作為 Phase 2
  roadmapping。

**具體做法清單**

你可以直接照這個順序執行：

1. api/contracts.py
   + compare_contracts(files,
     use_example, example_id)
2. schemas_api.py
   + 定義 request
     / response model
3. frontend/demo.html
   + 上傳區、範例區、結果區
4. .claude/skills/contract-risk-analysis.md
   + 輸入：RiskFlag[]
   + 輸出：plain_summary + business_impact
5. .claude/skills/negotiation-strategy.md
   + 輸入：高風險項目 +
     reference clause
   + 輸出：negotiation_options[]
6. retrieval.py（下一步）
   + 先簡單檔案檢索，後面再接 pgvector
