# Contract-Diff 技術設計文件

**專案**: Blue-AI Contract Comparison Assistant  
**版本**: 1.0  
**日期**: 2026-05-28  
**基於**: 2026 年高引用學術論文

---

## 目錄

1. [系統架構](#1-系統架構)
2. [核心演算法設計](#2-核心演算法設計)
3. [AI/ML 模型架構](#3-aiml-模型架構)
4. [資料流程](#4-資料流程)
5. [API 設計](#5-api-設計)
6. [效能指標](#6-效能指標)
7. [實作計劃](#7-實作計劃)

---

## 1. 系統架構

### 1.1 高階架構圖

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Web UI     │  │  Mobile App  │  │   CLI Tool   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
┌─────────────────────────────┼─────────────────────────────────────┐
│                    API Gateway Layer                              │
│  ┌──────────────────────────┴─────────────────────────┐          │
│  │  Kong / NGINX (Rate Limiting, Auth, Routing)       │          │
│  └──────────────────────────┬─────────────────────────┘          │
└─────────────────────────────┼─────────────────────────────────────┘
                              │
┌─────────────────────────────┼─────────────────────────────────────┐
│                    Application Layer                              │
│  ┌───────────────┬──────────┴────────┬───────────────────────┐   │
│  │               │                   │                       │   │
│  │  Document     │  Comparison       │   Risk Analysis       │   │
│  │  Processor    │  Engine           │   Service             │   │
│  │  Service      │  Service          │   (AI/ML)             │   │
│  │               │                   │                       │   │
│  └───────┬───────┴────────┬──────────┴──────┬────────────────┘   │
│          │                │                 │                    │
│  ┌───────┴────────┬───────┴─────────┬───────┴────────┐          │
│  │  Fraud         │  Template       │  Report        │          │
│  │  Detection     │  Generator      │  Generator     │          │
│  │  Service       │  Service        │  Service       │          │
│  └───────┬────────┴───────┬─────────┴───────┬────────┘          │
└──────────┼────────────────┼─────────────────┼────────────────────┘
           │                │                 │
┌──────────┼────────────────┼─────────────────┼────────────────────┐
│          │     AI/ML Integration Layer      │                    │
│  ┌───────┴─────────┐  ┌──────────────┐  ┌──┴──────────────┐    │
│  │  Claude API     │  │ Legal-BERT   │  │  Azure Speech   │    │
│  │  Opus 4.7       │  │ (Local)      │  │  (Optional)     │    │
│  └─────────────────┘  └──────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
           │                │                 │
┌──────────┼────────────────┼─────────────────┼────────────────────┐
│          │         Data Layer               │                    │
│  ┌───────┴─────────┐  ┌──────────────┐  ┌──┴──────────────┐    │
│  │  PostgreSQL     │  │    Redis     │  │  Blob Storage   │    │
│  │  (Metadata)     │  │   (Cache)    │  │  (Files)        │    │
│  └─────────────────┘  └──────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 微服務架構

#### Service 1: Document Processor
**職責**: 文件解析、文字提取、OCR
**技術棧**: Python, FastAPI, PyMuPDF, pdfplumber, pytesseract
**輸入**: PDF/DOCX 檔案
**輸出**: 結構化文字 + 中繼資料

#### Service 2: Comparison Engine
**職責**: 混合多階段比對演算法
**技術棧**: Python, NumPy, difflib
**輸入**: 兩份結構化文件
**輸出**: 差異對照表 + 信心分數

#### Service 3: Risk Analysis Service
**職責**: AI 驅動的風險評估、條款提取
**技術棧**: Python, transformers, Claude API
**輸入**: 差異清單 + 原始文件
**輸出**: 風險評分 + 解釋

#### Service 4: Fraud Detection Service
**職責**: 隱藏文字、詐欺偵測
**技術棧**: Python, OpenCV, pikepdf
**輸入**: 原始 PDF
**輸出**: 詐欺指標 + 證據

#### Service 5: Report Generator
**職責**: 產生多格式報告
**技術棧**: Python, Jinja2, WeasyPrint
**輸入**: 分析結果
**輸出**: Markdown/PDF/HTML 報告

---

## 2. 核心演算法設計

### 2.1 混合多階段比對管線

**基於**: [Hybrid Multi-Phase Page Matching (arXiv 2604.19770)](https://arxiv.org/html/2604.19770)

#### Phase 1: 文件指紋 (Document Fingerprinting)

```python
class DocumentFingerprint:
    """
    為每個頁面/段落產生多重指紋
    """
    def __init__(self, page_content: str, page_number: int):
        self.content_hash = self._compute_content_hash(page_content)
        self.clause_number = self._extract_clause_number(page_content)
        self.section_title = self._extract_section_title(page_content)
        self.perceptual_hash = self._compute_phash(page_content)
        
    def _compute_content_hash(self, content: str) -> str:
        """
        MD5 of normalized text (whitespace collapsed, lowercased)
        返回空字串如果內容 < 50 字元
        """
        normalized = re.sub(r'\s+', ' ', content.lower()).strip()
        if len(normalized) < 50:
            return ""
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _extract_clause_number(self, content: str) -> Optional[str]:
        """
        提取條款編號 (e.g., "第 5.2 條", "Article 3.1")
        使用 regex: r'第\s*(\d+\.?\d*)\s*條|Article\s+(\d+\.?\d*)'
        """
        patterns = [
            r'第\s*(\d+\.?\d*)\s*條',
            r'Article\s+(\d+\.?\d*)',
            r'Section\s+(\d+\.?\d*)',
            r'^\s*(\d+\.?\d*)\s*[\.、]'
        ]
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        return None
    
    def _extract_section_title(self, content: str) -> str:
        """
        第一行實質文字（用於章節標題匹配）
        """
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 5:  # 過濾太短的行
                return line
        return ""
    
    def _compute_phash(self, content: str) -> str:
        """
        感知哈希（用於文字稀疏頁面）
        僅在內容 < 200 字元時計算
        """
        if len(content) >= 200:
            return ""
        
        # 將文字轉換為圖像並計算 pHash
        # 使用 imagehash library
        from PIL import Image, ImageDraw, ImageFont
        import imagehash
        
        img = Image.new('L', (256, 256), color=255)
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        draw.text((10, 10), content[:100], fill=0, font=font)
        
        phash = imagehash.phash(img, hash_size=8)  # 64-bit hash
        return str(phash)
```

#### Phase 2: LCS 結構對齊

```python
from difflib import SequenceMatcher

def lcs_structural_alignment(doc1_hashes: List[str], 
                             doc2_hashes: List[str]) -> List[MatchBlock]:
    """
    使用 difflib.SequenceMatcher 進行初步對齊
    返回: equal blocks (直接接受), replace blocks (進入多階段評估)
    """
    matcher = SequenceMatcher(None, doc1_hashes, doc2_hashes)
    blocks = matcher.get_opcodes()
    
    results = []
    for tag, i1, i2, j1, j2 in blocks:
        if tag == 'equal':
            # 直接接受，信心分數 = 1.0
            for k in range(i2 - i1):
                results.append(MatchBlock(
                    old_idx=i1 + k,
                    new_idx=j1 + k,
                    confidence=1.0,
                    method='lcs_equal'
                ))
        elif tag == 'replace':
            # 進入七階段共識匹配
            results.extend(
                seven_phase_consensus(
                    doc1_pages[i1:i2], 
                    doc2_pages[j1:j2]
                )
            )
        # 'insert' 和 'delete' 標記為新增/刪除頁面
        elif tag == 'insert':
            for k in range(j2 - j1):
                results.append(MatchBlock(
                    old_idx=None,
                    new_idx=j1 + k,
                    confidence=1.0,
                    method='inserted'
                ))
        elif tag == 'delete':
            for k in range(i2 - i1):
                results.append(MatchBlock(
                    old_idx=i1 + k,
                    new_idx=None,
                    confidence=1.0,
                    method='deleted'
                ))
    
    return results
```

#### Phases 3-9: 七階段共識匹配 + 視覺重匹配

```python
def seven_phase_consensus(old_pages: List[Page], 
                          new_pages: List[Page]) -> List[MatchBlock]:
    """
    七階段共識匹配管線
    """
    matches = []
    matched_old = set()
    matched_new = set()
    
    # Phase 1: 精確內容哈希匹配
    for i, old_page in enumerate(old_pages):
        for j, new_page in enumerate(new_pages):
            if (i not in matched_old and j not in matched_new and
                old_page.fingerprint.content_hash and
                old_page.fingerprint.content_hash == new_page.fingerprint.content_hash):
                matches.append(MatchBlock(i, j, confidence=1.0, method='exact_hash'))
                matched_old.add(i)
                matched_new.add(j)
    
    # Phase 2: 條款編號匹配
    for i, old_page in enumerate(old_pages):
        if i in matched_old:
            continue
        for j, new_page in enumerate(new_pages):
            if j in matched_new:
                continue
            if (old_page.fingerprint.clause_number and
                old_page.fingerprint.clause_number == new_page.fingerprint.clause_number):
                matches.append(MatchBlock(i, j, confidence=0.9, method='clause_number'))
                matched_old.add(i)
                matched_new.add(j)
    
    # Phase 3: 章節標題匹配
    for i, old_page in enumerate(old_pages):
        if i in matched_old:
            continue
        for j, new_page in enumerate(new_pages):
            if j in matched_new:
                continue
            if (old_page.fingerprint.section_title and
                old_page.fingerprint.section_title == new_page.fingerprint.section_title):
                matches.append(MatchBlock(i, j, confidence=0.8, method='section_title'))
                matched_old.add(i)
                matched_new.add(j)
    
    # Phase 4: 自適應頁面位移偵測
    # 檢測系統性位置偏移（例如所有頁面都往後移 2 頁）
    shift_matches = detect_page_shift(old_pages, new_pages, matched_old, matched_new)
    matches.extend(shift_matches)
    for m in shift_matches:
        matched_old.add(m.old_idx)
        matched_new.add(m.new_idx)
    
    # Phase 5: 文字相似度匹配 (threshold = 0.5)
    for i, old_page in enumerate(old_pages):
        if i in matched_old:
            continue
        best_match = None
        best_similarity = 0.0
        
        for j, new_page in enumerate(new_pages):
            if j in matched_new:
                continue
            sim = text_similarity(old_page.content, new_page.content)
            if sim >= 0.5 and sim > best_similarity:
                best_similarity = sim
                best_match = j
        
        if best_match is not None:
            matches.append(MatchBlock(i, best_match, 
                                     confidence=min(0.85, best_similarity),
                                     method='text_similarity'))
            matched_old.add(i)
            matched_new.add(best_match)
    
    # Phase 6: 基於位置的插值匹配
    # 對於距離 ≤ 3 的未匹配頁面，應用位置調整
    for i, old_page in enumerate(old_pages):
        if i in matched_old:
            continue
        for j, new_page in enumerate(new_pages):
            if j in matched_new:
                continue
            
            distance = abs(i - j)
            if distance <= 3:
                sim = text_similarity(old_page.content, new_page.content)
                adjusted_sim = sim * (1 - 0.1 * distance)
                
                if adjusted_sim >= 0.3:
                    matches.append(MatchBlock(i, j,
                                            confidence=adjusted_sim,
                                            method='position_interpolation'))
                    matched_old.add(i)
                    matched_new.add(j)
    
    # Phase 7: 殘餘分類（未匹配頁面標記為刪除/新增）
    deleted_pages = [i for i in range(len(old_pages)) if i not in matched_old]
    inserted_pages = [j for j in range(len(new_pages)) if j not in matched_new]
    
    # Phase 7.5: 視覺重匹配（針對刪除/新增集合）
    if deleted_pages and inserted_pages:
        visual_matches = visual_rematch(
            [old_pages[i] for i in deleted_pages],
            [new_pages[j] for j in inserted_pages]
        )
        matches.extend(visual_matches)
        for m in visual_matches:
            deleted_pages.remove(m.old_idx)
            inserted_pages.remove(m.new_idx)
    
    # 標記最終的刪除/新增
    for i in deleted_pages:
        matches.append(MatchBlock(i, None, confidence=1.0, method='deleted'))
    for j in inserted_pages:
        matches.append(MatchBlock(None, j, confidence=1.0, method='inserted'))
    
    return matches

def text_similarity(text1: str, text2: str) -> float:
    """
    文字相似度: sim = 2M / T
    M = matching characters, T = total characters
    """
    from difflib import SequenceMatcher
    matcher = SequenceMatcher(None, text1, text2)
    matching_blocks = matcher.get_matching_blocks()
    M = sum(block.size for block in matching_blocks)
    T = len(text1) + len(text2)
    return 2.0 * M / T if T > 0 else 0.0

def visual_rematch(old_pages: List[Page], 
                   new_pages: List[Page]) -> List[MatchBlock]:
    """
    使用感知哈希進行視覺重匹配
    threshold = 0.45 (約 34 個不同位元 / 63 總位元)
    """
    import imagehash
    matches = []
    
    for i, old_page in enumerate(old_pages):
        if not old_page.fingerprint.perceptual_hash:
            continue
        
        for j, new_page in enumerate(new_pages):
            if not new_page.fingerprint.perceptual_hash:
                continue
            
            old_hash = imagehash.hex_to_hash(old_page.fingerprint.perceptual_hash)
            new_hash = imagehash.hex_to_hash(new_page.fingerprint.perceptual_hash)
            
            hamming_distance = old_hash - new_hash
            similarity = 1.0 - (hamming_distance / 64.0)
            
            if similarity >= 0.45:
                matches.append(MatchBlock(
                    old_page.original_idx,
                    new_page.original_idx,
                    confidence=similarity,
                    method='visual_rematch'
                ))
                break  # 找到最佳匹配後跳出
    
    return matches
```

#### Phase 10: 動態規劃最優對齊

```python
def dynamic_programming_alignment(old_pages: List[Page],
                                 new_pages: List[Page],
                                 candidate_matches: List[MatchBlock]) -> List[MatchBlock]:
    """
    Needleman-Wunsch 風格的全局對齊
    解決衝突的候選匹配
    """
    m, n = len(old_pages), len(new_pages)
    
    # 初始化 DP 表
    D = [[0.0] * (n + 1) for _ in range(m + 1)]
    
    # Gap penalty
    gap_penalty = -0.42
    
    # 初始化第一行和第一列
    for i in range(1, m + 1):
        D[i][0] = i * gap_penalty
    for j in range(1, n + 1):
        D[0][j] = j * gap_penalty
    
    # 填充 DP 表
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            old_page = old_pages[i - 1]
            new_page = new_pages[j - 1]
            
            # 計算配對分數
            score = compute_pair_score(old_page, new_page, i - 1, j - 1, m, n)
            
            # DP 遞推
            D[i][j] = max(
                D[i - 1][j - 1] + score,  # 匹配
                D[i - 1][j] + gap_penalty,  # 刪除
                D[i][j - 1] + gap_penalty   # 插入
            )
    
    # 回溯找最優路徑
    matches = []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            score = compute_pair_score(old_pages[i - 1], new_pages[j - 1], i - 1, j - 1, m, n)
            if D[i][j] == D[i - 1][j - 1] + score:
                # 匹配
                if score >= 0.28:
                    method = 'dp_content_similar'
                    confidence = score
                else:
                    method = 'dp_position_match'
                    confidence = min(0.60, score)
                
                matches.append(MatchBlock(i - 1, j - 1, confidence, method))
                i -= 1
                j -= 1
                continue
        
        if i > 0 and (j == 0 or D[i][j] == D[i - 1][j] + gap_penalty):
            # 刪除
            matches.append(MatchBlock(i - 1, None, 1.0, 'dp_deleted'))
            i -= 1
        else:
            # 插入
            matches.append(MatchBlock(None, j - 1, 1.0, 'dp_inserted'))
            j -= 1
    
    matches.reverse()
    return matches

def compute_pair_score(old_page: Page, new_page: Page,
                      i: int, j: int, m: int, n: int) -> float:
    """
    綜合配對分數計算
    
    基礎相似度:
    - 如果有視覺相似度: 0.40 * s_text + 0.60 * s_visual
    - 僅文字: s_text
    
    完整分數 = 基礎相似度(0.55) + 長度比(0.20) + 位置分數(0.15) + 
               哈希匹配(+0.50) + 條款匹配(+0.35) + 章節匹配(+0.20)
    """
    # 文字相似度
    s_text = text_similarity(old_page.content, new_page.content)
    
    # 視覺相似度（如果有）
    s_visual = 0.0
    has_visual = False
    if old_page.fingerprint.perceptual_hash and new_page.fingerprint.perceptual_hash:
        import imagehash
        old_hash = imagehash.hex_to_hash(old_page.fingerprint.perceptual_hash)
        new_hash = imagehash.hex_to_hash(new_page.fingerprint.perceptual_hash)
        hamming_dist = old_hash - new_hash
        s_visual = 1.0 - (hamming_dist / 64.0)
        has_visual = True
    
    # 基礎相似度
    if has_visual:
        base_sim = 0.40 * s_text + 0.60 * s_visual
    else:
        base_sim = s_text
    
    # 文字長度比
    len1, len2 = len(old_page.content), len(new_page.content)
    length_ratio = min(len1, len2) / max(len1, len2) if max(len1, len2) > 0 else 0.0
    
    # 位置分數
    position_score = 1.0 - abs(i / m - j / n) if m > 0 and n > 0 else 0.0
    
    # 二元指標
    hash_match = 0.50 if (old_page.fingerprint.content_hash and
                         old_page.fingerprint.content_hash == new_page.fingerprint.content_hash) else 0.0
    
    clause_match = 0.35 if (old_page.fingerprint.clause_number and
                           old_page.fingerprint.clause_number == new_page.fingerprint.clause_number) else 0.0
    
    # 條款子字串匹配（部分匹配，例如 "5.2" 匹配 "5.2.1"）
    clause_substring = 0.10 if (old_page.fingerprint.clause_number and
                               new_page.fingerprint.clause_number and
                               (old_page.fingerprint.clause_number in new_page.fingerprint.clause_number or
                                new_page.fingerprint.clause_number in old_page.fingerprint.clause_number)) else 0.0
    
    section_match = 0.20 if (old_page.fingerprint.section_title and
                            old_page.fingerprint.section_title == new_page.fingerprint.section_title) else 0.0
    
    # 綜合分數
    total_score = (
        0.55 * base_sim +
        0.20 * length_ratio +
        0.15 * position_score +
        hash_match +
        clause_match +
        clause_substring +
        section_match
    )
    
    return total_score
```

### 2.2 多層差異引擎

```python
class MultiLayerDiffEngine:
    """
    三層差異檢測：文字、表格、視覺
    """
    
    def compute_diff(self, old_page: Page, new_page: Page) -> DiffResult:
        """
        並行計算三層差異
        """
        return DiffResult(
            text_diff=self.text_diff(old_page, new_page),
            table_diff=self.table_diff(old_page, new_page),
            visual_diff=self.visual_diff(old_page, new_page)
        )
    
    def text_diff(self, old_page: Page, new_page: Page) -> TextDiff:
        """
        字元級統一差異（unified diff）
        最多 5000 字元，顏色標註
        """
        from difflib import unified_diff
        
        old_text = old_page.content[:5000]
        new_text = new_page.content[:5000]
        
        diff = unified_diff(
            old_text.splitlines(keepends=True),
            new_text.splitlines(keepends=True),
            lineterm=''
        )
        
        # 將差異轉換為帶顏色的 HTML
        html_diff = []
        for line in diff:
            if line.startswith('-'):
                html_diff.append(f'<span style="color: red">{line}</span>')
            elif line.startswith('+'):
                html_diff.append(f'<span style="color: green">{line}</span>')
            else:
                html_diff.append(line)
        
        return TextDiff(
            old_text=old_text,
            new_text=new_text,
            unified_diff=''.join(html_diff),
            change_count=sum(1 for line in html_diff if 'color' in line)
        )
    
    def table_diff(self, old_page: Page, new_page: Page) -> TableDiff:
        """
        逐儲存格比對（使用 pdfplumber 提取）
        變更儲存格以紅色標示
        """
        import pdfplumber
        
        old_tables = old_page.extract_tables()  # List[List[List[str]]]
        new_tables = new_page.extract_tables()
        
        table_changes = []
        
        for table_idx in range(max(len(old_tables), len(new_tables))):
            old_table = old_tables[table_idx] if table_idx < len(old_tables) else []
            new_table = new_tables[table_idx] if table_idx < len(new_tables) else []
            
            changes = []
            for row_idx in range(max(len(old_table), len(new_table))):
                old_row = old_table[row_idx] if row_idx < len(old_table) else []
                new_row = new_table[row_idx] if row_idx < len(new_table) else []
                
                for col_idx in range(max(len(old_row), len(new_row))):
                    old_cell = old_row[col_idx] if col_idx < len(old_row) else ""
                    new_cell = new_row[col_idx] if col_idx < len(new_row) else ""
                    
                    if old_cell != new_cell:
                        changes.append(CellChange(
                            table_idx=table_idx,
                            row=row_idx,
                            col=col_idx,
                            old_value=old_cell,
                            new_value=new_cell
                        ))
            
            if changes:
                table_changes.append(TableChange(table_idx=table_idx, changes=changes))
        
        return TableDiff(table_changes=table_changes)
    
    def visual_diff(self, old_page: Page, new_page: Page) -> VisualDiff:
        """
        像素級差異（150 DPI 渲染）
        使用 OpenCV 進行形態學降噪
        """
        import cv2
        import numpy as np
        from pdf2image import convert_from_path
        
        # 渲染為圖像
        old_img = old_page.render_image(dpi=150)  # numpy array
        new_img = new_page.render_image(dpi=150)
        
        # 確保尺寸一致
        if old_img.shape != new_img.shape:
            # 調整大小到較大的尺寸
            max_height = max(old_img.shape[0], new_img.shape[0])
            max_width = max(old_img.shape[1], new_img.shape[1])
            
            old_img = cv2.resize(old_img, (max_width, max_height))
            new_img = cv2.resize(new_img, (max_width, max_height))
        
        # 計算差異
        diff = cv2.absdiff(old_img, new_img)
        
        # 轉換為灰階
        if len(diff.shape) == 3:
            diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        else:
            diff_gray = diff
        
        # 二值化
        _, binary = cv2.threshold(diff_gray, 30, 255, cv2.THRESH_BINARY)
        
        # 形態學降噪（膨脹 + 侵蝕）
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        binary = cv2.dilate(binary, kernel, iterations=2)
        binary = cv2.erode(binary, kernel, iterations=2)
        
        # 找到差異區域的邊界矩形
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        bounding_boxes = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 10 and h > 10:  # 過濾太小的區域
                bounding_boxes.append((x, y, w, h))
        
        return VisualDiff(
            diff_image=diff,
            bounding_boxes=bounding_boxes,
            change_percentage=np.count_nonzero(binary) / binary.size * 100
        )
```

---

## 3. AI/ML 模型架構

### 3.1 三層 NER-RE-Clause 架構

**基於**: [Bi-FLEET Cross-Domain Contract Element Extraction](https://arxiv.org/pdf/2105.06083)

```python
class ContractAnalysisPipeline:
    """
    三層合約分析管線
    """
    
    def __init__(self):
        # Layer 1: NER 模型
        self.ner_model = self._load_ner_model()
        
        # Layer 2: 關係提取模型
        self.re_model = self._load_relation_extraction_model()
        
        # Layer 3: 條款提取（QA-based）
        self.clause_model = self._load_clause_extraction_model()
        
        # Claude API（進階分析）
        self.claude_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    
    def _load_ner_model(self):
        """
        載入 Legal-BERT NER 模型
        實體類型：PARTY, MONEY, DATE, DURATION, PERCENT, LEGAL_TERM
        """
        from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
        
        # 選項 1: 使用預訓練的 Legal-BERT
        model_name = "nlpaueb/legal-bert-base-uncased"
        
        # 選項 2: 微調後的模型（如果有）
        # model_name = "./models/legal-bert-contract-ner"
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForTokenClassification.from_pretrained(model_name)
        
        ner_pipeline = pipeline(
            "ner",
            model=model,
            tokenizer=tokenizer,
            aggregation_strategy="simple"
        )
        
        return ner_pipeline
    
    def extract_entities(self, text: str) -> List[Entity]:
        """
        Layer 1: 提取法律實體
        """
        # 使用 NER 模型
        raw_entities = self.ner_model(text)
        
        # 後處理：合併分散的實體、標準化
        entities = []
        for ent in raw_entities:
            entity = Entity(
                text=ent['word'],
                label=ent['entity_group'],
                start=ent['start'],
                end=ent['end'],
                confidence=ent['score']
            )
            entities.append(entity)
        
        # 額外的 rule-based 提取（補充模型可能遺漏的）
        entities.extend(self._extract_taiwanese_legal_terms(text))
        
        return entities
    
    def _extract_taiwanese_legal_terms(self, text: str) -> List[Entity]:
        """
        針對繁體中文法律術語的 rule-based 提取
        """
        entities = []
        
        # 金額模式
        money_pattern = r'(新台幣|美金|港幣)?\s*\$?\s*([\d,]+)\s*(元|萬|億)?'
        for match in re.finditer(money_pattern, text):
            entities.append(Entity(
                text=match.group(0),
                label='MONEY',
                start=match.start(),
                end=match.end(),
                confidence=0.95
            ))
        
        # 期限模式
        duration_pattern = r'(\d+)\s*(年|月|日|天|週|工作天|營業日)'
        for match in re.finditer(duration_pattern, text):
            entities.append(Entity(
                text=match.group(0),
                label='DURATION',
                start=match.start(),
                end=match.end(),
                confidence=0.95
            ))
        
        # 百分比
        percent_pattern = r'(\d+\.?\d*)\s*%'
        for match in re.finditer(percent_pattern, text):
            entities.append(Entity(
                text=match.group(0),
                label='PERCENT',
                start=match.start(),
                end=match.end(),
                confidence=0.95
            ))
        
        # 台灣法律術語
        legal_terms = ['甲方', '乙方', '丙方', '個資法', '服務水準協議', 'SLA', 
                      '保密協議', 'NDA', '賠償', '違約金', '終止', '解除']
        for term in legal_terms:
            for match in re.finditer(re.escape(term), text):
                entities.append(Entity(
                    text=term,
                    label='LEGAL_TERM',
                    start=match.start(),
                    end=match.end(),
                    confidence=1.0
                ))
        
        return entities
    
    def extract_relations(self, text: str, entities: List[Entity]) -> List[Relation]:
        """
        Layer 2: 提取實體間關係
        例如: (甲方, 應提供, 服務) -> OBLIGATION
        """
        # 簡化版：使用 dependency parsing
        import spacy
        nlp = spacy.load("zh_core_web_sm")  # 繁中模型
        
        doc = nlp(text)
        relations = []
        
        # 尋找 obligation 模式: [PARTY] + [VERB] + [OBJECT]
        for sent in doc.sents:
            party = None
            action = None
            object_ = None
            
            for token in sent:
                # 識別甲方/乙方
                if token.text in ['甲方', '乙方', '丙方']:
                    party = token
                # 識別動詞（應、須、得、可）
                elif token.pos_ == 'VERB' and token.text in ['應', '須', '得', '可', '提供', '負責']:
                    action = token
                # 識別受詞
                elif token.dep_ in ['obj', 'dobj']:
                    object_ = token
            
            if party and action and object_:
                relations.append(Relation(
                    subject=party.text,
                    predicate=action.text,
                    object=object_.text,
                    relation_type='OBLIGATION',
                    confidence=0.8
                ))
        
        return relations
    
    def extract_clauses_qa(self, text: str, clause_types: List[str]) -> Dict[str, str]:
        """
        Layer 3: 使用 QA-based 方法提取條款
        
        基於知識蒸餾:
        - Teacher: Legal-BERT-large (合約微調)
        - Student: Legal-BERT-base (快速推理)
        """
        from transformers import pipeline
        
        # QA pipeline
        qa_pipeline = pipeline(
            "question-answering",
            model="deepset/roberta-base-squad2"  # 或微調的 Legal-BERT QA 模型
        )
        
        # 預定義問題模板
        questions = {
            'sla': "服務可用性保證是多少？",
            'penalty': "若未達服務水準，賠償比例是多少？",
            'liability_cap': "賠償上限是多少？",
            'termination_notice': "終止合約需要提前多久通知？",
            'payment': "付款條件是什麼？",
            'jurisdiction': "管轄法院在哪裡？",
        }
        
        results = {}
        for clause_type, question in questions.items():
            if clause_type in clause_types:
                answer = qa_pipeline(question=question, context=text)
                if answer['score'] > 0.5:  # 信心閾值
                    results[clause_type] = answer['answer']
        
        return results
    
    def analyze_with_claude(self, old_clause: str, new_clause: str, 
                           entities: List[Entity], relations: List[Relation]) -> RiskAnalysis:
        """
        使用 Claude API 進行深度風險分析
        """
        # 構建 prompt
        prompt = f"""你是專業的合約分析助理。請分析以下合約條款的變更，並評估風險。

## 原條款
{old_clause}

## 新條款
{new_clause}

## 提取的實體
{self._format_entities(entities)}

## 提取的關係
{self._format_relations(relations)}

請提供：
1. **變更摘要**: 簡述主要變更（1-2 句）
2. **風險等級**: Critical / High / Medium / Low
3. **風險分數**: 1-10
4. **具體風險**:
   - WHY 是風險？（具體原因）
   - WHAT 變了？（量化比較）
   - WHAT 影響？（商業影響）
5. **建議行動**: 具體可執行的建議

以 JSON 格式回覆。"""

        # 呼叫 Claude API
        response = self.claude_client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=2000,
            temperature=0,  # 一致性輸出
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # 解析回應
        import json
        result = json.loads(response.content[0].text)
        
        return RiskAnalysis(
            summary=result['變更摘要'],
            risk_level=result['風險等級'],
            risk_score=result['風險分數'],
            risks=result['具體風險'],
            recommendations=result['建議行動']
        )
```

### 3.2 詐欺檢測模組

**基於**: [AI Powered Document Verification (IEEE 2026)](https://www.researchgate.net/publication/399750418)

```python
class FraudDetectionService:
    """
    多模態詐欺檢測
    """
    
    def detect_fraud(self, pdf_path: str) -> FraudReport:
        """
        綜合詐欺檢測
        """
        return FraudReport(
            pdf_version_analysis=self.check_pdf_versions(pdf_path),
            hidden_text=self.detect_hidden_text(pdf_path),
            image_forensics=self.image_forensics_analysis(pdf_path),
            metadata_check=self.check_metadata_consistency(pdf_path)
        )
    
    def check_pdf_versions(self, pdf_path: str) -> PDFVersionAnalysis:
        """
        PDF 版本分析 - Document X-Ray
        提取所有嵌入的 PDF 版本（包括"刪除"的）
        """
        import pikepdf
        
        pdf = pikepdf.open(pdf_path)
        
        # 檢查 PDF 歷史版本
        versions = []
        if '/Prev' in pdf.trailer:
            # 有先前版本
            prev_ref = pdf.trailer['/Prev']
            versions.append({
                'version': 'previous',
                'reference': str(prev_ref)
            })
        
        # 檢查增量更新
        # PDF 可能包含多個增量更新，每個都是一個"版本"
        
        # 比較時間戳
        creation_date = pdf.docinfo.get('/CreationDate', '')
        mod_date = pdf.docinfo.get('/ModDate', '')
        
        timestamp_suspicious = False
        if creation_date and mod_date:
            # 檢查是否時間順序異常
            if mod_date < creation_date:
                timestamp_suspicious = True
        
        return PDFVersionAnalysis(
            has_previous_versions=len(versions) > 0,
            versions=versions,
            creation_date=creation_date,
            modification_date=mod_date,
            timestamp_suspicious=timestamp_suspicious
        )
    
    def detect_hidden_text(self, pdf_path: str) -> List[HiddenText]:
        """
        隱藏文字檢測
        1. 白底白字
        2. 透明/近透明文字
        3. 被圖形遮蓋的文字
        4. 邊界外文字
        """
        import fitz  # PyMuPDF
        
        doc = fitz.open(pdf_path)
        hidden_texts = []
        
        for page_num, page in enumerate(doc):
            # 提取文字及其屬性
            text_instances = page.get_text("dict")["blocks"]
            
            for block in text_instances:
                if block["type"] == 0:  # 文字區塊
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"]
                            color = span["color"]  # RGB 整數
                            bbox = span["bbox"]  # (x0, y0, x1, y1)
                            
                            # 檢查 1: 白底白字（color 接近 16777215 = 0xFFFFFF）
                            if color > 16750000:  # 接近白色
                                page_rect = page.rect
                                page_color = self._get_background_color(page, bbox)
                                if page_color > 16750000:  # 背景也是白色
                                    hidden_texts.append(HiddenText(
                                        page=page_num,
                                        text=text,
                                        bbox=bbox,
                                        reason='white_on_white',
                                        confidence=0.95
                                    ))
                            
                            # 檢查 2: 透明文字（需要檢查 alpha 通道）
                            # PyMuPDF 不直接提供 alpha，需要渲染檢查
                            
                            # 檢查 3: 邊界外文字
                            page_width, page_height = page.rect.width, page.rect.height
                            if (bbox[0] < 0 or bbox[1] < 0 or 
                                bbox[2] > page_width or bbox[3] > page_height):
                                hidden_texts.append(HiddenText(
                                    page=page_num,
                                    text=text,
                                    bbox=bbox,
                                    reason='outside_margins',
                                    confidence=1.0
                                ))
            
            # 檢查 4: 被圖形遮蓋的文字
            # 渲染頁面，比較文字位置與圖形位置
            drawings = page.get_drawings()
            for drawing in drawings:
                draw_rect = drawing["rect"]
                # 檢查文字是否在圖形下方
                # （需要更複雜的 z-order 分析）
        
        return hidden_texts
    
    def image_forensics_analysis(self, pdf_path: str) -> ImageForensics:
        """
        AI 影像鑑識
        1. 像素級編輯識別
        2. 字體不匹配檢測
        3. 克隆區域識別
        """
        import cv2
        import numpy as np
        from pdf2image import convert_from_path
        
        images = convert_from_path(pdf_path, dpi=300)
        
        all_anomalies = []
        
        for page_num, image in enumerate(images):
            img_array = np.array(image)
            
            # 1. 紋理分析（LBP）
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            lbp_features = self._compute_lbp(gray)
            
            # 檢測紋理異常（可能的篡改區域）
            texture_anomalies = self._detect_texture_anomalies(lbp_features)
            
            # 2. Gabor 濾波器
            gabor_response = self._apply_gabor_filters(gray)
            gabor_anomalies = self._detect_gabor_anomalies(gabor_response)
            
            # 3. 克隆區域檢測（重複區域）
            clone_regions = self._detect_clone_regions(gray)
            
            all_anomalies.append(PageForensics(
                page=page_num,
                texture_anomalies=texture_anomalies,
                gabor_anomalies=gabor_anomalies,
                clone_regions=clone_regions
            ))
        
        return ImageForensics(pages=all_anomalies)
    
    def _compute_lbp(self, gray_image: np.ndarray) -> np.ndarray:
        """
        Local Binary Pattern 紋理特徵
        """
        from skimage.feature import local_binary_pattern
        
        radius = 3
        n_points = 8 * radius
        lbp = local_binary_pattern(gray_image, n_points, radius, method='uniform')
        
        return lbp
    
    def _apply_gabor_filters(self, gray_image: np.ndarray) -> np.ndarray:
        """
        Gabor 濾波器（多方向、多尺度）
        """
        filters = []
        for theta in range(4):  # 4 個方向
            theta = theta / 4. * np.pi
            for sigma in (1, 3):  # 2 個尺度
                for frequency in (0.05, 0.25):
                    kernel = cv2.getGaborKernel((21, 21), sigma, theta, 
                                               10.0/frequency, 0.5, 0, ktype=cv2.CV_32F)
                    filters.append(kernel)
        
        # 應用所有濾波器
        responses = [cv2.filter2D(gray_image, cv2.CV_8UC3, kernel) for kernel in filters]
        
        # 組合回應
        gabor_response = np.max(responses, axis=0)
        
        return gabor_response
    
    def _detect_clone_regions(self, gray_image: np.ndarray) -> List[CloneRegion]:
        """
        克隆區域檢測（Copy-Move Forgery Detection）
        """
        # 使用 SIFT 或 SURF 特徵匹配
        sift = cv2.SIFT_create()
        keypoints, descriptors = sift.detectAndCompute(gray_image, None)
        
        # 自我匹配（尋找重複區域）
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(descriptors, descriptors, k=2)
        
        # 過濾掉自我匹配和距離太遠的匹配
        clone_regions = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                pt1 = keypoints[m.queryIdx].pt
                pt2 = keypoints[m.trainIdx].pt
                
                # 計算距離
                dist = np.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)
                
                # 如果距離夠遠（不是同一個點）但特徵相似（可能是克隆）
                if dist > 50:  # 像素
                    clone_regions.append(CloneRegion(
                        region1=pt1,
                        region2=pt2,
                        similarity=1.0 - m.distance,
                        distance=dist
                    ))
        
        return clone_regions
    
    def check_metadata_consistency(self, pdf_path: str) -> MetadataCheck:
        """
        中繼資料一致性檢查
        """
        import pikepdf
        from datetime import datetime
        
        pdf = pikepdf.open(pdf_path)
        
        inconsistencies = []
        
        # 檢查時間戳邏輯
        creation_date = pdf.docinfo.get('/CreationDate', '')
        mod_date = pdf.docinfo.get('/ModDate', '')
        
        if creation_date and mod_date:
            # 解析 PDF 時間格式: D:YYYYMMDDHHmmSS
            try:
                creation_dt = datetime.strptime(creation_date[2:16], '%Y%m%d%H%M%S')
                mod_dt = datetime.strptime(mod_date[2:16], '%Y%m%d%H%M%S')
                
                if mod_dt < creation_dt:
                    inconsistencies.append("修改日期早於建立日期")
            except:
                inconsistencies.append("時間戳格式異常")
        
        # 檢查工具一致性
        creator = pdf.docinfo.get('/Creator', '')
        producer = pdf.docinfo.get('/Producer', '')
        
        # 如果聲稱是 Adobe 產生但版本資訊不符
        if 'Adobe' in producer:
            # 檢查 PDF 版本是否合理
            pass
        
        return MetadataCheck(
            inconsistencies=inconsistencies,
            creation_date=creation_date,
            modification_date=mod_date,
            creator=creator,
            producer=producer
        )
```

---

## 4. 資料流程

### 4.1 完整處理流程

```
使用者上傳兩份合約 (PDF/DOCX)
        ↓
┌───────────────────────────────────────┐
│  Step 1: Document Ingestion          │
│  - 檔案驗證（格式、大小）              │
│  - 安全掃描（病毒、惡意程式碼）         │
│  - 儲存至 Blob Storage                │
└───────────────┬───────────────────────┘
                ↓
┌───────────────────────────────────────┐
│  Step 2: Document Processing          │
│  - PDF → 文字提取 (PyMuPDF)           │
│  - OCR (如需要, Tesseract)            │
│  - 表格提取 (pdfplumber)              │
│  - 結構化為 Page 物件                 │
└───────────────┬───────────────────────┘
                ↓
        ┌───────┴───────┐
        ↓               ↓
┌─────────────┐  ┌─────────────────────┐
│ Step 3a:    │  │ Step 3b:            │
│ Comparison  │  │ Fraud Detection     │
│ Engine      │  │ (並行)              │
│             │  │                     │
│ - 指紋產生  │  │ - PDF 版本分析      │
│ - LCS 對齊  │  │ - 隱藏文字掃描      │
│ - 七階段    │  │ - 影像鑑識          │
│ - DP 最優化 │  │ - 中繼資料檢查      │
│ - 差異引擎  │  │                     │
└──────┬──────┘  └──────┬──────────────┘
       │                │
       └────────┬───────┘
                ↓
┌───────────────────────────────────────┐
│  Step 4: AI Risk Analysis             │
│  - Layer 1: NER 提取實體              │
│  - Layer 2: 關係提取                  │
│  - Layer 3: QA-based 條款提取         │
│  - Claude API 深度分析                │
│  - 風險評分 + 可解釋性說明            │
└───────────────┬───────────────────────┘
                ↓
┌───────────────────────────────────────┐
│  Step 5: Report Generation            │
│  - 整合所有分析結果                    │
│  - 產生結構化 Markdown                │
│  - 轉換為 PDF/HTML (可選)             │
│  - 儲存報告至資料庫                    │
└───────────────┬───────────────────────┘
                ↓
┌───────────────────────────────────────┐
│  Step 6: Notification & Delivery      │
│  - 通知使用者（Email/Teams）           │
│  - 提供下載連結                        │
│  - 記錄審計軌跡                        │
└───────────────────────────────────────┘
```

### 4.2 資料模型

```python
# Database Schema (PostgreSQL)

class ComparisonJob(BaseModel):
    """
    比對任務
    """
    id: UUID
    user_id: UUID
    created_at: datetime
    status: str  # pending, processing, completed, failed
    
    # 文件資訊
    old_document_id: UUID
    new_document_id: UUID
    
    # 配置
    comparison_options: dict  # fraud_check, benchmark, etc.
    
    # 結果
    result_id: Optional[UUID]
    error_message: Optional[str]
    
    # 效能指標
    processing_time_ms: Optional[int]
    total_pages: Optional[int]

class Document(BaseModel):
    """
    文件
    """
    id: UUID
    user_id: UUID
    filename: str
    file_type: str  # pdf, docx
    file_size: int
    blob_url: str
    
    # 提取的內容
    total_pages: int
    extracted_text: Optional[str]
    structured_data: Optional[dict]  # JSON
    
    # 中繼資料
    creation_date: Optional[datetime]
    modification_date: Optional[datetime]
    creator: Optional[str]
    
    created_at: datetime

class ComparisonResult(BaseModel):
    """
    比對結果
    """
    id: UUID
    job_id: UUID
    created_at: datetime
    
    # 匹配結果
    page_matches: List[dict]  # MatchBlock 列表
    
    # 差異
    text_diffs: List[dict]
    table_diffs: List[dict]
    visual_diffs: List[dict]
    
    # 風險分析
    risk_analysis: dict
    overall_risk_score: float
    overall_risk_level: str
    
    # 詐欺檢測
    fraud_report: Optional[dict]
    
    # 報告
    report_markdown: str
    report_pdf_url: Optional[str]

class RiskFinding(BaseModel):
    """
    風險發現
    """
    id: UUID
    result_id: UUID
    
    # 變更資訊
    old_clause_number: str
    new_clause_number: str
    old_text: str
    new_text: str
    
    # 風險評估
    risk_level: str  # critical, high, medium, low
    risk_score: float  # 1-10
    risk_category: str  # sla_degradation, liability_shift, etc.
    
    # 提取的實體
    entities: List[dict]
    relations: List[dict]
    
    # AI 分析
    summary: str
    why_risky: str
    what_changed: str
    impact: str
    recommendation: str
    
    created_at: datetime
```

---

## 5. API 設計

### 5.1 RESTful API 端點

```yaml
# OpenAPI 3.0 Specification

openapi: 3.0.0
info:
  title: Contract Diff API
  version: 1.0.0
  description: AI-powered contract comparison and risk analysis

servers:
  - url: https://api.blue-ai.com/v1

paths:
  /contracts/upload:
    post:
      summary: 上傳合約文件
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
                file_type:
                  type: string
                  enum: [old, new]
      responses:
        '200':
          description: 上傳成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  document_id:
                    type: string
                    format: uuid
                  filename:
                    type: string
                  file_size:
                    type: integer
                  total_pages:
                    type: integer

  /contracts/compare:
    post:
      summary: 比對兩份合約
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                old_document_id:
                  type: string
                  format: uuid
                new_document_id:
                  type: string
                  format: uuid
                options:
                  type: object
                  properties:
                    contract_type:
                      type: string
                      enum: [NDA, SLA, MSA, purchase, employment]
                    enable_fraud_detection:
                      type: boolean
                      default: true
                    enable_benchmark:
                      type: boolean
                      default: false
                    risk_threshold:
                      type: string
                      enum: [critical, high, medium, low]
                      default: medium
      responses:
        '202':
          description: 比對任務已建立
          content:
            application/json:
              schema:
                type: object
                properties:
                  job_id:
                    type: string
                    format: uuid
                  status:
                    type: string
                  estimated_time_seconds:
                    type: integer

  /contracts/compare/{job_id}:
    get:
      summary: 查詢比對任務狀態
      parameters:
        - name: job_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: 任務狀態
          content:
            application/json:
              schema:
                type: object
                properties:
                  job_id:
                    type: string
                  status:
                    type: string
                    enum: [pending, processing, completed, failed]
                  progress_percent:
                    type: integer
                  result:
                    $ref: '#/components/schemas/ComparisonResult'

  /contracts/compare/{job_id}/report:
    get:
      summary: 下載比對報告
      parameters:
        - name: job_id
          in: path
          required: true
          schema:
            type: string
        - name: format
          in: query
          schema:
            type: string
            enum: [markdown, pdf, html]
            default: markdown
      responses:
        '200':
          description: 報告內容
          content:
            text/markdown:
              schema:
                type: string
            application/pdf:
              schema:
                type: string
                format: binary

components:
  schemas:
    ComparisonResult:
      type: object
      properties:
        summary:
          type: object
          properties:
            total_changes:
              type: integer
            additions:
              type: integer
            deletions:
              type: integer
            modifications:
              type: integer
            overall_risk_level:
              type: string
            overall_risk_score:
              type: number
        
        critical_risks:
          type: array
          items:
            $ref: '#/components/schemas/RiskFinding'
        
        high_risks:
          type: array
          items:
            $ref: '#/components/schemas/RiskFinding'
        
        fraud_alerts:
          type: array
          items:
            type: object
            properties:
              type:
                type: string
              page:
                type: integer
              description:
                type: string
              evidence:
                type: string
        
        report_url:
          type: string
          format: uri
    
    RiskFinding:
      type: object
      properties:
        clause_number:
          type: string
        change_type:
          type: string
          enum: [modified, added, deleted]
        risk_level:
          type: string
          enum: [critical, high, medium, low]
        risk_score:
          type: number
        summary:
          type: string
        why_risky:
          type: string
        what_changed:
          type: string
        impact:
          type: string
        recommendation:
          type: string
        old_text:
          type: string
        new_text:
          type: string
```

### 5.2 使用範例

```python
import requests

# 1. 上傳兩份合約
with open('contract_v1.pdf', 'rb') as f:
    resp1 = requests.post(
        'https://api.blue-ai.com/v1/contracts/upload',
        files={'file': f},
        data={'file_type': 'old'}
    )
    old_doc_id = resp1.json()['document_id']

with open('contract_v2.pdf', 'rb') as f:
    resp2 = requests.post(
        'https://api.blue-ai.com/v1/contracts/upload',
        files={'file': f},
        data={'file_type': 'new'}
    )
    new_doc_id = resp2.json()['document_id']

# 2. 發起比對
resp3 = requests.post(
    'https://api.blue-ai.com/v1/contracts/compare',
    json={
        'old_document_id': old_doc_id,
        'new_document_id': new_doc_id,
        'options': {
            'contract_type': 'SLA',
            'enable_fraud_detection': True,
            'enable_benchmark': True,
            'risk_threshold': 'medium'
        }
    }
)
job_id = resp3.json()['job_id']

# 3. 輪詢狀態
import time
while True:
    resp4 = requests.get(f'https://api.blue-ai.com/v1/contracts/compare/{job_id}')
    status = resp4.json()['status']
    
    if status == 'completed':
        result = resp4.json()['result']
        print(f"Overall Risk: {result['summary']['overall_risk_level']}")
        print(f"Critical Risks: {len(result['critical_risks'])}")
        break
    elif status == 'failed':
        print("Job failed!")
        break
    
    time.sleep(5)

# 4. 下載報告
resp5 = requests.get(
    f'https://api.blue-ai.com/v1/contracts/compare/{job_id}/report',
    params={'format': 'pdf'}
)
with open('comparison_report.pdf', 'wb') as f:
    f.write(resp5.content)
```

---

## 6. 效能指標

### 6.1 效能目標

| 指標 | 目標 | 測量方法 |
|------|------|----------|
| **處理速度** | | |
| - 10 頁合約 | < 15 秒 | end-to-end |
| - 100 頁合約 | < 2 分鐘 | end-to-end |
| - 文件指紋產生 | < 0.1 秒/頁 | Step 2 |
| - LCS 對齊 | < 5 ms (100 頁) | Step 3 |
| - 七階段匹配 | < 50 ms (100 頁) | Step 3 |
| - DP 對齊 | < 100 ms (100 頁) | Step 3 |
| - NER 提取 | < 0.5 秒/頁 | Step 4 |
| - Claude API 分析 | < 3 秒/條款 | Step 4 |
| **準確率** | | |
| - 頁面/條款匹配 | > 98% | F1 score |
| - 條款識別 | > 95% | Precision/Recall |
| - 風險評估 | > 94% | vs 人類專家 |
| - NER (法律實體) | > 90% | F1 score |
| - 詐欺檢測 | > 90% | True Positive Rate |
| **系統效能** | | |
| - API 回應時間 (p95) | < 200 ms | 不含處理 |
| - 系統可用性 | > 99.5% | uptime |
| - 並發處理 | > 50 jobs | 同時 |
| **成本** | | |
| - Claude API 成本 | < $0.50/比對 | token 用量 |
| - 總處理成本 | < $1.00/比對 | 包含運算 |

### 6.2 效能優化策略

```python
# 1. 並行處理
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def process_comparison_parallel(old_doc, new_doc):
    """
    並行執行獨立任務
    """
    with ThreadPoolExecutor(max_workers=4) as executor:
        # 並行執行詐欺檢測和文件處理
        fraud_future = executor.submit(fraud_detection_service.detect, old_doc.path)
        process_old_future = executor.submit(document_processor.process, old_doc.path)
        process_new_future = executor.submit(document_processor.process, new_doc.path)
        
        # 等待文件處理完成
        old_processed = process_old_future.result()
        new_processed = process_new_future.result()
        
        # 比對引擎
        comparison_future = executor.submit(
            comparison_engine.compare, 
            old_processed, 
            new_processed
        )
        
        # 等待所有任務完成
        fraud_report = fraud_future.result()
        comparison_result = comparison_future.result()
    
    return comparison_result, fraud_report

# 2. 快取機制
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_document_fingerprint(func):
    """
    快取文件指紋
    """
    @wraps(func)
    def wrapper(document_id, *args, **kwargs):
        cache_key = f"fingerprint:{document_id}"
        cached = redis_client.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        result = func(document_id, *args, **kwargs)
        redis_client.setex(cache_key, 3600, json.dumps(result))  # 1 hour TTL
        return result
    
    return wrapper

# 3. Claude API 批次處理
def batch_claude_analysis(clauses: List[Tuple[str, str]]) -> List[RiskAnalysis]:
    """
    批次處理多個條款，減少 API 呼叫次數
    """
    # 構建批次 prompt
    batch_prompt = "分析以下 {} 個條款變更：\n\n".format(len(clauses))
    
    for i, (old, new) in enumerate(clauses):
        batch_prompt += f"## 條款 {i+1}\n"
        batch_prompt += f"舊: {old}\n新: {new}\n\n"
    
    batch_prompt += "以 JSON 陣列格式回覆所有分析結果。"
    
    # 單次 API 呼叫
    response = claude_client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=8000,
        messages=[{"role": "user", "content": batch_prompt}]
    )
    
    results = json.loads(response.content[0].text)
    return [RiskAnalysis(**r) for r in results]

# 4. Prompt Caching
def analyze_with_prompt_caching(clause_changes: List[ClauseChange]):
    """
    使用 Claude API Prompt Caching
    """
    # System prompt 會被快取
    system_prompt = """你是專業的合約分析助理..."""  # 長系統 prompt
    
    # 使用 cache_control
    response = claude_client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=2000,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"}  # 快取 system prompt
            }
        ],
        messages=[{
            "role": "user",
            "content": f"分析以下條款變更: {clause_changes}"
        }]
    )
    
    return response
```

---

## 7. 實作計劃

### 7.1 開發階段

#### Phase 1: 基礎建置（2週）

**Week 1: 基礎設施 + 文件處理**
- [ ] 建立專案結構與開發環境
- [ ] 設定 Docker + Docker Compose
- [ ] PostgreSQL + Redis 配置
- [ ] Blob Storage 整合（Azure Blob / AWS S3）
- [ ] Document Processor Service
  - [ ] PDF 文字提取 (PyMuPDF)
  - [ ] DOCX 文字提取 (python-docx)
  - [ ] OCR 整合 (Tesseract)
  - [ ] 表格提取 (pdfplumber)
- [ ] 單元測試（覆蓋率 >80%）

**Week 2: 比對引擎核心**
- [ ] 文件指紋模組
  - [ ] 內容哈希
  - [ ] 條款編號提取（中英文）
  - [ ] 章節標題提取
  - [ ] 感知哈希
- [ ] LCS 結構對齊
- [ ] 七階段共識匹配（Phase 1-5）
- [ ] 文字相似度計算
- [ ] 整合測試

#### Phase 2: 進階比對 + AI 分析（3週）

**Week 3: 完整比對管線**
- [ ] 七階段匹配（Phase 6-7.5）
  - [ ] 位置插值
  - [ ] 視覺重匹配
- [ ] 動態規劃最優對齊
- [ ] 多層差異引擎
  - [ ] 文字 diff
  - [ ] 表格 diff
  - [ ] 視覺 diff

**Week 4: NER & 條款提取**
- [ ] Legal-BERT NER 整合
  - [ ] 模型載入與推理
  - [ ] 繁體中文 rule-based 補充
- [ ] 關係提取（基礎版）
- [ ] QA-based 條款提取
  - [ ] 預定義問題模板
  - [ ] 答案提取與驗證
- [ ] 實體與條款資料庫設計

**Week 5: Claude API 風險分析**
- [ ] Claude API 整合
  - [ ] Prompt 設計與測試
  - [ ] Prompt Caching 優化
- [ ] 風險評分邏輯
- [ ] 可解釋性報告生成
- [ ] 批次分析優化
- [ ] 成本監控與限制

#### Phase 3: 詐欺檢測（2週）

**Week 6: 基礎詐欺檢測**
- [ ] PDF 版本分析
  - [ ] 版本歷史提取
  - [ ] 時間戳驗證
- [ ] 隱藏文字檢測
  - [ ] 白底白字
  - [ ] 透明文字
  - [ ] 邊界外文字
- [ ] 中繼資料檢查

**Week 7: 進階影像鑑識**
- [ ] LBP 紋理分析
- [ ] Gabor 濾波器
- [ ] 克隆區域檢測
- [ ] 視覺化結果產生
- [ ] 整合測試

#### Phase 4: API & 報告（2週）

**Week 8: RESTful API**
- [ ] FastAPI 應用建立
- [ ] API 端點實作
  - [ ] /upload
  - [ ] /compare
  - [ ] /compare/{job_id}
  - [ ] /report
- [ ] 認證與授權（JWT）
- [ ] Rate Limiting
- [ ] API 文件（OpenAPI/Swagger）

**Week 9: 報告生成 & 前端整合**
- [ ] Markdown 報告模板
- [ ] PDF 生成（WeasyPrint）
- [ ] HTML 報告
- [ ] 前端 UI（React）
  - [ ] 上傳介面
  - [ ] 狀態追蹤
  - [ ] 報告檢視
- [ ] E2E 測試

#### Phase 5: 優化 & 部署（2週）

**Week 10: 效能優化**
- [ ] 並行處理優化
- [ ] 快取策略實作
- [ ] 資料庫查詢優化
- [ ] Claude API 成本優化
- [ ] 效能測試與調優

**Week 11: 部署 & 監控**
- [ ] Docker 映像建立
- [ ] Kubernetes 配置
- [ ] CI/CD Pipeline（GitHub Actions）
- [ ] 監控設定（Prometheus + Grafana）
- [ ] 日誌管理（ELK Stack）
- [ ] 告警規則
- [ ] 上線前檢查清單

### 7.2 資源需求

**團隊組成** (11 週):
- 後端工程師 × 2
- ML 工程師 × 1
- 前端工程師 × 1
- DevOps 工程師 × 0.5
- QA 工程師 × 1

**技術資源**:
- Claude API Credits: $500 (開發+測試)
- Azure/AWS Credits: $300/月
- GPU (可選，本地 Legal-BERT): V100 或 A100

---

**文件版本**: 1.0  
**最後更新**: 2026-05-28  
**維護者**: Blue-AI Development Team
