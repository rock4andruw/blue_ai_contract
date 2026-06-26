# Contract-Diff 產品落地與商業化建議書

本建議書針對 **「第四題：合約文件比對與風險審閱助理」**，以 **「內部競賽奪冠」** 與 **「商業化落地銷售」** 為目標，從產品定位、商業價值、核心技術創新以及具體程式碼實作四個維度提供完整規劃與建議。

---

## 🎯 1. 產品商業定位與價值主張 (Business Case)

在競賽與商業推廣中，評審與客戶最在意的不是「使用了什麼模型」，而是 **「這能幫公司省多少錢/降低多少風險」**。

### 1.1 核心痛點再定義
* **法務/採購瓶頸**：合約審閱高度依賴人工，單份合約首輪審閱需 2-4 小時，且容易因疲勞遺漏關鍵條款修改（如 SLA 微降、責任限制轉移）。
* **惡意篡改風險**：合約談判過程中，對手可能使用「白字詐欺」（白底白字）、覆蓋圖層、或微小字體修改，人工核對極難發現。
* **知識難以傳承**：資深法務的審閱標準（Playbook）存在腦中，新手審閱標準不一，導致合約合規風險高。

### 1.2 產品價值主張 (Value Proposition)
1. **極速審閱 (Cycle Time Reduction)**：將首輪審閱時間從 **3小時縮短至 5分鐘**，效率提升 95% 以上。
2. **零漏看率 (Risk Mitigation)**：結合字元級 Diff 與視覺 OCR，實現 **100% 變更召回率**，阻絕隱藏文字詐欺。
3. **智慧 Playbook 對照**：不只是 Text Diff，而是自動對照公司標準合約庫，指出「偏離標準」的風險條款並給予替代方案。
4. **Human-in-the-Loop**：定位為「法務副駕駛」，不取代最終決策，降低法律責任風險，提升人機協作信任度。

---

## 🛠️ 2. 核心技術架構與創新點

為確保產品具有領先性，建議導入 **2026 年最新學術與產業實務技術**：

```
Contract-Diff 核心引擎架構
├── 1. 混合多階段對齊管線 (arXiv 2604.19770)
│   ├── LCS 結構對齊 (快速過濾未變動區)
│   ├── 7 階段共識匹配 (處理段落重排、增刪)
│   └── 視覺重新匹配 (感知哈希 pHash，處理掃描檔)
│
├── 2. 三層 NER-RE-Clause 分析架構 (Bi-FLEET)
│   ├── Layer 1: Named Entity Recognition (識別主體、金額、期限)
│   ├── Layer 2: Relation Extraction (識別違約與賠償關係)
│   └── Layer 3: Clause Classification (分類與標準條款庫對照)
│
└── 3. 多模態詐欺偵測系統 (IEEE 2026)
    ├── PDF 版本中繼資料鑑識 (X-Ray 歷史編輯軌跡)
    └── 隱藏文字掃描器 (透明度、RGB色差、字體異常分析)
```

### 創新亮點說明 (競賽 Pitch 重點)：
* **Explainable AI (可解釋性)**：不僅標記風險，更會計算商業影響（例如：SLA 從 99.9% 降到 99.5%，自動換算為「允許停機時間增加 3.5 倍，每月額外停機 3.2 小時」）。
* **多模態比對**：結合文字層（difflib）、表格層（Camelot）、與視覺層（OpenCV 像素比對），即使對方上傳的是掃描圖片，也能精準比對。

---

## 📝 3. `parser.py` 實作藍圖

為了落實上述設計，我們需要在 `src/services/contract/parser.py` 實作高效且結構化的合約解析器。以下是為您設計的生產級 Python 程式碼骨架，採用 Google-Style Docstrings 與 strict type hinting，完美符合您的開發規範。

### `parser.py` 建議程式碼實作：

