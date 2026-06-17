"""Contract structural alignment and comparison engine.

Implements a hybrid multi-phase alignment pipeline combining Longest Common Subsequence (LCS),
Consensus Matching, and Dynamic Programming (Needleman-Wunsch) alignment.
Based on specifications from: arXiv 2604.19770 (Hybrid Multi-Phase Page Matching).
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher

# Import ClauseElement from parser
from src.services.contract.parser import ClauseElement

@dataclass
class MatchBlock:
    """Represents a matched pair of clauses between old and new documents."""
    old_idx: Optional[int]
    new_idx: Optional[int]
    confidence: float
    method: str  # e.g., 'exact_hash', 'clause_number', 'dp_alignment', 'inserted', 'deleted'

class ContractAligner:
    """Engine for finding optimal alignment between versions of a contract."""

    def __init__(self, gap_penalty: float = -0.42, similarity_threshold: float = 0.28):
        self.gap_penalty = gap_penalty
        self.similarity_threshold = similarity_threshold

    def align_documents(self, old_clauses: List[ClauseElement], new_clauses: List[ClauseElement]) -> List[MatchBlock]:
        """Aligns old and new clauses using a multi-phase matching pipeline.

        Args:
            old_clauses: Clauses from the previous document version.
            new_clauses: Clauses from the new document version.

        Returns:
            List[MatchBlock]: The optimal alignment map.
        """
        if not old_clauses and not new_clauses:
            return []
        
        # Phase 1-3: Structural Alignment using SequenceMatcher (LCS Variant)
        old_hashes = [c.content_hash for c in old_clauses]
        new_hashes = [c.content_hash for c in new_clauses]
        
        matcher = SequenceMatcher(None, old_hashes, new_hashes)
        opcodes = matcher.get_opcodes()
        
        aligned_blocks: List[MatchBlock] = []
        
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                # Direct match via exact content hash
                for k in range(i2 - i1):
                    aligned_blocks.append(MatchBlock(
                        old_idx=i1 + k,
                        new_idx=j1 + k,
                        confidence=1.0,
                        method='lcs_equal'
                    ))
            elif tag == 'replace':
                # Fallback to Seven-Phase Consensus and Dynamic Programming
                sub_old = old_clauses[i1:i2]
                sub_new = new_clauses[j1:j2]
                sub_alignment = self._consensus_and_dp_align(
                    sub_old, sub_new, offset_old=i1, offset_new=j1
                )
                aligned_blocks.extend(sub_alignment)
            elif tag == 'delete':
                # Deleted clauses
                for k in range(i2 - i1):
                    aligned_blocks.append(MatchBlock(
                        old_idx=i1 + k,
                        new_idx=None,
                        confidence=1.0,
                        method='lcs_deleted'
                    ))
            elif tag == 'insert':
                # Inserted clauses
                for k in range(j2 - j1):
                    aligned_blocks.append(MatchBlock(
                        old_idx=None,
                        new_idx=j1 + k,
                        confidence=1.0,
                        method='lcs_inserted'
                    ))
                    
        return aligned_blocks

    def _consensus_and_dp_align(
        self, 
        old_list: List[ClauseElement], 
        new_list: List[ClauseElement],
        offset_old: int,
        offset_new: int
    ) -> List[MatchBlock]:
        """Runs fine-grained consensus alignment and DP on non-exact matches."""
        matches: List[MatchBlock] = []
        matched_old = set()
        matched_new = set()
        
        # 1. Consensus Stage: Clause number matching
        for i, old_clause in enumerate(old_list):
            if old_clause.clause_number is None:
                continue
            for j, new_clause in enumerate(new_list):
                if j in matched_new:
                    continue
                if old_clause.clause_number == new_clause.clause_number:
                    matches.append(MatchBlock(
                        old_idx=offset_old + i,
                        new_idx=offset_new + j,
                        confidence=0.90,
                        method='clause_number_match'
                    ))
                    matched_old.add(i)
                    matched_new.add(j)
                    break

        # 2. Consensus Stage: Title matching
        for i, old_clause in enumerate(old_list):
            if i in matched_old or old_clause.title == "未命名條款":
                continue
            for j, new_clause in enumerate(new_list):
                if j in matched_new or new_clause.title == "未命名條款":
                    continue
                if old_clause.title == new_clause.title:
                    matches.append(MatchBlock(
                        old_idx=offset_old + i,
                        new_idx=offset_new + j,
                        confidence=0.80,
                        method='title_match'
                    ))
                    matched_old.add(i)
                    matched_new.add(j)
                    break

        # Extract remaining unmatched elements for global alignment (Needleman-Wunsch)
        rem_old = [c for i, c in enumerate(old_list) if i not in matched_old]
        rem_new = [c for j, c in enumerate(new_list) if j not in matched_new]
        
        if rem_old or rem_new:
            dp_matches = self._needleman_wunsch_align(rem_old, rem_new, old_list, new_list, offset_old, offset_new)
            matches.extend(dp_matches)
            
        return matches

    def _needleman_wunsch_align(
        self,
        rem_old: List[ClauseElement],
        rem_new: List[ClauseElement],
        full_old: List[ClauseElement],
        full_new: List[ClauseElement],
        offset_old: int,
        offset_new: int
    ) -> List[MatchBlock]:
        """Needleman-Wunsch dynamic programming alignment for robust fallback matching."""
        m, n = len(rem_old), len(rem_new)
        if m == 0:
            return [MatchBlock(None, offset_new + full_new.index(c), 1.0, 'inserted') for c in rem_new]
        if n == 0:
            return [MatchBlock(offset_old + full_old.index(c), None, 1.0, 'deleted') for c in rem_old]

        # Initialize DP matrix
        dp = [[0.0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            dp[i][0] = i * self.gap_penalty
        for j in range(1, n + 1):
            dp[0][j] = j * self.gap_penalty
            
        # Fill DP matrix
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                old_clause = rem_old[i - 1]
                new_clause = rem_new[j - 1]
                
                # Compute composite score
                score = self.compute_similarity(old_clause.content, new_clause.content)
                
                dp[i][j] = max(
                    dp[i - 1][j - 1] + score,     # Match
                    dp[i - 1][j] + self.gap_penalty,  # Delete
                    dp[i][j - 1] + self.gap_penalty   # Insert
                )
                
        # Backtrack to find optimal path
        matches: List[MatchBlock] = []
        i, j = m, n
        while i > 0 or j > 0:
            if i > 0 and j > 0:
                old_clause = rem_old[i - 1]
                new_clause = rem_new[j - 1]
                score = self.compute_similarity(old_clause.content, new_clause.content)
                
                if dp[i][j] == dp[i - 1][j - 1] + score:
                    # Match found
                    old_idx = offset_old + full_old.index(old_clause)
                    new_idx = offset_new + full_new.index(new_clause)
                    
                    if score >= self.similarity_threshold:
                        matches.append(MatchBlock(old_idx, new_idx, score, 'dp_similar'))
                    else:
                        # Too different, treat as delete + insert
                        matches.append(MatchBlock(old_idx, None, 1.0, 'dp_deleted'))
                        matches.append(MatchBlock(None, new_idx, 1.0, 'dp_inserted'))
                    i -= 1
                    j -= 1
                    continue
            
            if i > 0 and (j == 0 or dp[i][j] == dp[i - 1][j] + self.gap_penalty):
                old_idx = offset_old + full_old.index(rem_old[i - 1])
                matches.append(MatchBlock(old_idx, None, 1.0, 'dp_deleted'))
                i -= 1
            else:
                new_idx = offset_new + full_new.index(rem_new[j - 1])
                matches.append(MatchBlock(None, new_idx, 1.0, 'dp_inserted'))
                j -= 1
                
        matches.reverse()
        return matches

    @staticmethod
    def compute_similarity(text1: str, text2: str) -> float:
        """Calculates text similarity ratio using difflib.

        Args:
            text1: First body text.
            text2: Second body text.

        Returns:
            float: Similarity ratio between 0.0 and 1.0.
        """
        if not text1 or not text2:
            return 0.0
        matcher = SequenceMatcher(None, text1, text2)
        return matcher.ratio()
