"""Diff engine: converts alignment MatchBlocks into structured DiffItems."""

from typing import List
from .schemas import DiffItem, MatchBlock
from .parser import ClauseElement


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
                clause_id = old.clause_number or new.clause_number or "?"
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

        return diffs