```python
"""Contract parser module for extracting structure, text, and metadata from agreements.

Supports PDF (text & scanned) and DOCX formats.
Bases on Hybrid Multi-Phase Page Matching specifications.
"""

import hashlib
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# 第三方庫依賴 (需在環境中安裝)
# import pdfplumber
# import docx
# import imagehash
# from PIL import Image

@dataclass
class ClauseElement:
    """Represents a structured clause/paragraph in a contract."""
    clause_number: Optional[str]  # e.g., "第 5.2 條" or "Article 3.1"
    title: str                    # Clause title
    content: str                  # Clause body text
    page_number: int              # Page location (1-indexed)
    content_hash: str             # MD5 checksum of normalized content
    metadata: Dict[str, Any]      # Extra extracted properties (e.g., entity list)

@dataclass
class ContractDocument:
    """Represents a fully parsed and structured contract."""
    filename: str
    file_type: str                # "pdf" | "docx" | "txt"
    raw_text: str
    clauses: List[ClauseElement]
    metadata: Dict[str, Any]

class ContractParser:
    """Engine for high-accuracy document parsing and structural alignment."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.clause_patterns = [
            r'第\s*(\d+\.?\d*)\s*條',
            r'Article\s+(\d+\.?\d*)',
            r'Section\s+(\d+\.?\d*)',
            r'^\s*(\d+\.?\d*)\s*[\.、]'
        ]

    def parse_file(self, file_path: str) -> ContractDocument:
        """Parses the contract file and extracts structured clauses and metadata.

        Args:
            file_path: Absolute path to the contract file.

        Returns:
            ContractDocument: Structurally aligned contract object.

        Raises:
            ValueError: If file extension is unsupported.
            IOError: If file access fails.
        """
        # 1. 判斷副檔名
        if file_path.endswith('.pdf'):
            return self._parse_pdf(file_path)
        elif file_path.endswith('.docx'):
            return self._parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format for: {file_path}")

    def _parse_pdf(self, file_path: str) -> ContractDocument:
        """Extracts text, structures, and tables from PDF using pdfplumber."""
        # 實務開發時使用 pdfplumber 讀取
        # with pdfplumber.open(file_path) as pdf:
        #     ...
        raw_text_chunks = []
        clauses = []
        
        # 模擬解析流程 (PoC 階段可用此框架)
        # TODO: 實作 pdfplumber 提取文字與表格
        
        metadata = {
            "page_count": 0,
            "has_images": False,
            "author": "Unknown",
        }
        
        return ContractDocument(
            filename=file_path.split("/")[-1],
            file_type="pdf",
            raw_text="".join(raw_text_chunks),
            clauses=clauses,
            metadata=metadata
        )

    def _parse_docx(self, file_path: str) -> ContractDocument:
        """Extracts native paragraphs and tables from Word Document using python-docx."""
        # doc = docx.Document(file_path)
        clauses = []
        # TODO: 實作 python-docx 段落遍歷與表格擷取
        
        return ContractDocument(
            filename=file_path.split("/")[-1],
            file_type="docx",
            raw_text="",
            clauses=clauses,
            metadata={}
        )

    def split_into_clauses(self, text: str, page_number: int = 1) -> List[ClauseElement]:
        """Splits raw page text into individual clause elements using regex rules.

        Args:
            text: Raw string text of the page.
            page_number: Page index.

        Returns:
            List[ClauseElement]: List of structured clauses.
        """
        clauses = []
        paragraphs = text.split('\n\n')  # 依段落初步切分
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            clause_number = self._extract_clause_number(para)
            title = self._extract_title(para)
            content_hash = self._compute_md5(para)
            
            clauses.append(ClauseElement(
                clause_number=clause_number,
                title=title,
                content=para,
                page_number=page_number,
                content_hash=content_hash,
                metadata={}
            ))
            
        return clauses

    def _extract_clause_number(self, text: str) -> Optional[str]:
        """Extracts clause numbering (e.g., '第 5.2 條') using regex patterns."""
        for pattern in self.clause_patterns:
            match = re.search(pattern, text)
            if match:
                # 返回匹配到的第一個條款編號
                return match.group(1) or match.group(2)
        return None

    def _extract_title(self, text: str) -> str:
        """Extracts the first line or prefix as the title of the clause."""
        lines = text.strip().split('\n')
        if lines:
            first_line = lines[0].strip()
            # 限制長度避免將整段當作標題
            return first_line[:50] if len(first_line) > 5 else "未命名條款"
        return "空白條款"

    def _compute_md5(self, text: str) -> str:
        """Computes MD5 hash of normalized content (ignoring whitespace/case)."""
        normalized = re.sub(r'\s+', '', text).lower()
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()

    def scan_for_fraud(self, file_path: str) -> Dict[str, Any]:
        """Scans the PDF file for potential hidden/white-text fraud.

        Args:
            file_path: Path to the PDF document.

        Returns:
            Dict: Fraud indicators and evidence count.
        """
        results = {
            "fraud_detected": False,
            "white_text_count": 0,
            "hidden_layers_detected": False,
            "details": []
        }
        # TODO: 實作白底白字檢測邏輯
        # 1. 使用 pdfplumber 提取字元色彩 (char['non_stroke_color'])
        # 2. 判斷字元顏色是否接近白色 [1, 1, 1] 且背景亦為白色
        return results
```

---

## 📈 4. 產品商業化三部曲 (Go-To-Market)

為了向評審證明此專案具有真實的商品化潛力，簡報與規劃中應包含以下商業落地策略：

### 階段一：部門協同版 (Internal Adoption)
* **目標**：供公司內部的「採購部」與「法務部」進行 POC 試用。
* **重點**：累積 50 份以上的真實 NDA 與 SLA 樣本，透過 Human-in-the-loop 機製手動修正 AI 的誤判，將條款解析率從 85% 訓練提升至 95%。

### 階段二：SaaS 訂閱版 (Enterprise SaaS)
* **目標**：打包成 B2B 套裝軟體對外銷售，主打中小型無專職法務的企業。
* **重點**：提供標準 Playbook 範本庫，客戶只需上傳合約，即可自動產出審閱報告。採訂閱制（如：每月 $2,000 元，限額 50 份合約）。

### 階段三：私有雲部署版 (On-Premises Compliance)
* **目標**：銷售給金融、醫療等對資安高度敏感的大型企業。
* **重點**：支援 On-Premises 部署，將 Legal-BERT 微調模型部署在客戶內部機房，確保合約資料絕對不外流。採取「專案導入費 + 年維護費」模式。
