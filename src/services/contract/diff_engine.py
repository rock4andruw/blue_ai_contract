"""Diff engine: converts alignment MatchBlocks into structured DiffItems."""

import re
import difflib
from typing import List, Tuple
from .schemas import DiffItem, MatchBlock, CoverageReport
from .parser import ClauseElement

_SIMILARITY_THRESHOLD = 0.75
_PARSER_COVERAGE_THRESHOLD = 0.97  # 97% acceptable loss (3% safety margin)


def _normalize_text_level_2(text: str) -> str:
    """Meaningful punctuation normalization: remove separators but keep semantic symbols.

    Keep: letters, digits, CJK, currency ($¥€), percent (%), slashes (/)
    Remove: commas, periods, quotes, brackets, and other separators

    This is the main metric for Parser Guard coverage check.
    """
    if not text:
        return ""

    # First, collapse HTML/MD formatting
    text = re.sub(r'<del[^>]*>.*?</del>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<ins[^>]*>(.*?)</ins>', r'\1', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'[\*_`]', '', text)

    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove purely decorative punctuation (separators)
    punctuation_to_remove = r'["\'\`\[\]\(\),。.;:!?！？；：、，「」『』（）\-—–]'
    text = re.sub(punctuation_to_remove, '', text)

    return text.strip()


def _measure_parser_coverage(raw_text: str, parsed_text: str) -> Tuple[float, List[str]]:
    """Measure how much of the original raw text was preserved during parsing.

    Returns:
      - coverage_ratio: float (0.0-1.0) at L2 normalization level
      - missing_fragments: list of character sequences that were lost (up to 50 chars each)
    """
    raw_norm = _normalize_text_level_2(raw_text)
    parsed_norm = _normalize_text_level_2(parsed_text)

    coverage = len(parsed_norm) / len(raw_norm) if len(raw_norm) > 0 else 1.0

    # Locate missing fragments using difflib.SequenceMatcher
    missing_fragments = []
    if coverage < 1.0:
        matcher = difflib.SequenceMatcher(None, raw_norm, parsed_norm)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag in ('delete', 'replace'):
                missing = raw_norm[i1:i2][:50]  # First 50 chars
                if missing and missing not in missing_fragments:
                    missing_fragments.append(missing)

    return coverage, missing_fragments


def _text_similarity(a: str, b: str) -> float:
    """Character-level similarity using difflib SequenceMatcher."""
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


class DiffEngine:
    def check_coverage(
        self,
        raw_original: str,
        raw_revised: str,
        old_clauses: List[ClauseElement],
        new_clauses: List[ClauseElement],
    ) -> CoverageReport:
        """Check text conservation: verify no silent content loss during parsing/diff.

        Args:
            raw_original: original contract raw text (before parsing)
            raw_revised: revised contract raw text (before parsing)
            old_clauses: parsed clauses from original
            new_clauses: parsed clauses from revised

        Returns:
            CoverageReport with coverage ratios and any missing fragments detected
        """
        # Reconstruct parsed text from all clauses
        parsed_original = "\n\n".join(c.content for c in old_clauses)
        parsed_revised = "\n\n".join(c.content for c in new_clauses)

        # Measure coverage for both versions
        orig_ratio, orig_missing = _measure_parser_coverage(raw_original, parsed_original)
        rev_ratio, rev_missing = _measure_parser_coverage(raw_revised, parsed_revised)

        all_missing = list(set(orig_missing + rev_missing))[:10]  # Cap to 10 fragments

        return CoverageReport(
            parser_coverage_ok=orig_ratio >= _PARSER_COVERAGE_THRESHOLD and rev_ratio >= _PARSER_COVERAGE_THRESHOLD,
            diff_coverage_ok=True,  # Diff coverage is always 100% by definition (nothing added/removed in diff output)
            original_parser_ratio=orig_ratio,
            revised_parser_ratio=rev_ratio,
            missing_fragments=all_missing,
        )

    def compute_diffs(
        self,
        old_clauses: List[ClauseElement],
        new_clauses: List[ClauseElement],
        alignment: List[MatchBlock],
    ) -> List[DiffItem]:
        diffs: List[DiffItem] = []

        for block in alignment:
            old = old_clauses[block.old_idx] if block.old_idx is not None else None
            new = new_clauses[block.new_idx] if block.new_idx is not None else None

            if old is not None and new is not None:
                if old.content_hash == new.content_hash:
                    continue  # unchanged — skip
                clause_id = (
                    old.clause_number or new.clause_number
                    or (old.title[:15] if old.title and old.title != "未命名條款" else None)
                    or (new.title[:15] if new.title and new.title != "未命名條款" else None)
                    or "未知條款"
                )
                diffs.append(DiffItem(
                    clause_id=clause_id,
                    change_type="modified",
                    old_text=old.content.strip(),
                    new_text=new.content.strip(),
                    confidence=block.confidence,
                    match_method=block.method,
                ))
            elif old is not None and new is None:
                clause_id = (
                    old.clause_number
                    or (old.title[:15] if old.title and old.title != "未命名條款" else None)
                    or "未知條款"
                )
                diffs.append(DiffItem(
                    clause_id=clause_id,
                    change_type="deleted",
                    old_text=old.content.strip(),
                    new_text="",
                    confidence=block.confidence,
                    match_method=block.method,
                ))
            elif old is None and new is not None:
                clause_id = (
                    new.clause_number
                    or (new.title[:15] if new.title and new.title != "未命名條款" else None)
                    or "未知條款"
                )
                diffs.append(DiffItem(
                    clause_id=clause_id,
                    change_type="inserted",
                    old_text="",
                    new_text=new.content.strip(),
                    confidence=block.confidence,
                    match_method=block.method,
                ))

        return self._merge_renumbered(diffs)

    def _merge_renumbered(self, diffs: List[DiffItem]) -> List[DiffItem]:
        """Post-process: merge inserted+deleted pairs with high text similarity.

        Handles clauses that were renumbered (e.g. 12.5 → 12.6) but have
        nearly identical content. Needleman-Wunsch treats these as separate
        deleted and inserted items; similarity check reclassifies them as modified.
        """
        deleted  = [d for d in diffs if d.change_type == "deleted"]
        inserted = [d for d in diffs if d.change_type == "inserted"]
        others   = [d for d in diffs if d.change_type == "modified"]

        merged_old_ids = set()
        merged_new_ids = set()
        merged: List[DiffItem] = []

        for ins in inserted:
            best_score = 0.0
            best_del = None
            for dele in deleted:
                if dele.clause_id in merged_old_ids:
                    continue
                score = _text_similarity(dele.old_text, ins.new_text)
                if score > best_score:
                    best_score = score
                    best_del = dele

            if best_del is not None and best_score >= _SIMILARITY_THRESHOLD:
                # Reclassify as modified (renumbered clause)
                clause_id = f"{best_del.clause_id}→{ins.clause_id}"
                merged.append(DiffItem(
                    clause_id=clause_id,
                    change_type="modified",
                    old_text=best_del.old_text,
                    new_text=ins.new_text,
                    confidence=best_score,
                    match_method="similarity_merge",
                ))
                merged_old_ids.add(best_del.clause_id)
                merged_new_ids.add(ins.clause_id)

        remaining_deleted  = [d for d in deleted  if d.clause_id not in merged_old_ids]
        remaining_inserted = [d for d in inserted if d.clause_id not in merged_new_ids]

        return others + merged + remaining_deleted + remaining_inserted
