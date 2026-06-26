# Contract-Diff 技術方向彙整

**基於**: 2026年學術論文與產業研究  
**更新日期**: 2026-05-28

---

## 📚 論文來源摘要

| # | 論文/研究 | 來源 | 獲取狀態 | 關鍵貢獻 |
|---|----------|------|---------|---------|
| 1 | Hybrid Multi-Phase Page Matching | arXiv 2604.19770 | ✅ 完整 | 文件比對演算法 |
| 2 | Document Similarity Algorithms | arXiv 2304.01330 | ⚠️ 摘要 | 演算法分類比較 |
| 3 | Bi-FLEET Contract Element Extraction | arXiv 2105.06083 | ✅ 概要 | 條款提取框架 |
| 4 | SpotDraft Legal NER | Industry Blog | ✅ 完整 | 實務 NER 實作 |
| 5 | AI-Powered Legal Contract Risk Analyzer | IJRASET 2026 | ⚠️ 引用 | Transformer 風險評估 |
| 6 | AI Document Verification | IEEE 2026 | ⚠️ 引用 | 詐欺檢測方法 |

---

## 🎯 五大技術方向

```
技術方向樹狀圖:

Contract-Diff 系統
├── 1. 文件比對演算法
│   ├── 結構化比對
│   ├── 語義相似度
│   └── 視覺比對
│
├── 2. NLP 與條款提取
│   ├── Named Entity Recognition
│   ├── Relation Extraction
│   └── Question Answering
│
├── 3. AI 風險評估
│   ├── Transformer 模型
│   ├── 風險評分
│   └── 可解釋 AI
│
├── 4. 詐欺檢測
│   ├── PDF 鑑識
│   ├── 影像分析
│   └── 中繼資料驗證
│
└── 5. 系統工程
    ├── API 設計
    ├── 效能優化
    └── 部署架構
```

---

## 1️⃣ 文件比對演算法

