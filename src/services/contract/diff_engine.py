"""Diff engine: converts alignment MatchBlocks into structured DiffItems."""

import difflib
from typing import List
from .schemas import DiffItem, MatchBlock
from .parser import ClauseElement

_SIMILARITY_THRESHOLD = 0.75


def _text_similarity(a: str, b: str) -> float:
    """Character-level similarity using difflib SequenceMatcher."""
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


class DiffEngine:
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
                if old.clause_number:
                    diffs.append(DiffItem(
                        clause_id=old.clause_number,
                        change_type="deleted",
                        old_text=old.content.strip(),
                        new_text="",
                        confidence=block.confidence,
                        match_method=block.method,
                    ))
            elif old is None and new is not None:
                if new.clause_number:
                    diffs.append(DiffItem(
                        clause_id=new.clause_number,
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
