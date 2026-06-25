"""Contract parser: extracts structured clauses from MD, DOCX, and PDF files."""

import hashlib
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ClauseElement:
    clause_number: Optional[str]
    title: str
    content: str
    page_number: int
    content_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContractDocument:
    filename: str
    file_type: str
    raw_text: str
    clauses: List[ClauseElement]
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContractParser:
    # Matches: 第5條、第5.2條、5.、5.2、一、二、三、Article 3、Section 3.1
    CLAUSE_PATTERNS = [
        r'^第\s*(\d+(?:\.\d+)*)\s*條',
        r'^([一二三四五六七八九十百]+)[、．]',  # 一、二、三、（中文數字條款）
        r'^(\d+(?:\.\d+)+)\s*[、\s]',          # 5.2、或 5.2 開頭
        r'^(\d+)\.\s+\S',                       # 5. 開頭（整條）
        r'^Article\s+(\d+(?:\.\d+)*)',
        r'^Section\s+(\d+(?:\.\d+)*)',
    ]

    def parse_file(self, file_path: str) -> ContractDocument:
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".md":
            return self._parse_md(file_path)
        elif suffix == ".pdf":
            return self._parse_pdf(file_path)
        elif suffix == ".docx":
            return self._parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported format: {suffix}")

    # ------------------------------------------------------------------
    # MD parser (primary for demo)
    # ------------------------------------------------------------------

    def _parse_md(self, file_path: str) -> ContractDocument:
        text = Path(file_path).read_text(encoding="utf-8")
        clauses = self._split_md_clauses(text)
        return ContractDocument(
            filename=Path(file_path).name,
            file_type="md",
            raw_text=text,
            clauses=clauses,
            metadata={"clause_count": len(clauses)},
        )

    def _split_md_clauses(self, text: str) -> List[ClauseElement]:
        """Split MD into clauses by ## headings then by numbered sub-items."""
        clauses: List[ClauseElement] = []
        # Split on ## section headings
        sections = re.split(r'\n(?=## )', text)

        for section in sections:
            lines = section.strip().splitlines()
            if not lines:
                continue

            # Section heading becomes a parent clause
            heading = lines[0].lstrip("#").strip()
            section_number = self._extract_clause_number(heading)
            section_body = "\n".join(lines[1:]).strip()

            # Try to split body into sub-clauses by numbered lines (e.g. "4.1 ...")
            sub_clauses = self._split_numbered_items(section_body, parent_title=heading)

            if sub_clauses:
                # Add section header as its own entry (no content, just structure)
                clauses.append(ClauseElement(
                    clause_number=section_number,
                    title=heading,
                    content=heading,
                    page_number=1,
                    content_hash=self._md5(heading),
                ))
                clauses.extend(sub_clauses)
            else:
                clauses.append(ClauseElement(
                    clause_number=section_number,
                    title=heading,
                    content=section.strip(),
                    page_number=1,
                    content_hash=self._md5(section.strip()),
                ))

        return clauses

    def _split_numbered_items(self, text: str, parent_title: str) -> List[ClauseElement]:
        """Split text block into sub-clauses by lines starting with N.N pattern."""
        pattern = re.compile(r'^(\d+\.\d+)\s+(.+)', re.MULTILINE)
        matches = list(pattern.finditer(text))
        if not matches:
            return []

        items: List[ClauseElement] = []
        for i, m in enumerate(matches):
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            block = text[start:end].strip()
            number = m.group(1)
            title_text = m.group(2).strip()[:60]
            items.append(ClauseElement(
                clause_number=number,
                title=f"{number} {title_text}",
                content=block,
                page_number=1,
                content_hash=self._md5(block),
            ))
        return items

    # ------------------------------------------------------------------
    # PDF parser
    # ------------------------------------------------------------------

    def _parse_pdf(self, file_path: str) -> ContractDocument:
        try:
            import pdfplumber
        except ImportError:
            raise ImportError("pdfplumber not installed: pip install pdfplumber")

        chunks: List[str] = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                chunks.append(page.extract_text() or "")

        raw = "\n".join(chunks)
        clauses = self.split_into_clauses(raw)
        return ContractDocument(
            filename=Path(file_path).name,
            file_type="pdf",
            raw_text=raw,
            clauses=clauses,
            metadata={"page_count": len(chunks)},
        )

    # ------------------------------------------------------------------
    # DOCX parser
    # ------------------------------------------------------------------

    def _parse_docx(self, file_path: str) -> ContractDocument:
        try:
            import docx
        except ImportError:
            raise ImportError("python-docx not installed: pip install python-docx")

        doc = docx.Document(file_path)
        raw = "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
        clauses = self.split_into_clauses(raw)
        return ContractDocument(
            filename=Path(file_path).name,
            file_type="docx",
            raw_text=raw,
            clauses=clauses,
            metadata={},
        )

    # ------------------------------------------------------------------
    # Shared utilities
    # ------------------------------------------------------------------

    def split_into_clauses(self, text: str, page_number: int = 1) -> List[ClauseElement]:
        """Generic clause splitter for plain text (PDF/DOCX fallback)."""
        clauses: List[ClauseElement] = []
        for para in text.split("\n\n"):
            para = para.strip()
            if not para:
                continue
            clauses.append(ClauseElement(
                clause_number=self._extract_clause_number(para),
                title=self._extract_title(para),
                content=para,
                page_number=page_number,
                content_hash=self._md5(para),
            ))
        return clauses

    def _extract_clause_number(self, text: str) -> Optional[str]:
        first_line = text.strip().splitlines()[0] if text.strip() else ""
        for pattern in self.CLAUSE_PATTERNS:
            m = re.match(pattern, first_line.strip())
            if m:
                return m.group(1)
        return None

    def _extract_title(self, text: str) -> str:
        lines = text.strip().splitlines()
        first = lines[0].strip() if lines else ""
        return first[:60] if len(first) > 5 else "未命名條款"

    @staticmethod
    def _md5(text: str) -> str:
        normalized = re.sub(r"\s+", "", text).lower()
        return hashlib.md5(normalized.encode("utf-8")).hexdigest()