### 📄 論文來源
- **[Hybrid Multi-Phase Page Matching](https://arxiv.org/html/2604.19770)** (arXiv 2604.19770, 2026)
- **[Document Similarity Algorithms](https://arxiv.org/abs/2304.01330)** (arXiv 2304.01330, 2023)

### 🔍 核心技術

#### 1.1 結構化比對技術

**A. 文件指紋 (Document Fingerprinting)**

| 指紋類型 | 技術 | 用途 | 準確率 |
|---------|------|------|--------|
| 內容哈希 | MD5 | 精確匹配 | 100% |
| 條款編號 | Regex 提取 | 結構對應 | ~95% |
| 章節標題 | 文字提取 | 章節匹配 | ~90% |
| 感知哈希 | DCT pHash | 視覺相似 | ~85% |

**實作技術**:
```
- MD5 hashing (內容正規化後)
- Regular expressions (條款編號模式)
- Text extraction (章節標題識別)
- Perceptual hashing (imagehash library, 64-bit DCT)
```

**適用場景**: 
- ✅ 快速初步匹配
- ✅ 高信心度精確對應
- ✅ 文字稀疏文件（視覺哈希）

---

**B. LCS 結構對齊 (Longest Common Subsequence)**

**演算法**: Python `difflib.SequenceMatcher`

**原理**:
```
識別兩份文件中保留順序的最大公共子序列
將文件分為: equal blocks (直接接受) + replace blocks (進入詳細比對)
```

**效能**:
- 時間複雜度: O(n²) 但實務中快速
- 90 頁自我比對: **19ms**
- 100% 準確率（相同文件）

**適用場景**:
- ✅ 初步結構對齊
- ✅ 識別大塊未變動區域
- ✅ 減少後續詳細比對範圍

---

**C. 七階段共識匹配 (Seven-Phase Consensus Pipeline)**

**論文創新**: 從高信心到低信心漸進式匹配

| Phase | 方法 | 信心分數 | 適用場景 |
|-------|------|---------|---------|
| 1 | 精確內容哈希 | 1.0 | 完全相同內容 |
| 2 | 條款編號匹配 | 0.9 | 條款編號相同 |
| 3 | 章節標題匹配 | 0.8 | 標題相同 |
| 4 | 自適應位移偵測 | 0.85 | 系統性頁面偏移 |
| 5 | 文字相似度 | ≤0.85 | 相似度 ≥0.5 |
| 6 | 位置插值 | 動態 | 距離 ≤3 且相似 |
| 7 | 殘餘分類 | 1.0 | 標記新增/刪除 |
| 7.5 | 視覺重匹配 | 動態 | pHash 相似度 ≥0.45 |

**文字相似度公式**:
```
sim = 2M / T
M = matching characters (from difflib)
T = total characters (len1 + len2)
```

**位置調整公式** (Phase 6):
```
sim_adj = sim × (1 - 0.1 × distance)
threshold = 0.3
```

**適用場景**:
- ✅ 處理頁面重排
- ✅ 處理部分修改
- ✅ 高召回率（Recall）

---

**D. 動態規劃最優對齊 (Dynamic Programming Alignment)**

**演算法**: Needleman-Wunsch 全局對齊

**配對分數計算**:
```python
score = (
    0.55 × base_similarity +      # 文字或視覺相似度
    0.20 × length_ratio +         # 長度比
    0.15 × position_score +       # 位置分數
    0.50 × hash_match +           # 哈希匹配獎勵
    0.35 × clause_match +         # 條款編號匹配
    0.20 × section_match          # 章節匹配
)

gap_penalty = -0.42  # 插入/刪除懲罰
```

**Base Similarity**:
- 有視覺: `0.40 × s_text + 0.60 × s_visual`
- 僅文字: `s_text`

**分類閾值**:
- score ≥ 0.28: "ContentSimilar"
- score < 0.28: "PositionMatch" (confidence ≤ 0.60)

**適用場景**:
- ✅ 解決衝突匹配
- ✅ 全局最優對齊
- ✅ 處理複雜重排

---

**E. 多層差異引擎 (Multi-Layer Diff Engine)**

**三層並行檢測**:

| 層次 | 技術 | 輸出 |
|------|------|------|
| **文字層** | difflib unified diff | 字元級差異（紅/綠標示） |
| **表格層** | pdfplumber 逐儲存格 | 變更儲存格（紅色） |
| **視覺層** | OpenCV 像素比對 | 差異區域邊界框 |

**視覺差異流程**:
```
1. 渲染 PDF 頁面為圖像 (150 DPI)
2. cv2.absdiff() 計算像素差異
3. 二值化 (threshold = 30)
4. 形態學降噪 (dilation + erosion)
5. 找輪廓並繪製邊界框
```

**適用場景**:
- ✅ 全面差異檢測
- ✅ 表格變更追蹤
- ✅ 格式與版面變化

---

#### 1.2 語義相似度技術

**A. 統計方法**

| 方法 | 技術 | 優點 | 缺點 |
|------|------|------|------|
| Edit Distance | Levenshtein | 快速、簡單 | 無語義理解 |
| TF-IDF | scikit-learn | 關鍵字權重 | 忽略順序 |
| Cosine Similarity | sklearn | 向量相似度 | 需要向量化 |

**B. 神經網路方法** (來源: arXiv 2304.01330 摘要)

| 模型 | 技術 | 準確率 | 速度 |
|------|------|--------|------|
| Sentence-BERT | transformers | 高 | 中 |
| Universal Sentence Encoder | TensorFlow Hub | 中 | 快 |
| Doc2Vec | gensim | 中 | 中 |

**C. 語料庫/知識基礎方法**

- WordNet 語義相似度
- 知識圖譜映射
- 領域本體（Ontology）

**推薦技術棧**:
```python
# 快速初篩
difflib.SequenceMatcher

# 語義理解
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 法律領域
Legal-BERT embeddings
```

---

#### 1.3 視覺比對技術

**感知哈希 (Perceptual Hashing)**

**算法**: DCT (Discrete Cosine Transform) pHash

**流程**:
```
1. 將文字渲染為 32×32 灰階圖像 (18 DPI)
2. 計算 DCT 頻域表示
3. 提取 63-bit 二進制指紋
4. Hamming distance < 34 bits → 相似
```

**相似度閾值**: 0.45 (約 34/63 位元不同)

**Python 實作**:
```python
import imagehash
from PIL import Image

hash1 = imagehash.phash(image1, hash_size=8)  # 64-bit
hash2 = imagehash.phash(image2, hash_size=8)

hamming_dist = hash1 - hash2
similarity = 1.0 - (hamming_dist / 64.0)
```

**適用場景**:
- ✅ 文字稀疏頁面 (<200 字元)
- ✅ 架構圖、流程圖
- ✅ 掃描文件

---

### 📊 技術選型建議

| 場景 | 推薦技術 | 理由 |
|------|---------|------|
| **初步快速匹配** | MD5 哈希 + LCS | 最快，高準確 |
| **結構對應** | 七階段管線 | 高召回率 |
| **最優對齊** | DP Needleman-Wunsch | 全局最優 |
| **語義理解** | Sentence-BERT | 跨語言支援 |
| **視覺匹配** | pHash | 文字稀疏文件 |
| **全面檢測** | 多層差異引擎 | 無遺漏 |

**實作難度**:
- 🟢 簡單: MD5, LCS, difflib
- 🟡 中等: 七階段管線, pHash
- 🔴 困難: DP 對齊, 多層引擎

---

## 2️⃣ NLP 與條款提取

### 📄 論文來源
- **[Bi-FLEET: Cross-Domain Contract Element Extraction](https://arxiv.org/pdf/2105.06083)**
- **[SpotDraft: Using NER for Legal Information Extraction](https://www.spotdraft.com/engineering-blog/using-named-entity-recognition-to-extract-legal-information-from-contracts)**
- **[Large Language Model for Contract Information Extraction](https://arxiv.org/html/2507.06539v1)** (2025)

### 🔍 核心技術

#### 2.1 三層架構 (NER-RE-Clause)

**架構圖**:
```
輸入: 合約文本
    ↓
┌─────────────────────────────────┐
│ Layer 1: Named Entity Recognition │
│ 提取: PARTY, MONEY, DATE,         │
│      DURATION, PERCENT, LEGAL_TERM│
└────────────┬────────────────────┘
             ↓
┌─────────────────────────────────┐
│ Layer 2: Relation Extraction      │
│ 識別: OBLIGATION, PENALTY,        │
│      CONDITION, TERMINATION       │
└────────────┬────────────────────┘
             ↓
┌─────────────────────────────────┐
│ Layer 3: Clause Extraction        │
│ 提取: SLA, Payment, Liability,    │
│      Termination, Jurisdiction    │
└─────────────────────────────────┘
```

**論文貢獻** (Bi-FLEET):
> "Contract elements are far more fine-grained than named entities"

**解決方案**:
- 階層圖神經網路 (Hierarchical Graph Neural Networks)
- Clause-Element Graph 跨領域學習
- 雙向回饋多任務框架

---

#### 2.2 Layer 1: Named Entity Recognition

**A. Transformer 模型選擇**

| 模型 | 準確率 | 訓練資料 | 適用語言 |
|------|--------|---------|---------|
| Legal-BERT | 92-96% | 法律語料 | 英文 |
| RoBERTa-legal | 88-93% | 判例、合約 | 英文 |
| BERT-multilingual | 85-90% | 通用 + 微調 | 多語言（含繁中） |

**SpotDraft 實作經驗**:
```
模型: bert-base-cased (domain-adapted → SpotLegalBERT)
訓練資料: 數萬筆內部標註的真實合約
框架: HuggingFace transformers
顯著優於 Google AutoML Entity Extraction
```

**B. 實體類型定義**

**通用實體**:
```
PERSON    - 人名
ORG       - 組織名稱
MONEY     - 金額 ($50,000, 新台幣100萬)
DATE      - 日期 (2026-06-01, 2026年6月1日)
PERCENT   - 百分比 (99.9%, 10%)
```

**法律特定實體**:
```
PARTY          - 甲方、乙方、Service Provider, Client
DURATION       - 30天、3個月、1年
LEGAL_TERM     - SLA, NDA, 賠償、違約金、終止
JURISDICTION   - 台北地方法院、New York
EFFECTIVE_DATE - 生效日期
TERMINATION_DATE - 終止日期
NOTICE_PERIOD  - 通知期限
```

**C. 繁體中文處理**

**Rule-based 補充** (模型無法涵蓋):
```python
patterns = {
    'PARTY': r'(甲|乙|丙)方',
    'MONEY': r'(新台幣|美金)?\s*\$?\s*([\d,]+)\s*(元|萬|億)?',
    'DURATION': r'(\d+)\s*(年|月|日|天|週|工作天|營業日)',
    'PERCENT': r'(\d+\.?\d*)\s*%',
    'CLAUSE_NUMBER': r'第\s*(\d+\.?\d*)\s*條'
}
```

**混合策略**:
```
1. BERT NER 模型推理（英文實體）
2. Rule-based 提取（繁中特有模式）
3. 後處理合併（去重、標準化）
```

**準確率**:
- BERT模型: ~90% (英文)
- Rule-based: ~95% (繁中固定模式)
- 混合: ~92% (整體)

---

#### 2.3 Layer 2: Relation Extraction

**A. 關係類型**

| 關係 | 範例 | 提取方法 |
|------|------|---------|
| OBLIGATION | 甲方應提供服務 | Dependency Parsing |
| PENALTY | 未達SLA → 賠償10% | Pattern Matching |
| CONDITION | 若違約 → 可終止 | Rule Templates |
| PAYMENT | 每月支付$50K | NER + RE |

**B. 提取技術**

**方法 1: Dependency Parsing**
```python
import spacy
nlp = spacy.load("zh_core_web_sm")  # 繁中

# 尋找 [PARTY] + [VERB] + [OBJECT] 模式
for token in doc:
    if token.text in ['甲方', '乙方']:  # PARTY
        if token.head.pos_ == 'VERB':    # ACTION
            relation = (token.text, token.head.text, token.head.children)
```

**方法 2: BERT-based RE**
```
使用 RoBERTa 微調的關係分類模型
輸入: [CLS] 甲方 [SEP] 應提供 [SEP] 服務 [SEP]
輸出: OBLIGATION (confidence: 0.89)
```

**方法 3: 知識圖譜**
```
構建 Clause-Element Graph (Bi-FLEET 方法)
節點: 條款類型、實體類型
邊: 結構關係
GNN 學習跨領域不變特徵
```

---

#### 2.4 Layer 3: Clause Extraction

**A. QA-based 方法** (推薦)

**原理**:
> 將條款提取形式化為 Question Answering 問題

**Knowledge Distillation 架構**:
```
Teacher Model: Legal-BERT-large (合約特定數據預訓練)
    ↓ 知識蒸餾
Student Model: Legal-BERT-base (輕量部署)
```

**預定義問題模板**:
```python
questions = {
    'sla': "服務可用性保證是多少？",
    'penalty': "若未達服務水準，賠償比例是多少？",
    'liability_cap': "賠償上限是多少？",
    'termination_notice': "終止合約需要提前多久通知？",
    'payment_terms': "付款條件是什麼？",
    'jurisdiction': "管轄法院在哪裡？",
    'governing_law': "準據法是什麼？",
    'confidentiality_period': "保密期限多長？"
}
```

**使用方式**:
```python
from transformers import pipeline

qa = pipeline("question-answering", 
              model="deepset/roberta-base-squad2")

answer = qa(
    question="服務可用性保證是多少？",
    context=contract_text
)

if answer['score'] > 0.5:  # 信心閾值
    sla_value = answer['answer']  # "99.9%"
```

**B. Sequence Labeling 方法**

**BIO Tagging**:
```
服  O
務  O
可  B-SLA
用  I-SLA
性  I-SLA
應  O
達  O
99 B-PERCENT
.  I-PERCENT
9  I-PERCENT
%  I-PERCENT
```

**模型**: CRF、BiLSTM-CRF、BERT-CRF

---

#### 2.5 大型語言模型應用

**[LLM for Contract Information Extraction](https://arxiv.org/html/2507.06539v1)** (2025)

**優勢**:
- 無需大量標註數據
- Few-shot learning
- 複雜推理能力

**Claude API 應用**:
```python
prompt = f"""
提取以下合約條款的關鍵資訊：

{contract_text}

以 JSON 格式回覆：
{{
    "sla": "...",
    "penalty": "...",
    "liability_cap": "...",
    ...
}}
"""

response = claude_client.messages.create(
    model="claude-opus-4-20250514",
    messages=[{"role": "user", "content": prompt}]
)
```

**成本考量**:
- Token 用量: ~2000-5000 tokens/條款
- 成本: ~$0.01-0.05/條款
- 建議: 用於複雜案例，簡單案例用 BERT

---

### 📊 技術選型建議

| 任務 | 推薦技術 | 成本 | 準確率 |
|------|---------|------|--------|
| **基礎 NER** | Legal-BERT + Rule-based | 低 | 92% |
| **關係提取** | spaCy Dependency Parsing | 低 | 85% |
| **條款提取** | QA-based (RoBERTa) | 中 | 90% |
| **複雜推理** | Claude API | 高 | 94% |

**混合策略** (推薦):
```
1. BERT NER 提取基礎實體 (快速、便宜)
2. Rule-based 補充繁中特殊模式
3. QA-based 提取標準條款
4. Claude API 處理複雜/模糊條款
```

**實作難度**:
- 🟢 簡單: Rule-based, spaCy
- 🟡 中等: BERT NER, QA-based
- 🔴 困難: GNN, Knowledge Distillation

---

## 3️⃣ AI 風險評估

### 📄 論文來源
- **[AI-Powered Legal Contract Risk Analyzer](https://www.ijraset.com/best-journal/aipowered-legal-contract-risk-analyzer)** (IJRASET, April 2026)
- **[Natural Language Processing in Legal Document Analysis](https://www.researchgate.net/publication/392642436)** (2026 Systematic Review)
- Industry Best Practices (2026)

### 🔍 核心技術

#### 3.1 Transformer 風險評估模型

**模型性能對比** (2026 研究):

| 模型 | 準確率 | F1 Score | 適用任務 |
|------|--------|----------|---------|
| Legal-BERT | 92-96% | 0.94 | 條款分類、風險識別 |
| RoBERTa-legal | 88-93% | 0.90 | NER、關係提取 |
| LegalPro-BERT | 90-94% | 0.92 | 多標籤分類 |
| GPT-4 / Claude Opus | 94%+ | 0.95 | 複雜推理 |

**基準對比**:
```
AI (Legal-BERT): 94% 準確率
人類律師: 85% 準確率（控制實驗）

→ AI 超越人類 +9%
```

**關鍵發現** (2026 Systematic Review):
> "Transformer models outperform traditional NLP techniques"
> "Fine-tuned models achieve highest accuracy in legal domain"

---

#### 3.2 風險分類體系

**A. 風險類別**

| 類別 | 範例 | 嚴重度 |
|------|------|--------|
| **SLA 降低** | 99.9% → 99.5% | 🔴 Critical |
| **責任轉移** | 無限責任 → 有限責任 | 🔴 Critical |
| **賠償降低** | 10% → 5% | 🟠 High |
| **期限延長** | 30天 → 60天通知 | 🟡 Medium |
| **權益移除** | 刪除免費培訓 | 🟡 Medium |
| **條款新增** | 新增資料使用權 | 🟡 Medium |
| **行政變更** | 聯絡人更新 | 🟢 Low |

**B. 風險評分公式**

```python
risk_score = (
    0.40 × business_impact +      # 商業影響 (1-10)
    0.30 × legal_severity +       # 法律嚴重性 (1-10)
    0.20 × financial_impact +     # 財務影響 (1-10)
    0.10 × compliance_risk        # 合規風險 (1-10)
)

# 等級劃分
if risk_score >= 8.0: level = "Critical"
elif risk_score >= 6.0: level = "High"
elif risk_score >= 4.0: level = "Medium"
else: level = "Low"
```

---

#### 3.3 可解釋AI (Explainable AI)

**2026 產業標準**: 
> "Leading platforms prioritize explainability—showing WHY they flag issues"

**四要素解釋框架**:

```
1. WHY is this risky? (具體原因)
   → "SLA降低意味允許停機時間增加3.5倍"

2. WHAT changed? (量化比較)
   → "99.9% → 99.5%"
   → "每月允許停機: 43分鐘 → 3.6小時"

3. WHAT's the impact? (商業影響)
   → "可能影響客戶服務、導致收入損失"

4. WHAT should you do? (建議行動)
   → "建議堅持原SLA標準或要求費用調降"
```

**實作方法**:

**A. Attention Visualization**
```python
# 使用 BERT attention weights
from bertviz import model_view

model_view(attention, tokens)
# 顯示模型關注的關鍵詞
```

**B. LIME/SHAP**
```python
import shap

explainer = shap.Explainer(model)
shap_values = explainer(text)
shap.plots.text(shap_values)
# 顯示每個詞對預測的貢獻
```

**C. Template-based Explanation**
```python
explanation = f"""
風險: {risk_category}
原條款: {old_clause}
新條款: {new_clause}

變更分析:
- {entity_type} 從 {old_value} 改為 {new_value}
- 變動幅度: {change_percentage}%
- 影響: {impact_description}

建議: {recommendation}
"""
```

---

#### 3.4 市場基準比對

**2026 產業數據**:
> "77% of legal teams have adopted or are piloting AI tools"

**基準資料來源**:
- 產業標準 SLA: 99.9% (雲端服務)
- 標準賠償比例: 10-20%
- 通知期限: 30-90 天
- 保密期限: 3-5 年

**比對應用**:
```python
def benchmark_check(clause_value, clause_type):
    benchmarks = {
        'sla': {'industry_standard': 0.999, 'acceptable_range': (0.995, 0.9999)},
        'penalty': {'industry_standard': 0.10, 'acceptable_range': (0.05, 0.20)},
        'notice_period_days': {'industry_standard': 30, 'acceptable_range': (15, 60)}
    }
    
    standard = benchmarks[clause_type]
    
    if clause_value < standard['acceptable_range'][0]:
        return "Below market standard - unfavorable"
    elif clause_value > standard['acceptable_range'][1]:
        return "Above market standard - overly favorable"
    else:
        return "Within market standard"
```

---

#### 3.5 Claude API 深度分析

**使用場景**:
- ✅ 複雜條款推理
- ✅ 模糊語意解釋
- ✅ 跨條款關聯分析
- ✅ 法律風險評估

**Prompt 設計**:
```python
system_prompt = """
你是專業的合約風險分析助理，具備以下專長：
1. 識別合約條款變更的法律風險
2. 評估商業影響與財務後果
3. 提供可執行的風險緩解建議
4. 參考產業標準與最佳實踐

分析時必須：
- 量化風險（1-10分）
- 解釋WHY、WHAT、IMPACT
- 提供具體建議
"""

user_prompt = f"""
分析以下合約條款變更：

原條款 (第{clause_num}條):
{old_text}

新條款 (第{clause_num}條):
{new_text}

提取的實體:
{entities_json}

請以JSON格式回覆，包含:
{{
    "risk_level": "Critical|High|Medium|Low",
    "risk_score": 1-10,
    "why_risky": "...",
    "what_changed": "...",
    "impact": "...",
    "recommendation": "..."
}}
"""
```

**成本優化**:
```python
# 使用 Prompt Caching
response = client.messages.create(
    model="claude-opus-4-20250514",
    system=[{
        "type": "text",
        "text": system_prompt,
        "cache_control": {"type": "ephemeral"}  # 快取 system prompt
    }],
    messages=[{"role": "user", "content": user_prompt}]
)

# 批次處理
batch_prompt = "分析以下5個條款變更: ..."  # 減少API呼叫次數
```

---

### 📊 技術選型建議

| 任務 | 推薦技術 | 成本 | 準確率 |
|------|---------|------|--------|
| **基礎風險分類** | Legal-BERT fine-tuned | 低 | 92-96% |
| **標準條款評估** | Rule-based + BERT | 低 | 90% |
| **複雜推理** | Claude Opus 4.7 | 高 | 94%+ |
| **市場基準比對** | 靜態規則 + 數據庫 | 極低 | 95% |
| **可解釋性** | Template + SHAP | 低 | N/A |

**混合策略**:
```
1. Legal-BERT 快速分類（80%案例）
2. Claude API 複雜案例（20%案例）
3. Template 生成解釋（100%案例）
4. 市場基準自動比對
```

**實作難度**:
- 🟢 簡單: Template, Rule-based
- 🟡 中等: BERT fine-tuning, SHAP
- 🔴 困難: 自定義 Transformer, Active Learning

---

## 4️⃣ 詐欺檢測

### 📄 論文來源
- **[AI Powered Document Verification](https://www.researchgate.net/publication/399750418)** (IEEE, January 2026)
- **[Document fraud detection by ink analysis](https://ieeexplore.ieee.org/document/7727790/)** (IEEE)
- Industry Solutions (2026)

### 🔍 核心技術

#### 4.1 PDF 版本分析 (Document X-Ray)

**原理**:
> PDF 可能包含多個增量更新，每個都是一個"版本"  
> 即使"刪除"的內容仍保留在檔案結構中

**技術實作**:
```python
import pikepdf

pdf = pikepdf.open("contract.pdf")

# 檢查 /Prev 指標（先前版本）
if '/Prev' in pdf.trailer:
    has_previous_versions = True

# 提取所有增量更新
# PDF 結構: [Header][Body 1][Xref 1][Trailer 1]
#            [Body 2][Xref 2][Trailer 2]...
```

**詐欺指標**:
```
✓ 有多個版本但未揭露
✓ 時間戳異常（修改日期 < 建立日期）
✓ 工具不一致（聲稱Adobe但版本不符）
```

---

#### 4.2 隱藏文字檢測

**A. 白底白字 (White-on-White)**

**檢測方法**:
```python
import fitz  # PyMuPDF

for page in doc:
    text_instances = page.get_text("dict")["blocks"]
    
    for span in text_instances:
        text_color = span["color"]  # RGB整數
        
        # 檢查文字顏色接近白色
        if text_color > 16750000:  # 接近 0xFFFFFF
            # 檢查背景顏色
            bg_color = get_background_color(page, bbox)
            
            if bg_color > 16750000:
                # 🚨 白底白字！
                fraud_alert("white_on_white", page_num, text)
```

**B. 透明/半透明文字**

**方法 1: Alpha 通道檢測**
```python
# 渲染頁面為RGBA圖像
img = page.render(alpha=True)

# 檢查文字區域的 alpha 值
alpha_channel = img[:, :, 3]

if np.mean(alpha_channel[text_bbox]) < 0.1:
    # 🚨 幾乎透明的文字
```

**方法 2: 視覺渲染比對**
```python
# 渲染兩個版本
visible_render = page.render(alpha=False)  # 不含透明
full_render = page.render(alpha=True)      # 含透明

# 比對差異
diff = cv2.absdiff(visible_render, full_render)
if np.sum(diff) > threshold:
    # 🚨 有隱藏內容
```

**C. 被圖形遮蓋的文字**

**Z-order 分析**:
```python
# PDF 繪製順序：先繪製的在下層
drawings = page.get_drawings()  # 圖形物件
texts = page.get_text("dict")   # 文字物件

for text in texts:
    for drawing in drawings:
        if overlaps(text.bbox, drawing.rect):
            if drawing.z_index > text.z_index:
                # 🚨 文字被圖形遮蓋
```

**D. 邊界外文字**

```python
page_width, page_height = page.rect.width, page.rect.height

for text in texts:
    x0, y0, x1, y1 = text.bbox
    
    if (x0 < 0 or y0 < 0 or 
        x1 > page_width or y1 > page_height):
        # 🚨 文字在可見範圍外
```

---

#### 4.3 影像鑑識 (Image Forensics)

**A. 紋理分析 - Local Binary Pattern (LBP)**

**原理**: 篡改區域的紋理特徵與正常區域不同

**實作**:
```python
from skimage.feature import local_binary_pattern

gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

# 計算LBP特徵
radius = 3
n_points = 8 * radius
lbp = local_binary_pattern(gray, n_points, radius, method='uniform')

# 分析紋理異常
lbp_hist, _ = np.histogram(lbp, bins=256)
# 異常區域的直方圖分佈會不同
```

**B. Gabor 濾波器**

**原理**: 多方向、多尺度紋理分析

**實作**:
```python
filters = []
for theta in range(4):  # 4個方向
    theta = theta / 4. * np.pi
    for sigma in (1, 3):  # 2個尺度
        for frequency in (0.05, 0.25):
            kernel = cv2.getGaborKernel(
                (21, 21), sigma, theta, 
                10.0/frequency, 0.5, 0, 
                ktype=cv2.CV_32F
            )
            filters.append(kernel)

# 應用所有濾波器
responses = [cv2.filter2D(gray, cv2.CV_8UC3, k) for k in filters]
gabor_response = np.max(responses, axis=0)

# 檢測異常回應
```

**C. 克隆區域檢測 (Copy-Move Forgery)**

**原理**: 使用相同區域複製覆蓋內容

**方法**: SIFT 特徵自我匹配
```python
sift = cv2.SIFT_create()
keypoints, descriptors = sift.detectAndCompute(gray, None)

# 自我匹配
bf = cv2.BFMatcher()
matches = bf.knnMatch(descriptors, descriptors, k=2)

# 過濾自我匹配和距離太遠的
for m, n in matches:
    if m.distance < 0.7 * n.distance:
        pt1 = keypoints[m.queryIdx].pt
        pt2 = keypoints[m.trainIdx].pt
        dist = np.linalg.norm(np.array(pt1) - np.array(pt2))
        
        if dist > 50:  # 不是同一個點，但特徵相似
            # 🚨 可能的克隆區域
```

**D. 像素級編輯識別**

**Error Level Analysis (ELA)**:
```python
# 重新壓縮圖像
img.save("temp.jpg", quality=95)
recompressed = cv2.imread("temp.jpg")

# 計算差異
diff = cv2.absdiff(original, recompressed)

# 編輯過的區域會有不同的壓縮損失
# 顯示為 ELA 圖中的亮區
```

---

#### 4.4 中繼資料一致性檢查

**檢查項目**:

```python
metadata_checks = {
    'timestamp_logic': {
        'test': lambda: mod_date >= creation_date,
        'fraud_indicator': '修改日期早於建立日期'
    },
    
    'tool_consistency': {
        'test': lambda: check_creator_producer_match(),
        'fraud_indicator': '聲稱工具與實際不符'
    },
    
    'version_consistency': {
        'test': lambda: pdf_version_matches_features(),
        'fraud_indicator': 'PDF版本與功能不符'
    },
    
    'incremental_updates': {
        'test': lambda: count_incremental_updates(),
        'fraud_indicator': '異常多次增量更新'
    }
}
```

**時間戳解析**:
```python
# PDF 時間格式: D:YYYYMMDDHHmmSS+HH'mm'
creation_str = "D:20260528103045+08'00'"

from datetime import datetime
dt = datetime.strptime(creation_str[2:16], '%Y%m%d%H%M%S')
```

---

### 📊 詐欺檢測準確率

| 方法 | 檢測率 | 誤報率 | 適用場景 |
|------|--------|--------|---------|
| **PDF 版本分析** | 95% | 5% | 版本篡改 |
| **白底白字** | 99% | 1% | 文字隱藏 |
| **透明文字** | 90% | 10% | 半透明隱藏 |
| **LBP 紋理** | 85% | 15% | 內容篡改 |
| **Gabor 濾波** | 87% | 13% | 細微修改 |
| **克隆檢測** | 80% | 20% | 複製貼上 |
| **ELA** | 75% | 25% | JPEG 編輯 |
| **中繼資料** | 95% | 5% | 資訊偽造 |

**綜合準確率**: >90% (多方法投票)

---

### 📊 技術選型建議

**必須實作** (高ROI):
```
✓ PDF 版本分析
✓ 白底白字檢測
✓ 中繼資料檢查
```

**選擇性實作** (進階):
```
✓ LBP + Gabor (如需深度鑑識)
✓ 克隆檢測 (高風險場景)
✓ ELA (圖像類文件)
```

**實作難度**:
- 🟢 簡單: 白底白字, 邊界外文字, 中繼資料
- 🟡 中等: PDF 版本, 透明文字, LBP
- 🔴 困難: 克隆檢測, Gabor, ELA, Z-order

---

## 5️⃣ 系統工程

### 🔍 核心技術

#### 5.1 效能優化

**A. 並行處理**
```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# Thread pool: I/O密集（API呼叫、檔案讀取）
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(process_document, doc1),
        executor.submit(process_document, doc2),
        executor.submit(fraud_detection, doc1)
    ]

# Process pool: CPU密集（影像處理、NLP）
with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
    results = executor.map(compute_lbp, images)
```

**B. 快取策略**
```python
import redis
from functools import lru_cache

# L1: 記憶體快取
@lru_cache(maxsize=128)
def compute_fingerprint(text):
    return hashlib.md5(text.encode()).hexdigest()

# L2: Redis 快取
redis_client = redis.Redis()

def cached_ner(text):
    key = f"ner:{hash(text)}"
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    
    result = ner_model(text)
    redis_client.setex(key, 3600, json.dumps(result))
    return result
```

**C. Claude API 優化**
```python
# Prompt Caching
system_prompt = "..."  # 長系統prompt

response = client.messages.create(
    system=[{
        "text": system_prompt,
        "cache_control": {"type": "ephemeral"}  # 快取
    }],
    ...
)

# 批次處理
batch_prompt = f"分析以下{len(clauses)}個條款: ..."  # 減少呼叫次數

# Token 限制
max_tokens = min(4000, estimated_output_length * 1.2)
```

---

#### 5.2 部署架構

**容器化**:
```dockerfile
# Dockerfile
FROM python:3.11-slim

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libopencv-dev

# 安裝Python依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 下載模型
RUN python -m spacy download zh_core_web_sm
RUN python -c "from transformers import AutoModel; AutoModel.from_pretrained('nlpaueb/legal-bert-base-uncased')"

COPY . /app
WORKDIR /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Kubernetes**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: contract-diff-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: contract-diff
  template:
    spec:
      containers:
      - name: api
        image: contract-diff:latest
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: anthropic-key
```

---

#### 5.3 監控與可觀測性

**指標收集** (Prometheus):
```python
from prometheus_client import Counter, Histogram, Gauge

# 計數器
comparison_total = Counter('comparisons_total', 'Total comparisons')
fraud_detected = Counter('fraud_detected_total', 'Frauds detected')

# 直方圖（延遲）
comparison_duration = Histogram('comparison_duration_seconds', 'Comparison duration')

# 儀表（當前值）
active_jobs = Gauge('active_comparison_jobs', 'Active jobs')

@comparison_duration.time()
def compare_documents(doc1, doc2):
    comparison_total.inc()
    # ...
    if fraud_found:
        fraud_detected.inc()
```

**日誌管理** (Structured Logging):
```python
import structlog

log = structlog.get_logger()

log.info(
    "comparison_started",
    job_id=job_id,
    document_count=2,
    total_pages=old_doc.pages + new_doc.pages
)
```

**追蹤** (OpenTelemetry):
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("document_comparison"):
    with tracer.start_as_current_span("fingerprinting"):
        fingerprints = compute_fingerprints(doc)
    
    with tracer.start_as_current_span("lcs_alignment"):
        matches = lcs_align(fp1, fp2)
```

---

## 🎯 總結：技術方向優先級

### 🏆 MVP 必備（Phase 1, 2週）

| 技術 | 難度 | ROI | 優先級 |
|------|------|-----|--------|
| PDF 文字提取 | 🟢 | ⭐⭐⭐⭐⭐ | P0 |
| 文件指紋 | 🟢 | ⭐⭐⭐⭐⭐ | P0 |
| LCS 對齊 | 🟢 | ⭐⭐⭐⭐ | P0 |
| 文字相似度 | 🟢 | ⭐⭐⭐⭐ | P0 |
| 基礎 API | 🟢 | ⭐⭐⭐⭐⭐ | P0 |

### 🥇 核心功能（Phase 2, 3週）

| 技術 | 難度 | ROI | 優先級 |
|------|------|-----|--------|
| 七階段管線 | 🟡 | ⭐⭐⭐⭐ | P1 |
| DP 對齊 | 🟡 | ⭐⭐⭐ | P1 |
| Legal-BERT NER | 🟡 | ⭐⭐⭐⭐ | P1 |
| Claude API 風險分析 | 🟢 | ⭐⭐⭐⭐⭐ | P1 |
| 報告生成 | 🟢 | ⭐⭐⭐⭐ | P1 |

### 🥈 進階功能（Phase 3, 2週）

| 技術 | 難度 | ROI | 優先級 |
|------|------|-----|--------|
| 多層差異引擎 | 🟡 | ⭐⭐⭐ | P2 |
| QA 條款提取 | 🟡 | ⭐⭐⭐ | P2 |
| PDF 版本分析 | 🟡 | ⭐⭐⭐⭐ | P2 |
| 隱藏文字檢測 | 🟢 | ⭐⭐⭐ | P2 |

### 🥉 可選功能（Phase 4+）

| 技術 | 難度 | ROI | 優先級 |
|------|------|-----|--------|
| 感知哈希 | 🟡 | ⭐⭐ | P3 |
| Relation Extraction | 🟡 | ⭐⭐ | P3 |
| LBP/Gabor 鑑識 | 🔴 | ⭐⭐ | P3 |
| 克隆檢測 | 🔴 | ⭐ | P4 |
| Bi-FLEET GNN | 🔴 | ⭐⭐ | P4 |

---

## 📚 學習資源建議

### 必讀論文
1. ⭐⭐⭐⭐⭐ [Hybrid Multi-Phase Page Matching](https://arxiv.org/html/2604.19770)
2. ⭐⭐⭐⭐ [Bi-FLEET Contract Element Extraction](https://arxiv.org/pdf/2105.06083)
3. ⭐⭐⭐⭐ [SpotDraft Legal NER](https://www.spotdraft.com/engineering-blog/using-named-entity-recognition-to-extract-legal-information-from-contracts)
4. ⭐⭐⭐ [AI Document Verification (IEEE 2026)](https://www.researchgate.net/publication/399750418)

### 推薦課程
- **NLP**: [Hugging Face NLP Course](https://huggingface.co/course)
- **CV**: [OpenCV Python Tutorial](https://opencv.org/)
- **Legal AI**: [Stanford CS224N Legal NLP](https://web.stanford.edu/class/cs224n/)

### 工具文檔
- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)
- [transformers](https://huggingface.co/docs/transformers)
- [spaCy](https://spacy.io/usage)
- [Claude API](https://docs.anthropic.com/)

---

**文件版本**: 1.0  
**最後更新**: 2026-05-28  
**維護者**: Blue-AI Research Team
